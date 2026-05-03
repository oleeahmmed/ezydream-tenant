"""
Warehouse Bolt API — গুদাম মাস্টার (``OWHS``)।

``django_bolt_guide.md``: ``APIView``, ``BadRequest`` / ``NotFound``। সিরিয়ালাইজার: ``serializers.py``।
"""
from __future__ import annotations

from typing import Any

from asgiref.sync import sync_to_async
from django.db import IntegrityError
from django.db.models import Q
from django_bolt import BoltAPI
from django_bolt.auth import IsAuthenticated, JWTAuthentication
from django_bolt.exceptions import BadRequest, NotFound
from django_bolt.views import APIView

from apps.warehouse.models import OWHS

from .serializers import (
    WarehouseCreateBody,
    WarehousePage,
    WarehousePatchBody,
    WarehouseResponse,
)


WAREHOUSE_API_PREFIX = "/api/warehouse"


class WarehouseCollection(APIView):
    """List warehouses (GET) or create one (POST)."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> WarehousePage:
        qd = getattr(self.request, "query", None) or {}
        try:
            limit = min(100, max(1, int(qd.get("limit", "50"))))
        except ValueError:
            limit = 50
        try:
            offset = max(0, int(qd.get("offset", "0")))
        except ValueError:
            offset = 0
        search_prefix = (qd.get("q") or "").strip()
        active_only = (qd.get("active_only") or "1").strip().lower() in ("1", "true", "yes", "")
        queryset = OWHS.objects.all().order_by("WhsCode")
        if active_only and (qd.get("include_deleted", "").strip().lower() not in ("1", "true", "yes")):
            queryset = queryset.filter(Inactive="N")
        if search_prefix:
            queryset = queryset.filter(
                Q(WhsCode__istartswith=search_prefix)
                | Q(WhsName__istartswith=search_prefix)
                | Q(Location__istartswith=search_prefix)
                | Q(City__istartswith=search_prefix)
                | Q(Street__istartswith=search_prefix)
                | Q(ZipCode__istartswith=search_prefix)
                | Q(E_Mail__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return WarehousePage(
            items=[
                WarehouseResponse(
                    WhsCode=row.WhsCode,
                    WhsName=row.WhsName,
                    Location=row.Location or "",
                    Inactive=row.Inactive,
                )
                for row in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: WarehouseCreateBody) -> WarehouseResponse:
        inactive = (data.Inactive or "N").strip().upper()[:1] or "N"
        if inactive not in ("Y", "N"):
            raise BadRequest(detail="Inactive must be Y or N.")
        warehouse = OWHS(
            WhsCode=data.WhsCode.strip(),
            WhsName=data.WhsName.strip(),
            Location=(data.Location or "").strip(),
            Inactive=inactive,
        )
        try:
            await warehouse.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate WhsCode.")
        return WarehouseResponse(
            WhsCode=warehouse.WhsCode,
            WhsName=warehouse.WhsName,
            Location=warehouse.Location or "",
            Inactive=warehouse.Inactive,
        )


class WarehouseDetail(APIView):
    """Single warehouse: GET / PATCH / DELETE (DELETE = inactive ``Inactive='Y'``)."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, whs_code: str) -> WarehouseResponse:
        code = whs_code.strip()
        try:
            row = await OWHS.objects.aget(pk=code)
        except OWHS.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if row.Inactive == "Y" and (qd.get("include_deleted", "").strip().lower() not in ("1", "true", "yes")):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return WarehouseResponse(
            WhsCode=row.WhsCode,
            WhsName=row.WhsName,
            Location=row.Location or "",
            Inactive=row.Inactive,
        )

    async def patch(self, whs_code: str, data: WarehousePatchBody) -> WarehouseResponse:
        code = whs_code.strip()
        try:
            row = await OWHS.objects.aget(pk=code)
        except OWHS.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.WhsName is not None:
            row.WhsName = data.WhsName.strip()
        if data.Location is not None:
            row.Location = data.Location.strip()
        if data.Inactive is not None:
            v = (data.Inactive or "N").strip().upper()[:1] or "N"
            if v not in ("Y", "N"):
                raise BadRequest(detail="Inactive must be Y or N.")
            row.Inactive = v
        await row.asave()
        return WarehouseResponse(
            WhsCode=row.WhsCode,
            WhsName=row.WhsName,
            Location=row.Location or "",
            Inactive=row.Inactive,
        )

    async def delete(self, whs_code: str) -> WarehouseResponse:
        code = whs_code.strip()
        try:
            row = await OWHS.objects.aget(pk=code)
        except OWHS.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        row.Inactive = "Y"
        await row.asave(update_fields=["Inactive"])
        return WarehouseResponse(
            WhsCode=row.WhsCode,
            WhsName=row.WhsName,
            Location=row.Location or "",
            Inactive=row.Inactive,
        )


def attach_warehouse_routes(api: BoltAPI) -> None:
    """Register Bolt routes for this app."""
    tag = ["warehouse"]
    api.view(WAREHOUSE_API_PREFIX + "/warehouses", methods=["GET", "POST"], status_code=200, tags=tag)(WarehouseCollection)
    api.view(
        WAREHOUSE_API_PREFIX + "/warehouses/{whs_code}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(WarehouseDetail)
    api.view(WAREHOUSE_API_PREFIX + "/owhs", methods=["GET", "POST"], status_code=200, tags=tag)(WarehouseCollection)
    api.view(
        WAREHOUSE_API_PREFIX + "/owhs/{whs_code}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(WarehouseDetail)
