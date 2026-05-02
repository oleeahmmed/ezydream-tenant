"""
Production — ইনপুট ও আউটপুট সিরিয়ালাইজার (``django_bolt_guide.md`` ধারণা)।

নামগুলো বিশেষ্য (``BomHeaderResponse``, ``ProductionOrderPage``, …)।
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated, Any

from django_bolt.serializers import Serializer, field
from django_bolt.serializers.nested import Nested

PAGE_MAX_ITEMS = 100


class BomHeaderResponse(Serializer):
    Code: str
    TreeType: str
    Quantity: str
    Canceled: str




class BomHeaderPage(Serializer):
    items: Annotated[list[BomHeaderResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class BomHeaderCreateBody(Serializer):
    Code: str
    TreeType: str = field(default="P")
    Quantity: str = field(default="1")




class BomHeaderPatchBody(Serializer):
    TreeType: str | None = field(default=None)
    Quantity: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class BomLineResponse(Serializer):
    Father: str
    LineNum: int
    ItemCode: str
    Quantity: str
    WhsCode: str
    Canceled: str




class BomLinePage(Serializer):
    items: Annotated[list[BomLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class BomLineCreateBody(Serializer):
    Father: str
    LineNum: int
    ItemCode: str
    Quantity: str
    WhsCode: str




class BomLinePatchBody(Serializer):
    ItemCode: str | None = field(default=None)
    Quantity: str | None = field(default=None)
    WhsCode: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class ProductionOrderResponse(Serializer):
    DocEntry: int
    DocNum: int | None = field(default=None)
    ItemCode: str
    Status: str
    PlannedQty: str
    CmpltQty: str
    PostDate: date
    WhsCode: str
    Canceled: str




class ProductionOrderPage(Serializer):
    items: Annotated[list[ProductionOrderResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class ProductionOrderCreateBody(Serializer):
    DocNum: int | None = field(default=None)
    ItemCode: str
    Status: str = field(default="P")
    PlannedQty: str
    CmpltQty: str = field(default="0")
    PostDate: date
    WhsCode: str




class ProductionOrderPatchBody(Serializer):
    DocNum: int | None = field(default=None)
    ItemCode: str | None = field(default=None)
    Status: str | None = field(default=None)
    PlannedQty: str | None = field(default=None)
    CmpltQty: str | None = field(default=None)
    PostDate: date | None = field(default=None)
    WhsCode: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class ProductionOrderLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    PlannedQty: str
    IssuedQty: str
    WhsCode: str
    Canceled: str




class ProductionOrderLinePage(Serializer):
    items: Annotated[list[ProductionOrderLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class ProductionOrderLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    PlannedQty: str
    IssuedQty: str = field(default="0")
    WhsCode: str




class ProductionOrderLinePatchBody(Serializer):
    ItemCode: str | None = field(default=None)
    PlannedQty: str | None = field(default=None)
    IssuedQty: str | None = field(default=None)
    WhsCode: str | None = field(default=None)
    Canceled: str | None = field(default=None)
