"""
Warehouse — ইনপুট ও আউটপুট সিরিয়ালাইজার (``django_bolt_guide.md`` ধারণা)।

নামগুলো বিশেষ্য (``WarehouseResponse``, ``WarehousePage``, …)।
"""

from __future__ import annotations

from typing import Annotated, Any

from django_bolt.serializers import Serializer, field
from django_bolt.serializers.nested import Nested

PAGE_MAX_ITEMS = 100


class WarehouseResponse(Serializer):
    WhsCode: str
    WhsName: str
    Location: str = field(default="")
    Inactive: str


class WarehousePage(Serializer):
    items: Annotated[list[WarehouseResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int


class WarehouseCreateBody(Serializer):
    WhsCode: str
    WhsName: str
    Location: str = field(default="")
    Inactive: str = field(default="N")


class WarehousePatchBody(Serializer):
    WhsName: str | None = field(default=None)
    Location: str | None = field(default=None)
    Inactive: str | None = field(default=None)
