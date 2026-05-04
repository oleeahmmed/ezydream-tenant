"""
Create or replace automatic OJDT + JDT1 journal entries for key documents (SAP B1–style).

Each run deletes prior rows with ``Ref1 = AUTOJE:<KIND>:<DocEntry>`` then inserts a balanced
entry when the document is active and amounts allow.

Requires ``FINANCE_GL_*`` settings (see ``posting_defaults``). Optionally enforces ``OFPR``
(``fi_period.assert_open_fi_period`` when ``FINANCE_ENFORCE_OFPR`` is true and periods exist).
Does not update ``OACT.CurrTotal`` (ledger lines are the source of truth until a GL roll-up exists).
"""

from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum

from apps.core import b1_field_choices as jt
from apps.finance.models import JDT1, OACT, OJDT
from apps.finance.services import posting_defaults as pd
from apps.finance.services.fi_period import assert_open_fi_period

_AUTO_PREFIX = "AUTOJE:"


def _auto_ref1(kind: str, doc_entry: int) -> str:
    return f"{_AUTO_PREFIX}{kind}:{doc_entry}"


def clear_document_journal(kind: str, doc_entry: int) -> None:
    """Remove automatic journal rows for ``kind`` (OINV, OPCH, ORCT, OVPM) + ``doc_entry``."""
    ref1 = _auto_ref1(kind, int(doc_entry))
    for hdr in OJDT.objects.filter(Ref1=ref1).order_by("TransId"):
        JDT1.objects.filter(header=hdr).delete()
        hdr.delete()


def _delete_auto_journal_by_ref1(ref1: str) -> None:
    for hdr in OJDT.objects.filter(Ref1=ref1).order_by("TransId"):
        JDT1.objects.filter(header=hdr).delete()
        hdr.delete()


def _assert_balanced(debits: Decimal, credits: Decimal) -> None:
    if debits != credits:
        raise ValidationError(f"Journal not balanced: debit {debits} != credit {credits}.")


@transaction.atomic
def sync_ar_invoice_journal(doc_entry: int) -> None:
    from apps.sales.models import OINV

    ref1 = _auto_ref1("OINV", doc_entry)
    _delete_auto_journal_by_ref1(ref1)
    inv = OINV.objects.filter(pk=doc_entry).first()
    if inv is None or inv.Canceled == "Y":
        return
    total = Decimal(str(inv.DocTotal or "0"))
    vat = Decimal(str(inv.VatSum or "0"))
    if total <= 0:
        return
    net = total - vat
    if net < 0:
        vat = total
        net = Decimal("0")
    vat_acct = pd.gl_output_vat()
    if vat > 0 and not vat_acct:
        raise ValidationError(
            "OINV has VatSum > 0 but FINANCE_GL_OUTPUT_VAT is not set. Set it or clear VatSum."
        )

    assert_open_fi_period(inv.DocDate)
    ar = pd.gl_ar_receivable()
    rev = pd.gl_sales_revenue()

    hdr = OJDT.objects.create(
        BaseRef=f"OINV-{doc_entry}",
        RefDate=inv.DocDate,
        TransType=jt.JTRANS_AR_INVOICE,
        Memo=f"A/R Invoice {inv.DocNum or ''}".strip()[:200],
        Ref1=ref1,
        Ref2=(inv.CardCode or "")[:100],
    )
    dr = Decimal("0")
    cr = Decimal("0")
    JDT1.objects.create(
        header=hdr,
        Line_ID=1,
        Account=ar,
        ShortName=inv.CardCode or "",
        Debit=total,
        Credit=Decimal("0"),
        LineMemo=f"OINV DocEntry {doc_entry}",
    )
    dr += total
    JDT1.objects.create(
        header=hdr,
        Line_ID=2,
        Account=rev,
        ShortName=inv.CardCode or "",
        Debit=Decimal("0"),
        Credit=net,
        LineMemo="Revenue net",
    )
    cr += net
    if vat > 0 and vat_acct:
        JDT1.objects.create(
            header=hdr,
            Line_ID=3,
            Account=vat_acct,
            ShortName=inv.CardCode or "",
            Debit=Decimal("0"),
            Credit=vat,
            LineMemo="Output VAT",
        )
        cr += vat
    _assert_balanced(dr, cr)


