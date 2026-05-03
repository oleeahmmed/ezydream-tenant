"""
SAP B1–style stock application: OINM (ledger row) stays the source of truth for a
movement; OITW (per warehouse) and OITM (company-wide totals) are updated in the same
DB transaction.

Sales / purchase / production APIs should eventually call these helpers instead of
writing OINM or OITW directly.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.inventory.models import OINM, OITM, OITW
from apps.warehouse.models import OWHS


def _oitm_onhand_total(item_code: str) -> Decimal:
    agg = OITW.objects.filter(ItemCode=item_code, Canceled="N").aggregate(
        s=Coalesce(Sum("OnHand"), Decimal("0"))
    )
    return Decimal(str(agg["s"] or "0"))


def _apply_net_to_oitw(item_code: str, whs_code: str, net_qty: Decimal) -> None:
    """net_qty = InQty - OutQty (positive increases OnHand)."""
    oitw, _created = OITW.objects.select_for_update().get_or_create(
        ItemCode=item_code,
        WhsCode=whs_code,
        defaults={
            "OnHand": Decimal("0"),
            "IsCommited": Decimal("0"),
            "AvgPrice": Decimal("0"),
            "OrderQty": Decimal("0"),
            "MinStock": Decimal("0"),
            "MaxStock": Decimal("0"),
            "Locked": "N",
            "Canceled": "N",
        },
    )
    new_on = oitw.OnHand + net_qty
    if new_on < 0:
        raise ValidationError(
            f"Insufficient stock for {item_code} @ {whs_code}: OnHand would become {new_on}."
        )
    oitw.OnHand = new_on
    oitw.save(update_fields=["OnHand"])


def _sync_oitm_onhand(item_code: str) -> None:
    OITM.objects.filter(pk=item_code).update(OnHand=_oitm_onhand_total(item_code))


@transaction.atomic
def post_oinm_and_apply_stock(
    *,
    trans_type: int,
    item_code: str,
    warehouse: str,
    in_qty: Decimal,
    out_qty: Decimal,
    price: Decimal,
    base_ref: str,
    doc_time,
    doc_entry: int | None = None,
    doc_line_num: int | None = None,
    trans_value: Decimal | None = None,
    created_by: str = "",
) -> OINM:
    """
    Create one OINM row and move stock on OITW / OITM for inventory-tracked items.
    """
    item_code = item_code.strip()
    warehouse = warehouse.strip()
    if not item_code or not warehouse:
        raise ValidationError("ItemCode and Warehouse are required.")

    in_qty = Decimal(in_qty or 0)
    out_qty = Decimal(out_qty or 0)
    if in_qty < 0 or out_qty < 0:
        raise ValidationError("InQty and OutQty must be non-negative.")
    if in_qty > 0 and out_qty > 0:
        raise ValidationError("Use either InQty or OutQty on one row, not both.")

    oitm = OITM.objects.select_for_update().filter(pk=item_code).first()
    if oitm is None:
        raise ValidationError(f"Item {item_code!r} does not exist (OITM).")
    if not OWHS.objects.filter(WhsCode=warehouse, Inactive="N").exists():
        raise ValidationError(f"Warehouse {warehouse!r} is missing or inactive (OWHS).")

    net = in_qty - out_qty
    if oitm.InvntItem == "Y":
        _apply_net_to_oitw(item_code, warehouse, net)
        _sync_oitm_onhand(item_code)

    tv = trans_value if trans_value is not None else (in_qty - out_qty) * price
    oinm = OINM(
        TransType=int(trans_type),
        ItemCode=item_code,
        Warehouse=warehouse,
        InQty=in_qty,
        OutQty=out_qty,
        Price=price,
        BASE_REF=(base_ref or "").strip()[:30],
        DocEntry=doc_entry,
        DocLineNum=doc_line_num,
        TransValue=tv,
        CreatedBy=(created_by or "").strip()[:50],
        DocTime=doc_time if doc_time is not None else timezone.now(),
        Canceled="N",
    )
    oinm.save()
    return oinm


@transaction.atomic
def reverse_oinm_stock(oinm: OINM) -> None:
    """
    Undo the stock effect of an active (Canceled=N) OINM row. Caller sets Canceled=Y
    after this returns.
    """
    if oinm.Canceled != "N":
        return
    oitm = OITM.objects.select_for_update().filter(pk=oinm.ItemCode).first()
    if oitm is None:
        return
    net = oinm.InQty - oinm.OutQty
    if oitm.InvntItem == "Y" and net != 0:
        # Opposite movement
        _apply_net_to_oitw(oinm.ItemCode, oinm.Warehouse, -net)
        _sync_oitm_onhand(oinm.ItemCode)


@transaction.atomic
def reactivate_oinm_stock(oinm: OINM) -> None:
    """Re-apply stock for a previously canceled (Canceled=Y) ledger row (uncancel)."""
    if oinm.Canceled != "Y":
        return
    oitm = OITM.objects.select_for_update().filter(pk=oinm.ItemCode).first()
    if oitm is None:
        return
    net = oinm.InQty - oinm.OutQty
    if oitm.InvntItem == "Y" and net != 0:
        _apply_net_to_oitw(oinm.ItemCode, oinm.Warehouse, net)
        _sync_oitm_onhand(oinm.ItemCode)
