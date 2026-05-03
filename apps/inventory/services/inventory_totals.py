"""
Recompute OITW / OITM derived quantities from open sales and purchase documents.

- IsCommited: open sales order lines (ORDR DocStatus=O, not canceled).
- OrderQty: open purchase order lines (OPOR DocStatus=O, not canceled), summed by OpenQty
  when > 0 else Quantity per line.
"""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce

from apps.inventory.models import OITM, OITW


def _por1_effective_on_order_qty(row: dict) -> Decimal:
    oq = row.get("OpenQty") or Decimal("0")
    q = row.get("Quantity") or Decimal("0")
    if oq > 0:
        return Decimal(str(oq))
    return Decimal(str(q))


@transaction.atomic
def rebuild_oitw_committed_and_on_order() -> None:
    from apps.purchase.models import POR1
    from apps.sales.models import ORDR, RDR1

    committed: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
    for row in (
        RDR1.objects.filter(Canceled="N", header__Canceled="N", header__DocStatus="O")
        .values("ItemCode", "WhsCode", "Quantity")
        .iterator()
    ):
        ic = (row["ItemCode"] or "").strip()
        wh = (row["WhsCode"] or "").strip()
        if ic and wh:
            committed[(ic, wh)] += Decimal(str(row["Quantity"] or "0"))

    on_order: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
    for row in (
        POR1.objects.filter(Canceled="N", header__Canceled="N", header__DocStatus="O")
        .values("ItemCode", "WhsCode", "Quantity", "OpenQty")
        .iterator()
    ):
        ic = (row["ItemCode"] or "").strip()
        wh = (row["WhsCode"] or "").strip()
        if ic and wh:
            on_order[(ic, wh)] += _por1_effective_on_order_qty(row)

    items = {k[0] for k in committed} | {k[0] for k in on_order}
    for item in items:
        whs = set()
        for (ic, wh), _ in committed.items():
            if ic == item:
                whs.add(wh)
        for (ic, wh), _ in on_order.items():
            if ic == item:
                whs.add(wh)
        for wh in OITW.objects.filter(ItemCode=item).values_list("WhsCode", flat=True):
            whs.add(wh)
        for wh in whs:
            oitw, _created = OITW.objects.select_for_update().get_or_create(
                ItemCode=item,
                WhsCode=wh,
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
            oitw.IsCommited = committed.get((item, wh), Decimal("0"))
            oitw.OrderQty = on_order.get((item, wh), Decimal("0"))
            oitw.save(update_fields=["IsCommited", "OrderQty"])

        agg_c = OITW.objects.filter(ItemCode=item, Canceled="N").aggregate(
            s=Coalesce(Sum("IsCommited"), Decimal("0"))
        )
        agg_o = OITW.objects.filter(ItemCode=item, Canceled="N").aggregate(
            s=Coalesce(Sum("OrderQty"), Decimal("0"))
        )
        OITM.objects.filter(pk=item).update(
            IsCommited=Decimal(str(agg_c["s"] or "0")),
            OnOrder=Decimal(str(agg_o["s"] or "0")),
        )