@transaction.atomic
def sync_ap_invoice_journal(doc_entry: int) -> None:
    from apps.purchase.models import OPCH

    ref1 = _auto_ref1("OPCH", doc_entry)
    _delete_auto_journal_by_ref1(ref1)
    inv = OPCH.objects.filter(pk=doc_entry).first()
    if inv is None or inv.Canceled == "Y":
        return
    total = Decimal(str(inv.DocTotal or "0"))
    vat = Decimal(str(inv.VatSum or "0"))
    if total <= 0:
        return
    net = total - vat
    if net < 0:
        vat = total
        net = Decimal("0")
    vat_acct = pd.gl_input_vat()
    if vat > 0 and not vat_acct:
        raise ValidationError(
            "OPCH has VatSum > 0 but FINANCE_GL_INPUT_VAT is not set. Set it or clear VatSum."
        )
    assert_open_fi_period(inv.DocDate)
    ap = pd.gl_ap_payable()
    exp = pd.gl_purchase_expense()
    hdr = OJDT.objects.create(
        BaseRef=f"OPCH-{doc_entry}",
        RefDate=inv.DocDate,
        TransType=jt.JTRANS_AP_INVOICE,
        Memo=f"A/P Invoice {inv.DocNum or ''}".strip()[:200],
        Ref1=ref1,
        Ref2=(inv.CardCode or "")[:100],
    )
    dr = Decimal("0")
    cr = Decimal("0")
    line_id = 1
    JDT1.objects.create(
        header=hdr,
        Line_ID=line_id,
        Account=exp,
        ShortName=inv.CardCode or "",
        Debit=net,
        Credit=Decimal("0"),
        LineMemo="Purchases / expense net",
    )
    dr += net
    line_id += 1
    if vat > 0 and vat_acct:
        JDT1.objects.create(
            header=hdr,
            Line_ID=line_id,
            Account=vat_acct,
            ShortName=inv.CardCode or "",
            Debit=vat,
            Credit=Decimal("0"),
            LineMemo="Input VAT",
        )
        dr += vat
        line_id += 1
    JDT1.objects.create(
        header=hdr,
        Line_ID=line_id,
        Account=ap,
        ShortName=inv.CardCode or "",
        Debit=Decimal("0"),
        Credit=total,
        LineMemo="A/P",
    )
    cr += total
    _assert_balanced(dr, cr)


def _resolve_cash_account_for_orct(header) -> str:
    for cand in (header.CashAcct or "", header.CheckAcct or "", header.TrsfrAcct or ""):
        c = (cand or "").strip()
        if c and OACT.objects.filter(pk=c, Postable="Y", Frozen="N").exists():
            return c
    return pd.gl_cash_or_bank()


@transaction.atomic
def sync_incoming_payment_journal(doc_entry: int) -> None:
    from apps.finance.models import ORCT, RCT1

    ref1 = _auto_ref1("ORCT", doc_entry)
    _delete_auto_journal_by_ref1(ref1)
    p = ORCT.objects.filter(pk=doc_entry).first()
    if p is None:
        return
    line_agg = RCT1.objects.filter(header_id=doc_entry).aggregate(s=Sum("SumApplied"))
    raw = line_agg["s"]
    line_sum = Decimal(str(raw)) if raw is not None else Decimal("0")
    header_amt = Decimal(str(p.DocTotal or "0"))
    amt = line_sum if line_sum > 0 else header_amt
    if amt <= 0 or p.DocStatus != "O":
        return
    assert_open_fi_period(p.DocDate)
    ar = pd.gl_ar_receivable()
    cash = _resolve_cash_account_for_orct(p)
    hdr = OJDT.objects.create(
        BaseRef=f"ORCT-{doc_entry}",
        RefDate=p.DocDate,
        TransType=jt.JTRANS_INCOMING_PAYMENT,
        Memo=f"Incoming payment {doc_entry}",
        Ref1=ref1,
        Ref2=(p.CardCode or "")[:100],
    )
    JDT1.objects.create(
        header=hdr,
        Line_ID=1,
        Account=cash,
        ShortName=p.CardCode or "",
        Debit=amt,
        Credit=Decimal("0"),
        LineMemo="Cash / bank",
    )
    JDT1.objects.create(
        header=hdr,
        Line_ID=2,
        Account=ar,
        ShortName=p.CardCode or "",
        Debit=Decimal("0"),
        Credit=amt,
        LineMemo="A/R",
    )
    _assert_balanced(amt, amt)


def _resolve_bank_for_ovpm(header) -> str:
    b = (header.BankAcct or "").strip()
    if b and OACT.objects.filter(pk=b, Postable="Y", Frozen="N").exists():
        return b
    return pd.gl_cash_or_bank()


@transaction.atomic
def sync_outgoing_payment_journal(doc_entry: int) -> None:
    from apps.finance.models import OVPM, VPM1

    ref1 = _auto_ref1("OVPM", doc_entry)
    _delete_auto_journal_by_ref1(ref1)
    p = OVPM.objects.filter(pk=doc_entry).first()
    if p is None:
        return
    line_agg = VPM1.objects.filter(header_id=doc_entry).aggregate(s=Sum("SumApplied"))
    raw = line_agg["s"]
    line_sum = Decimal(str(raw)) if raw is not None else Decimal("0")
    header_amt = Decimal(str(p.DocTotal or "0"))
    amt = line_sum if line_sum > 0 else header_amt
    if amt <= 0 or p.DocStatus != "O":
        return
    assert_open_fi_period(p.DocDate)
    ap = pd.gl_ap_payable()
    bank = _resolve_bank_for_ovpm(p)
    hdr = OJDT.objects.create(
        BaseRef=f"OVPM-{doc_entry}",
        RefDate=p.DocDate,
        TransType=jt.JTRANS_OUTGOING_PAYMENT,
        Memo=f"Outgoing payment {doc_entry}",
        Ref1=ref1,
        Ref2=(p.CardCode or "")[:100],
    )
    JDT1.objects.create(
        header=hdr,
        Line_ID=1,
        Account=ap,
        ShortName=p.CardCode or "",
        Debit=amt,
        Credit=Decimal("0"),
        LineMemo="A/P",
    )
    JDT1.objects.create(
        header=hdr,
        Line_ID=2,
        Account=bank,
        ShortName=p.CardCode or "",
        Debit=Decimal("0"),
        Credit=amt,
        LineMemo="Bank / cash",
    )
    _assert_balanced(amt, amt)
