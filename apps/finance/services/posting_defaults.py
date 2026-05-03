"""
Default G/L accounts for automatic journal posting (SAP B1–style).

Set ``FINANCE_GL_*`` in Django settings to existing ``OACT.AcctCode`` values
(``Postable='Y'``). Empty strings skip that account (VAT lines omitted when unset).
"""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError

from apps.finance.models import OACT


def _opt(name: str) -> str:
    return (getattr(settings, name, None) or "").strip()


def _require_postable(acct: str, label: str) -> str:
    code = (acct or "").strip()
    if not code:
        raise ValidationError(
            f"Configure Django setting {label} to a postable G/L account code (OACT.AcctCode)."
        )
    row = OACT.objects.filter(pk=code, Postable="Y", Frozen="N").first()
    if row is None:
        raise ValidationError(f"{label}={code!r} is not a valid postable G/L account (OACT).")
    return code


def gl_ar_receivable() -> str:
    return _require_postable(_opt("FINANCE_GL_AR"), "FINANCE_GL_AR")


def gl_sales_revenue() -> str:
    return _require_postable(_opt("FINANCE_GL_SALES_REVENUE"), "FINANCE_GL_SALES_REVENUE")


def gl_output_vat() -> str | None:
    v = _opt("FINANCE_GL_OUTPUT_VAT")
    return _require_postable(v, "FINANCE_GL_OUTPUT_VAT") if v else None


def gl_ap_payable() -> str:
    return _require_postable(_opt("FINANCE_GL_AP"), "FINANCE_GL_AP")


def gl_purchase_expense() -> str:
    return _require_postable(_opt("FINANCE_GL_PURCHASE_EXPENSE"), "FINANCE_GL_PURCHASE_EXPENSE")


def gl_input_vat() -> str | None:
    v = _opt("FINANCE_GL_INPUT_VAT")
    return _require_postable(v, "FINANCE_GL_INPUT_VAT") if v else None


def gl_cash_or_bank() -> str:
    return _require_postable(_opt("FINANCE_GL_CASH"), "FINANCE_GL_CASH")
