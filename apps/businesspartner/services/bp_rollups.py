"""
Recompute OCRD roll-up fields from posted sales / purchase / finance documents.

- OrdersBal: sum of open ORDR.DocTotal + open OPOR.DocTotal for this CardCode.
- DNotesBal: sum of open ODLN.DocTotal.
- Balance: sum of OINV.DocTotal (not canceled) minus sum of ORCT.DocTotal (open payments).
"""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce

from apps.businesspartner.models import OCRD


@transaction.atomic
def recalculate_bp_rollups(card_code: str) -> None:
    cc = (card_code or "").strip()
    if not cc:
        return
    if not OCRD.objects.select_for_update().filter(pk=cc).exists():
        return

    from apps.finance.models import ORCT
    from apps.purchase.models import OPOR
    from apps.sales.models import ODLN, OINV, ORDR

    orders_sum = ORDR.objects.filter(CardCode=cc, Canceled="N", DocStatus="O").aggregate(
        s=Coalesce(Sum("DocTotal"), Decimal("0"))
    )["s"] or Decimal("0")
    por_sum = OPOR.objects.filter(CardCode=cc, Canceled="N", DocStatus="O").aggregate(
        s=Coalesce(Sum("DocTotal"), Decimal("0"))
    )["s"] or Decimal("0")
    dnotes_sum = ODLN.objects.filter(CardCode=cc, Canceled="N", DocStatus="O").aggregate(
        s=Coalesce(Sum("DocTotal"), Decimal("0"))
    )["s"] or Decimal("0")
    inv_sum = OINV.objects.filter(CardCode=cc, Canceled="N").aggregate(s=Coalesce(Sum("DocTotal"), Decimal("0")))[
        "s"
    ] or Decimal("0")
    pay_sum = ORCT.objects.filter(CardCode=cc, DocStatus="O").aggregate(s=Coalesce(Sum("DocTotal"), Decimal("0")))[
        "s"
    ] or Decimal("0")

    orders_bal = Decimal(str(orders_sum)) + Decimal(str(por_sum))
    dnotes_bal = Decimal(str(dnotes_sum))
    balance = Decimal(str(inv_sum)) - Decimal(str(pay_sum))

    OCRD.objects.filter(pk=cc).update(
        OrdersBal=orders_bal,
        DNotesBal=dnotes_bal,
        Balance=balance,
    )
