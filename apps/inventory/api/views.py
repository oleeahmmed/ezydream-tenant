"""
Inventory Bolt API — মাল, গ্রুপ, স্টক, ডকুমেন্ট।

``django_bolt_guide.md``: ``APIView``, ``BadRequest`` / ``NotFound``। সিরিয়ালাইজার: ``serializers.py``।
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Any

from asgiref.sync import sync_to_async
from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone
from django_bolt import BoltAPI
from django_bolt.auth import IsAuthenticated, JWTAuthentication
from django_bolt.exceptions import BadRequest, NotFound
from django_bolt.views import APIView

from apps.inventory.models import (
    IGN1,
    IGE1,
    INC1,
    OUOM,
    OINC,
    OIGE,
    OIGN,
    OITB,
    OITM,
    OITW,
    OINM,
    OWTQ,
    OWTR,
    WTQ1,
    WTR1,
)

from .serializers import (
    InventoryGoodsIssueCreateBody,
    InventoryGoodsIssueLineCreateBody,
    InventoryGoodsIssueLinePage,
    InventoryGoodsIssueLinePatchBody,
    InventoryGoodsIssueLineResponse,
    InventoryGoodsIssuePage,
    InventoryGoodsIssuePatchBody,
    InventoryGoodsIssueResponse,
    InventoryGoodsReceiptCreateBody,
    InventoryGoodsReceiptLineCreateBody,
    InventoryGoodsReceiptLinePage,
    InventoryGoodsReceiptLinePatchBody,
    InventoryGoodsReceiptLineResponse,
    InventoryGoodsReceiptPage,
    InventoryGoodsReceiptPatchBody,
    InventoryGoodsReceiptResponse,
    InventoryPostingCreateBody,
    InventoryPostingPage,
    InventoryPostingPatchBody,
    InventoryPostingResponse,
    ItemCreateBody,
    ItemGroupCreateBody,
    ItemGroupPage,
    ItemGroupPatchBody,
    ItemGroupResponse,
    ItemPage,
    ItemPatchBody,
    ItemResponse,
    ItemWarehouseStockCreateBody,
    ItemWarehouseStockPage,
    ItemWarehouseStockPatchBody,
    ItemWarehouseStockResponse,
    StockTakeCreateBody,
    StockTakeLineCreateBody,
    StockTakeLinePage,
    StockTakeLinePatchBody,
    StockTakeLineResponse,
    StockTakePage,
    StockTakePatchBody,
    StockTakeResponse,
    StockTransferCreateBody,
    StockTransferLineCreateBody,
    StockTransferLinePage,
    StockTransferLinePatchBody,
    StockTransferLineResponse,
    StockTransferPage,
    StockTransferPatchBody,
    StockTransferResponse,
    StockTransferRequestCreateBody,
    StockTransferRequestLineCreateBody,
    StockTransferRequestLinePage,
    StockTransferRequestLinePatchBody,
    StockTransferRequestLineResponse,
    StockTransferRequestPage,
    StockTransferRequestPatchBody,
    StockTransferRequestResponse,
    UnitOfMeasureCreateBody,
    UnitOfMeasurePage,
    UnitOfMeasurePatchBody,
    UnitOfMeasureResponse,
)


INVENTORY_API_PREFIX = "/api/inventory"


class ItemGroupCollection(APIView):
    """Item groups: list with optional ``q`` search, or create one row."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> ItemGroupPage:
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
        qs = OITB.objects.all().order_by("ItmsGrpCod")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            qs = qs.filter(Canceled="N")
        if search_prefix:
            cond = Q(ItmsGrpNam__istartswith=search_prefix)
            if search_prefix.isdigit():
                cond |= Q(ItmsGrpCod=int(search_prefix))
            qs = qs.filter(cond)
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return ItemGroupPage(
            items=[ItemGroupResponse(ItmsGrpCod=o.ItmsGrpCod, ItmsGrpNam=o.ItmsGrpNam, Canceled=o.Canceled) for o in rows],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: ItemGroupCreateBody) -> ItemGroupResponse:
        o = OITB(ItmsGrpCod=int(data.ItmsGrpCod), ItmsGrpNam=data.ItmsGrpNam.strip())
        try:
            await o.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate ItmsGrpCod.")
        return ItemGroupResponse(ItmsGrpCod=o.ItmsGrpCod, ItmsGrpNam=o.ItmsGrpNam, Canceled=o.Canceled)


class ItemGroupDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, itms_grp_cod: int) -> ItemGroupResponse:
        try:
            o = await OITB.objects.aget(pk=int(itms_grp_cod))
        except OITB.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return ItemGroupResponse(ItmsGrpCod=o.ItmsGrpCod, ItmsGrpNam=o.ItmsGrpNam, Canceled=o.Canceled)

    async def patch(self, itms_grp_cod: int, data: ItemGroupPatchBody) -> ItemGroupResponse:
        try:
            o = await OITB.objects.aget(pk=int(itms_grp_cod))
        except OITB.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.ItmsGrpNam is not None:
            o.ItmsGrpNam = data.ItmsGrpNam.strip()
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return ItemGroupResponse(ItmsGrpCod=o.ItmsGrpCod, ItmsGrpNam=o.ItmsGrpNam, Canceled=o.Canceled)

    async def delete(self, itms_grp_cod: int) -> ItemGroupResponse:
        try:
            o = await OITB.objects.aget(pk=int(itms_grp_cod))
        except OITB.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return ItemGroupResponse(ItmsGrpCod=o.ItmsGrpCod, ItmsGrpNam=o.ItmsGrpNam, Canceled=o.Canceled)


class ItemCollection(APIView):
    """Item master (OITM): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> ItemPage:
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
        qs = OITM.objects.select_related("ItmsGrpCod").all().order_by("ItemCode")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            qs = qs.filter(ValidFor="Y")
        if search_prefix:
            qs = qs.filter(Q(ItemCode__istartswith=search_prefix) | Q(ItemName__istartswith=search_prefix))
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return ItemPage(
            items=[
                ItemResponse(
                    ItemCode=o.ItemCode,
                    ItemName=o.ItemName,
                    ItmsGrpCod=o.ItmsGrpCod_id,
                    InvntItem=o.InvntItem,
                    OnHand=str(o.OnHand),
                    IsCommited=str(o.IsCommited),
                    OnOrder=str(o.OnOrder),
                    ByWh=o.ByWh,
                    ValidFor=o.ValidFor,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: ItemCreateBody) -> ItemResponse:
        if not await OITB.objects.filter(pk=data.ItmsGrpCod).aexists():
            raise BadRequest(detail="Invalid ItmsGrpCod (OITB).")
        inv = (data.InvntItem or "Y").strip().upper()[:1] or "Y"
        byw = (data.ByWh or "N").strip().upper()[:1] or "N"
        if inv not in ("Y", "N") or byw not in ("Y", "N"):
            raise BadRequest(detail="InvntItem and ByWh must be Y or N.")
        o = OITM(
            ItemCode=data.ItemCode.strip(),
            ItemName=data.ItemName.strip(),
            ItmsGrpCod_id=int(data.ItmsGrpCod),
            InvntItem=inv,
            OnHand=Decimal(str(data.OnHand or "0")),
            IsCommited=Decimal(str(data.IsCommited or "0")),
            OnOrder=Decimal(str(data.OnOrder or "0")),
            ByWh=byw,
        )
        try:
            await o.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate ItemCode.")
        return ItemResponse(
            ItemCode=o.ItemCode,
            ItemName=o.ItemName,
            ItmsGrpCod=o.ItmsGrpCod_id,
            InvntItem=o.InvntItem,
            OnHand=str(o.OnHand),
            IsCommited=str(o.IsCommited),
            OnOrder=str(o.OnOrder),
            ByWh=o.ByWh,
            ValidFor=o.ValidFor,
        )


class ItemDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, item_code: str) -> ItemResponse:
        try:
            _ic = (item_code).strip()
            o = await OITM.objects.select_related("ItmsGrpCod").aget(pk=_ic)
        except OITM.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and o.ValidFor == "N":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return ItemResponse(
            ItemCode=o.ItemCode,
            ItemName=o.ItemName,
            ItmsGrpCod=o.ItmsGrpCod_id,
            InvntItem=o.InvntItem,
            OnHand=str(o.OnHand),
            IsCommited=str(o.IsCommited),
            OnOrder=str(o.OnOrder),
            ByWh=o.ByWh,
            ValidFor=o.ValidFor,
        )

    async def patch(self, item_code: str, data: ItemPatchBody) -> ItemResponse:
        try:
            _ic = (item_code).strip()
            o = await OITM.objects.select_related("ItmsGrpCod").aget(pk=_ic)
        except OITM.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and o.ValidFor == "N":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.ItemName is not None:
            o.ItemName = data.ItemName.strip()
        if data.ItmsGrpCod is not None:
            if not await OITB.objects.filter(pk=data.ItmsGrpCod).aexists():
                raise BadRequest(detail="Invalid ItmsGrpCod (OITB).")
            o.ItmsGrpCod_id = int(data.ItmsGrpCod)
        if data.InvntItem is not None:
            v = (data.InvntItem or "Y").strip().upper()[:1] or "Y"
            if v not in ("Y", "N"):
                raise BadRequest(detail="InvntItem must be Y or N.")
            o.InvntItem = v
        if data.OnHand is not None:
            o.OnHand = Decimal(str(data.OnHand))
        if data.IsCommited is not None:
            o.IsCommited = Decimal(str(data.IsCommited))
        if data.OnOrder is not None:
            o.OnOrder = Decimal(str(data.OnOrder))
        if data.ByWh is not None:
            w = (data.ByWh or "N").strip().upper()[:1] or "N"
            if w not in ("Y", "N"):
                raise BadRequest(detail="ByWh must be Y or N.")
            o.ByWh = w
        if data.ValidFor is not None:
            vf = (data.ValidFor or "Y").strip().upper()[:1] or "Y"
            if vf not in ("Y", "N"):
                raise BadRequest(detail="ValidFor must be Y or N.")
            o.ValidFor = vf
        await o.asave()
        return ItemResponse(
            ItemCode=o.ItemCode,
            ItemName=o.ItemName,
            ItmsGrpCod=o.ItmsGrpCod_id,
            InvntItem=o.InvntItem,
            OnHand=str(o.OnHand),
            IsCommited=str(o.IsCommited),
            OnOrder=str(o.OnOrder),
            ByWh=o.ByWh,
            ValidFor=o.ValidFor,
        )

    async def delete(self, item_code: str) -> ItemResponse:
        """SAP-style: ``ValidFor='N'`` (item stays in DB)."""
        try:
            _ic = (item_code).strip()
            o = await OITM.objects.select_related("ItmsGrpCod").aget(pk=_ic)
        except OITM.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and o.ValidFor == "N":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.ValidFor = "N"
        await o.asave(update_fields=["ValidFor"])
        return ItemResponse(
            ItemCode=o.ItemCode,
            ItemName=o.ItemName,
            ItmsGrpCod=o.ItmsGrpCod_id,
            InvntItem=o.InvntItem,
            OnHand=str(o.OnHand),
            IsCommited=str(o.IsCommited),
            OnOrder=str(o.OnOrder),
            ByWh=o.ByWh,
            ValidFor=o.ValidFor,
        )


class ItemWarehouseStockCollection(APIView):
    """Per-warehouse stock (OITW): list or upsert one row."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> ItemWarehouseStockPage:
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
        query_dict = getattr(self.request, "query", None) or {}
        item_code = (query_dict.get("item_code") or "").strip()
        whs_code = (query_dict.get("whs_code") or "").strip()
        qs = OITW.objects.all().order_by("WhsCode", "ItemCode")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            qs = qs.filter(Canceled="N")
        if item_code:
            qs = qs.filter(ItemCode__istartswith=item_code)
        if whs_code:
            qs = qs.filter(WhsCode__istartswith=whs_code)
        if search_prefix:
            qs = qs.filter(Q(ItemCode__istartswith=search_prefix) | Q(WhsCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return ItemWarehouseStockPage(
            items=[
                ItemWarehouseStockResponse(
                    ItemCode=o.ItemCode,
                    WhsCode=o.WhsCode,
                    OnHand=str(o.OnHand),
                    IsCommited=str(o.IsCommited),
                    AvgPrice=str(o.AvgPrice),
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: ItemWarehouseStockCreateBody) -> ItemWarehouseStockResponse:
        o, _created = await OITW.objects.aupdate_or_create(
            ItemCode=data.ItemCode.strip(),
            WhsCode=data.WhsCode.strip(),
            defaults={
                "OnHand": Decimal(str(data.OnHand or "0")),
                "IsCommited": Decimal(str(data.IsCommited or "0")),
                "AvgPrice": Decimal(str(data.AvgPrice or "0")),
                "Canceled": "N",
            },
        )
        return ItemWarehouseStockResponse(
            ItemCode=o.ItemCode,
            WhsCode=o.WhsCode,
            OnHand=str(o.OnHand),
            IsCommited=str(o.IsCommited),
            AvgPrice=str(o.AvgPrice),
            Canceled=o.Canceled,
        )


class ItemWarehouseStockDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, item_code: str, whs_code: str) -> ItemWarehouseStockResponse:
        try:
            o = await OITW.objects.aget(ItemCode=(item_code).strip(), WhsCode=(whs_code).strip())
        except OITW.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return ItemWarehouseStockResponse(
            ItemCode=o.ItemCode,
            WhsCode=o.WhsCode,
            OnHand=str(o.OnHand),
            IsCommited=str(o.IsCommited),
            AvgPrice=str(o.AvgPrice),
            Canceled=o.Canceled,
        )

    async def patch(self, item_code: str, whs_code: str, data: ItemWarehouseStockPatchBody) -> ItemWarehouseStockResponse:
        try:
            o = await OITW.objects.aget(ItemCode=(item_code).strip(), WhsCode=(whs_code).strip())
        except OITW.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.OnHand is not None:
            o.OnHand = Decimal(str(data.OnHand))
        if data.IsCommited is not None:
            o.IsCommited = Decimal(str(data.IsCommited))
        if data.AvgPrice is not None:
            o.AvgPrice = Decimal(str(data.AvgPrice))
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return ItemWarehouseStockResponse(
            ItemCode=o.ItemCode,
            WhsCode=o.WhsCode,
            OnHand=str(o.OnHand),
            IsCommited=str(o.IsCommited),
            AvgPrice=str(o.AvgPrice),
            Canceled=o.Canceled,
        )

    async def delete(self, item_code: str, whs_code: str) -> ItemWarehouseStockResponse:
        try:
            o = await OITW.objects.aget(ItemCode=(item_code).strip(), WhsCode=(whs_code).strip())
        except OITW.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return ItemWarehouseStockResponse(
            ItemCode=o.ItemCode,
            WhsCode=o.WhsCode,
            OnHand=str(o.OnHand),
            IsCommited=str(o.IsCommited),
            AvgPrice=str(o.AvgPrice),
            Canceled=o.Canceled,
        )


class UnitOfMeasureCollection(APIView):
    """Units of measure (OUOM): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> UnitOfMeasurePage:
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
        qs = OUOM.objects.all().order_by("UomCode")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            qs = qs.filter(Locked="N")
        if search_prefix:
            qs = qs.filter(Q(UomCode__istartswith=search_prefix) | Q(UomName__istartswith=search_prefix))
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return UnitOfMeasurePage(
            items=[
                UnitOfMeasureResponse(
                    UomEntry=o.UomEntry,
                    UomCode=o.UomCode,
                    UomName=o.UomName,
                    Locked=o.Locked,
                    DataSource=o.DataSource,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: UnitOfMeasureCreateBody) -> UnitOfMeasureResponse:
        lk = (data.Locked or "N").strip().upper()[:1] or "N"
        if lk not in ("Y", "N"):
            raise BadRequest(detail="Locked must be Y or N.")
        ds = (data.DataSource or "N").strip().upper()[:1] or "N"
        o = OUOM(
            UomCode=data.UomCode.strip(),
            UomName=data.UomName.strip(),
            Locked=lk,
            DataSource=ds,
        )
        try:
            await o.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate UomCode.")
        return UnitOfMeasureResponse(
            UomEntry=o.UomEntry,
            UomCode=o.UomCode,
            UomName=o.UomName,
            Locked=o.Locked,
            DataSource=o.DataSource,
        )


class UnitOfMeasureDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, uom_entry: int) -> UnitOfMeasureResponse:
        try:
            o = await OUOM.objects.aget(pk=int(uom_entry))
        except OUOM.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and o.Locked == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return UnitOfMeasureResponse(
            UomEntry=o.UomEntry,
            UomCode=o.UomCode,
            UomName=o.UomName,
            Locked=o.Locked,
            DataSource=o.DataSource,
        )

    async def patch(self, uom_entry: int, data: UnitOfMeasurePatchBody) -> UnitOfMeasureResponse:
        try:
            o = await OUOM.objects.aget(pk=int(uom_entry))
        except OUOM.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and o.Locked == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.UomCode is not None:
            o.UomCode = data.UomCode.strip()
        if data.UomName is not None:
            o.UomName = data.UomName.strip()
        if data.Locked is not None:
            lk = (data.Locked or "N").strip().upper()[:1] or "N"
            if lk not in ("Y", "N"):
                raise BadRequest(detail="Locked must be Y or N.")
            o.Locked = lk
        if data.DataSource is not None:
            o.DataSource = (data.DataSource or "N").strip().upper()[:1] or "N"
        try:
            await o.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate UomCode.")
        return UnitOfMeasureResponse(
            UomEntry=o.UomEntry,
            UomCode=o.UomCode,
            UomName=o.UomName,
            Locked=o.Locked,
            DataSource=o.DataSource,
        )

    async def delete(self, uom_entry: int) -> UnitOfMeasureResponse:
        """Soft delete: ``Locked='Y'`` (SAP OUOM)."""
        try:
            o = await OUOM.objects.aget(pk=int(uom_entry))
        except OUOM.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and o.Locked == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Locked = "Y"
        await o.asave(update_fields=["Locked"])
        return UnitOfMeasureResponse(
            UomEntry=o.UomEntry,
            UomCode=o.UomCode,
            UomName=o.UomName,
            Locked=o.Locked,
            DataSource=o.DataSource,
        )


class StockTransferRequestCollection(APIView):
    """Inventory transfer request header (OWTQ): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> StockTransferRequestPage:
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
        qs = OWTQ.objects.all().order_by("-DocEntry")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            qs = qs.filter(Canceled="N")
        if search_prefix:
            qs = qs.filter(Q(Filler__istartswith=search_prefix) | Q(Comments__istartswith=search_prefix))
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return StockTransferRequestPage(
            items=[
                StockTransferRequestResponse(
                    DocEntry=o.DocEntry,
                    DocNum=o.DocNum,
                    DocDate=o.DocDate,
                    Filler=o.Filler,
                    Comments=o.Comments or "",
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: StockTransferRequestCreateBody) -> StockTransferRequestResponse:
        o = OWTQ(
            DocNum=data.DocNum,
            DocDate=data.DocDate,
            Filler=data.Filler.strip()[:8],
            Comments=(data.Comments or "").strip()[:254],
        )
        await o.asave()
        return StockTransferRequestResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocDate=o.DocDate,
            Filler=o.Filler,
            Comments=o.Comments or "",
            Canceled=o.Canceled,
        )


class StockTransferRequestDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> StockTransferRequestResponse:
        try:
            o = await OWTQ.objects.aget(pk=doc_entry)
        except OWTQ.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return StockTransferRequestResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocDate=o.DocDate,
            Filler=o.Filler,
            Comments=o.Comments or "",
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, data: StockTransferRequestPatchBody) -> StockTransferRequestResponse:
        try:
            o = await OWTQ.objects.aget(pk=doc_entry)
        except OWTQ.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.DocNum is not None:
            o.DocNum = data.DocNum
        if data.DocDate is not None:
            o.DocDate = data.DocDate
        if data.Filler is not None:
            o.Filler = data.Filler.strip()[:8]
        if data.Comments is not None:
            o.Comments = data.Comments.strip()[:254]
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return StockTransferRequestResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocDate=o.DocDate,
            Filler=o.Filler,
            Comments=o.Comments or "",
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int) -> StockTransferRequestResponse:
        try:
            o = await OWTQ.objects.aget(pk=doc_entry)
        except OWTQ.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return StockTransferRequestResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocDate=o.DocDate,
            Filler=o.Filler,
            Comments=o.Comments or "",
            Canceled=o.Canceled,
        )


class StockTransferRequestLineCollection(APIView):
    """Transfer request lines (WTQ1): list (optional ``doc_entry``) or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> StockTransferRequestLinePage:
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
        qd_de = getattr(self.request, "query", None) or {}
        raw_de = (qd_de.get("doc_entry") or "").strip()
        try:
            de = int(raw_de) if raw_de else None
        except ValueError:
            raise BadRequest(detail="doc_entry সঠিক পূর্ণসংখ্যা নয়।")
        qs = WTQ1.objects.all().order_by("header_id", "LineNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            qs = qs.filter(Canceled="N", header__Canceled="N")
        if de is not None:
            qs = qs.filter(header_id=de)
        if search_prefix:
            qs = qs.filter(
                Q(ItemCode__istartswith=search_prefix)
                | Q(FromWhsCod__istartswith=search_prefix)
                | Q(WhsCode__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return StockTransferRequestLinePage(
            items=[
                StockTransferRequestLineResponse(
                    DocEntry=o.header_id,
                    LineNum=o.LineNum,
                    ItemCode=o.ItemCode,
                    Quantity=str(o.Quantity),
                    OpenQty=str(o.OpenQty),
                    Price=str(o.Price),
                    FromWhsCod=o.FromWhsCod,
                    WhsCode=o.WhsCode,
                    LineStatus=o.LineStatus,
                    TargetType=o.TargetType,
                    TrgetEntry=o.TrgetEntry,
                    BaseRef=o.BaseRef or "",
                    BaseType=o.BaseType,
                    BaseEntry=o.BaseEntry,
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: StockTransferRequestLineCreateBody) -> StockTransferRequestLineResponse:
        hdr = await OWTQ.objects.filter(pk=data.DocEntry).afirst()
        if not hdr:
            raise BadRequest(detail="Invalid DocEntry (OWTQ).")
        if hdr.Canceled == "Y":
            raise BadRequest(detail="Cannot add lines to a canceled document.")
        st = (data.LineStatus or "O").strip().upper()[:1] or "O"
        if st not in ("O", "C"):
            raise BadRequest(detail="LineStatus must be O or C.")
        qty = Decimal(str(data.Quantity))
        open_qty = Decimal(str(data.OpenQty)) if data.OpenQty is not None else qty
        o = WTQ1(
            header_id=data.DocEntry,
            LineNum=int(data.LineNum),
            ItemCode=data.ItemCode.strip(),
            Quantity=qty,
            OpenQty=open_qty,
            Price=Decimal(str(data.Price or "0")),
            FromWhsCod=data.FromWhsCod.strip()[:8],
            WhsCode=data.WhsCode.strip()[:8],
            LineStatus=st,
            TargetType=int(data.TargetType) if data.TargetType is not None else -1,
            TrgetEntry=data.TrgetEntry,
            BaseRef=(data.BaseRef or "").strip()[:16],
            BaseType=data.BaseType,
            BaseEntry=data.BaseEntry,
        )
        try:
            await o.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        return StockTransferRequestLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            OpenQty=str(o.OpenQty),
            Price=str(o.Price),
            FromWhsCod=o.FromWhsCod,
            WhsCode=o.WhsCode,
            LineStatus=o.LineStatus,
            TargetType=o.TargetType,
            TrgetEntry=o.TrgetEntry,
            BaseRef=o.BaseRef or "",
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            Canceled=o.Canceled,
        )


class StockTransferRequestLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> StockTransferRequestLineResponse:
        try:
            o = await WTQ1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except WTQ1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return StockTransferRequestLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            OpenQty=str(o.OpenQty),
            Price=str(o.Price),
            FromWhsCod=o.FromWhsCod,
            WhsCode=o.WhsCode,
            LineStatus=o.LineStatus,
            TargetType=o.TargetType,
            TrgetEntry=o.TrgetEntry,
            BaseRef=o.BaseRef or "",
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, line_num: int, data: StockTransferRequestLinePatchBody) -> StockTransferRequestLineResponse:
        try:
            o = await WTQ1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except WTQ1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if o.header.Canceled == "Y":
            raise BadRequest(detail="Cannot edit lines of a canceled document.")
        if data.ItemCode is not None:
            o.ItemCode = data.ItemCode.strip()
        if data.Quantity is not None:
            o.Quantity = Decimal(str(data.Quantity))
        if data.OpenQty is not None:
            o.OpenQty = Decimal(str(data.OpenQty))
        if data.Price is not None:
            o.Price = Decimal(str(data.Price))
        if data.FromWhsCod is not None:
            o.FromWhsCod = data.FromWhsCod.strip()[:8]
        if data.WhsCode is not None:
            o.WhsCode = data.WhsCode.strip()[:8]
        if data.LineStatus is not None:
            st = (data.LineStatus or "O").strip().upper()[:1] or "O"
            if st not in ("O", "C"):
                raise BadRequest(detail="LineStatus must be O or C.")
            o.LineStatus = st
        if data.TargetType is not None:
            o.TargetType = int(data.TargetType)
        if data.TrgetEntry is not None:
            o.TrgetEntry = data.TrgetEntry
        if data.BaseRef is not None:
            o.BaseRef = data.BaseRef.strip()[:16]
        if data.BaseType is not None:
            o.BaseType = data.BaseType
        if data.BaseEntry is not None:
            o.BaseEntry = data.BaseEntry
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return StockTransferRequestLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            OpenQty=str(o.OpenQty),
            Price=str(o.Price),
            FromWhsCod=o.FromWhsCod,
            WhsCode=o.WhsCode,
            LineStatus=o.LineStatus,
            TargetType=o.TargetType,
            TrgetEntry=o.TrgetEntry,
            BaseRef=o.BaseRef or "",
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int, line_num: int) -> StockTransferRequestLineResponse:
        try:
            o = await WTQ1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except WTQ1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if o.header.Canceled == "Y":
            raise BadRequest(detail="Cannot delete lines of a canceled document.")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return StockTransferRequestLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            OpenQty=str(o.OpenQty),
            Price=str(o.Price),
            FromWhsCod=o.FromWhsCod,
            WhsCode=o.WhsCode,
            LineStatus=o.LineStatus,
            TargetType=o.TargetType,
            TrgetEntry=o.TrgetEntry,
            BaseRef=o.BaseRef or "",
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            Canceled=o.Canceled,
        )


class StockTransferCollection(APIView):
    """Inventory transfer header (OWTR): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> StockTransferPage:
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
        qs = OWTR.objects.all().order_by("-DocEntry")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            qs = qs.filter(Canceled="N")
        if search_prefix:
            qs = qs.filter(Q(Filler__istartswith=search_prefix) | Q(Comments__istartswith=search_prefix))
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return StockTransferPage(
            items=[
                StockTransferResponse(
                    DocEntry=o.DocEntry,
                    DocNum=o.DocNum,
                    DocDate=o.DocDate,
                    Filler=o.Filler,
                    Comments=o.Comments or "",
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: StockTransferCreateBody) -> StockTransferResponse:
        o = OWTR(
            DocNum=data.DocNum,
            DocDate=data.DocDate,
            Filler=data.Filler.strip(),
            Comments=(data.Comments or "").strip(),
        )
        await o.asave()
        return StockTransferResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocDate=o.DocDate,
            Filler=o.Filler,
            Comments=o.Comments or "",
            Canceled=o.Canceled,
        )


class StockTransferDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> StockTransferResponse:
        try:
            o = await OWTR.objects.aget(pk=doc_entry)
        except OWTR.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return StockTransferResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocDate=o.DocDate,
            Filler=o.Filler,
            Comments=o.Comments or "",
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, data: StockTransferPatchBody) -> StockTransferResponse:
        try:
            o = await OWTR.objects.aget(pk=doc_entry)
        except OWTR.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.DocNum is not None:
            o.DocNum = data.DocNum
        if data.DocDate is not None:
            o.DocDate = data.DocDate
        if data.Filler is not None:
            o.Filler = data.Filler.strip()[:20]
        if data.Comments is not None:
            o.Comments = data.Comments.strip()
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return StockTransferResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocDate=o.DocDate,
            Filler=o.Filler,
            Comments=o.Comments or "",
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int) -> StockTransferResponse:
        try:
            o = await OWTR.objects.aget(pk=doc_entry)
        except OWTR.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return StockTransferResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocDate=o.DocDate,
            Filler=o.Filler,
            Comments=o.Comments or "",
            Canceled=o.Canceled,
        )


class StockTransferLineCollection(APIView):
    """Transfer lines (WTR1): list (optional ``doc_entry``) or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> StockTransferLinePage:
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
        qd_de = getattr(self.request, "query", None) or {}
        raw_de = (qd_de.get("doc_entry") or "").strip()
        try:
            de = int(raw_de) if raw_de else None
        except ValueError:
            raise BadRequest(detail="doc_entry সঠিক পূর্ণসংখ্যা নয়।")
        qs = WTR1.objects.select_related("header").all().order_by("header_id", "LineNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            qs = qs.filter(Canceled="N", header__Canceled="N")
        if de is not None:
            qs = qs.filter(header_id=de)
        if search_prefix:
            qs = qs.filter(Q(ItemCode__istartswith=search_prefix) | Q(WhsCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return StockTransferLinePage(
            items=[
                StockTransferLineResponse(
                    DocEntry=o.header_id,
                    LineNum=o.LineNum,
                    ItemCode=o.ItemCode,
                    Quantity=str(o.Quantity),
                    WhsCode=o.WhsCode,
                    Price=str(o.Price),
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: StockTransferLineCreateBody) -> StockTransferLineResponse:
        hdr = await OWTR.objects.filter(pk=data.DocEntry).afirst()
        if not hdr:
            raise BadRequest(detail="Invalid DocEntry (OWTR).")
        if hdr.Canceled == "Y":
            raise BadRequest(detail="Cannot add lines to a canceled document.")
        o = WTR1(
            header_id=data.DocEntry,
            LineNum=int(data.LineNum),
            ItemCode=data.ItemCode.strip(),
            Quantity=Decimal(str(data.Quantity)),
            WhsCode=data.WhsCode.strip(),
            Price=Decimal(str(data.Price or "0")),
        )
        try:
            await o.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        return StockTransferLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            Price=str(o.Price),
            Canceled=o.Canceled,
        )


class StockTransferLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> StockTransferLineResponse:
        try:
            o = await WTR1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except WTR1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return StockTransferLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            Price=str(o.Price),
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, line_num: int, data: StockTransferLinePatchBody) -> StockTransferLineResponse:
        try:
            o = await WTR1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except WTR1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if o.header.Canceled == "Y":
            raise BadRequest(detail="Cannot edit lines of a canceled document.")
        if data.ItemCode is not None:
            o.ItemCode = data.ItemCode.strip()
        if data.Quantity is not None:
            o.Quantity = Decimal(str(data.Quantity))
        if data.WhsCode is not None:
            o.WhsCode = data.WhsCode.strip()
        if data.Price is not None:
            o.Price = Decimal(str(data.Price))
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return StockTransferLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            Price=str(o.Price),
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int, line_num: int) -> StockTransferLineResponse:
        try:
            o = await WTR1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except WTR1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if o.header.Canceled == "Y":
            raise BadRequest(detail="Cannot delete lines of a canceled document.")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return StockTransferLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            Price=str(o.Price),
            Canceled=o.Canceled,
        )


class InventoryGoodsReceiptCollection(APIView):
    """Goods receipt header (OIGN): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> InventoryGoodsReceiptPage:
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
        qs = OIGN.objects.all().order_by("-DocEntry")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            qs = qs.filter(Canceled="N")
        if search_prefix:
            qs = qs.filter(Comments__istartswith=search_prefix)
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return InventoryGoodsReceiptPage(
            items=[
                InventoryGoodsReceiptResponse(
                    DocEntry=o.DocEntry,
                    DocNum=o.DocNum,
                    DocDate=o.DocDate,
                    Comments=o.Comments or "",
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: InventoryGoodsReceiptCreateBody) -> InventoryGoodsReceiptResponse:
        o = OIGN(
            DocNum=data.DocNum,
            DocDate=data.DocDate,
            Comments=(data.Comments or "").strip(),
        )
        await o.asave()
        return InventoryGoodsReceiptResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocDate=o.DocDate,
            Comments=o.Comments or "",
            Canceled=o.Canceled,
        )


class InventoryGoodsReceiptDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> InventoryGoodsReceiptResponse:
        try:
            o = await OIGN.objects.aget(pk=doc_entry)
        except OIGN.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return InventoryGoodsReceiptResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocDate=o.DocDate,
            Comments=o.Comments or "",
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, data: InventoryGoodsReceiptPatchBody) -> InventoryGoodsReceiptResponse:
        try:
            o = await OIGN.objects.aget(pk=doc_entry)
        except OIGN.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.DocNum is not None:
            o.DocNum = data.DocNum
        if data.DocDate is not None:
            o.DocDate = data.DocDate
        if data.Comments is not None:
            o.Comments = data.Comments.strip()
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return InventoryGoodsReceiptResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocDate=o.DocDate,
            Comments=o.Comments or "",
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int) -> InventoryGoodsReceiptResponse:
        try:
            o = await OIGN.objects.aget(pk=doc_entry)
        except OIGN.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return InventoryGoodsReceiptResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocDate=o.DocDate,
            Comments=o.Comments or "",
            Canceled=o.Canceled,
        )


class InventoryGoodsReceiptLineCollection(APIView):
    """Goods receipt lines (IGN1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> InventoryGoodsReceiptLinePage:
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
        qd_de = getattr(self.request, "query", None) or {}
        raw_de = (qd_de.get("doc_entry") or "").strip()
        try:
            de = int(raw_de) if raw_de else None
        except ValueError:
            raise BadRequest(detail="doc_entry সঠিক পূর্ণসংখ্যা নয়।")
        qs = IGN1.objects.all().order_by("header_id", "LineNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            qs = qs.filter(Canceled="N", header__Canceled="N")
        if de is not None:
            qs = qs.filter(header_id=de)
        if search_prefix:
            qs = qs.filter(Q(ItemCode__istartswith=search_prefix) | Q(WhsCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return InventoryGoodsReceiptLinePage(
            items=[
                InventoryGoodsReceiptLineResponse(
                    DocEntry=o.header_id,
                    LineNum=o.LineNum,
                    ItemCode=o.ItemCode,
                    Quantity=str(o.Quantity),
                    WhsCode=o.WhsCode,
                    Price=str(o.Price),
                    BaseType=o.BaseType,
                    BaseEntry=o.BaseEntry,
                    BaseLine=o.BaseLine,
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: InventoryGoodsReceiptLineCreateBody) -> InventoryGoodsReceiptLineResponse:
        hdr = await OIGN.objects.filter(pk=data.DocEntry).afirst()
        if not hdr:
            raise BadRequest(detail="Invalid DocEntry (OIGN).")
        if hdr.Canceled == "Y":
            raise BadRequest(detail="Cannot add lines to a canceled document.")
        o = IGN1(
            header_id=data.DocEntry,
            LineNum=int(data.LineNum),
            ItemCode=data.ItemCode.strip(),
            Quantity=Decimal(str(data.Quantity)),
            WhsCode=data.WhsCode.strip(),
            Price=Decimal(str(data.Price or "0")),
            BaseType=data.BaseType,
            BaseEntry=data.BaseEntry,
            BaseLine=data.BaseLine,
        )
        try:
            await o.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        return InventoryGoodsReceiptLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            Price=str(o.Price),
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )


class InventoryGoodsReceiptLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> InventoryGoodsReceiptLineResponse:
        try:
            o = await IGN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except IGN1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return InventoryGoodsReceiptLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            Price=str(o.Price),
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, line_num: int, data: InventoryGoodsReceiptLinePatchBody) -> InventoryGoodsReceiptLineResponse:
        try:
            o = await IGN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except IGN1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if o.header.Canceled == "Y":
            raise BadRequest(detail="Cannot edit lines of a canceled document.")
        if data.ItemCode is not None:
            o.ItemCode = data.ItemCode.strip()
        if data.Quantity is not None:
            o.Quantity = Decimal(str(data.Quantity))
        if data.WhsCode is not None:
            o.WhsCode = data.WhsCode.strip()
        if data.Price is not None:
            o.Price = Decimal(str(data.Price))
        if data.BaseType is not None:
            o.BaseType = data.BaseType
        if data.BaseEntry is not None:
            o.BaseEntry = data.BaseEntry
        if data.BaseLine is not None:
            o.BaseLine = data.BaseLine
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return InventoryGoodsReceiptLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            Price=str(o.Price),
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int, line_num: int) -> InventoryGoodsReceiptLineResponse:
        try:
            o = await IGN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except IGN1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if o.header.Canceled == "Y":
            raise BadRequest(detail="Cannot delete lines of a canceled document.")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return InventoryGoodsReceiptLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            Price=str(o.Price),
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )


class InventoryGoodsIssueCollection(APIView):
    """Goods issue header (OIGE): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> InventoryGoodsIssuePage:
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
        qs = OIGE.objects.all().order_by("-DocEntry")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            qs = qs.filter(Canceled="N")
        if search_prefix:
            qs = qs.filter(Comments__istartswith=search_prefix)
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return InventoryGoodsIssuePage(
            items=[
                InventoryGoodsIssueResponse(
                    DocEntry=o.DocEntry,
                    DocNum=o.DocNum,
                    DocDate=o.DocDate,
                    Comments=o.Comments or "",
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: InventoryGoodsIssueCreateBody) -> InventoryGoodsIssueResponse:
        o = OIGE(
            DocNum=data.DocNum,
            DocDate=data.DocDate,
            Comments=(data.Comments or "").strip(),
        )
        await o.asave()
        return InventoryGoodsIssueResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocDate=o.DocDate,
            Comments=o.Comments or "",
            Canceled=o.Canceled,
        )


class InventoryGoodsIssueDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> InventoryGoodsIssueResponse:
        try:
            o = await OIGE.objects.aget(pk=doc_entry)
        except OIGE.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return InventoryGoodsIssueResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocDate=o.DocDate,
            Comments=o.Comments or "",
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, data: InventoryGoodsIssuePatchBody) -> InventoryGoodsIssueResponse:
        try:
            o = await OIGE.objects.aget(pk=doc_entry)
        except OIGE.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.DocNum is not None:
            o.DocNum = data.DocNum
        if data.DocDate is not None:
            o.DocDate = data.DocDate
        if data.Comments is not None:
            o.Comments = data.Comments.strip()
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return InventoryGoodsIssueResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocDate=o.DocDate,
            Comments=o.Comments or "",
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int) -> InventoryGoodsIssueResponse:
        try:
            o = await OIGE.objects.aget(pk=doc_entry)
        except OIGE.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return InventoryGoodsIssueResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocDate=o.DocDate,
            Comments=o.Comments or "",
            Canceled=o.Canceled,
        )


class InventoryGoodsIssueLineCollection(APIView):
    """Goods issue lines (IGE1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> InventoryGoodsIssueLinePage:
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
        qd_de = getattr(self.request, "query", None) or {}
        raw_de = (qd_de.get("doc_entry") or "").strip()
        try:
            de = int(raw_de) if raw_de else None
        except ValueError:
            raise BadRequest(detail="doc_entry সঠিক পূর্ণসংখ্যা নয়।")
        qs = IGE1.objects.all().order_by("header_id", "LineNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            qs = qs.filter(Canceled="N", header__Canceled="N")
        if de is not None:
            qs = qs.filter(header_id=de)
        if search_prefix:
            qs = qs.filter(Q(ItemCode__istartswith=search_prefix) | Q(WhsCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return InventoryGoodsIssueLinePage(
            items=[
                InventoryGoodsIssueLineResponse(
                    DocEntry=o.header_id,
                    LineNum=o.LineNum,
                    ItemCode=o.ItemCode,
                    Quantity=str(o.Quantity),
                    WhsCode=o.WhsCode,
                    Account=o.Account or "",
                    Price=str(o.Price),
                    BaseType=o.BaseType,
                    BaseEntry=o.BaseEntry,
                    BaseLine=o.BaseLine,
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: InventoryGoodsIssueLineCreateBody) -> InventoryGoodsIssueLineResponse:
        hdr = await OIGE.objects.filter(pk=data.DocEntry).afirst()
        if not hdr:
            raise BadRequest(detail="Invalid DocEntry (OIGE).")
        if hdr.Canceled == "Y":
            raise BadRequest(detail="Cannot add lines to a canceled document.")
        o = IGE1(
            header_id=data.DocEntry,
            LineNum=int(data.LineNum),
            ItemCode=data.ItemCode.strip(),
            Quantity=Decimal(str(data.Quantity)),
            WhsCode=data.WhsCode.strip(),
            Account=(data.Account or "").strip(),
            Price=Decimal(str(data.Price or "0")),
            BaseType=data.BaseType,
            BaseEntry=data.BaseEntry,
            BaseLine=data.BaseLine,
        )
        try:
            await o.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        return InventoryGoodsIssueLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            Account=o.Account or "",
            Price=str(o.Price),
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )


class InventoryGoodsIssueLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> InventoryGoodsIssueLineResponse:
        try:
            o = await IGE1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except IGE1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return InventoryGoodsIssueLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            Account=o.Account or "",
            Price=str(o.Price),
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, line_num: int, data: InventoryGoodsIssueLinePatchBody) -> InventoryGoodsIssueLineResponse:
        try:
            o = await IGE1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except IGE1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if o.header.Canceled == "Y":
            raise BadRequest(detail="Cannot edit lines of a canceled document.")
        if data.ItemCode is not None:
            o.ItemCode = data.ItemCode.strip()
        if data.Quantity is not None:
            o.Quantity = Decimal(str(data.Quantity))
        if data.WhsCode is not None:
            o.WhsCode = data.WhsCode.strip()
        if data.Account is not None:
            o.Account = data.Account.strip()
        if data.Price is not None:
            o.Price = Decimal(str(data.Price))
        if data.BaseType is not None:
            o.BaseType = data.BaseType
        if data.BaseEntry is not None:
            o.BaseEntry = data.BaseEntry
        if data.BaseLine is not None:
            o.BaseLine = data.BaseLine
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return InventoryGoodsIssueLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            Account=o.Account or "",
            Price=str(o.Price),
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int, line_num: int) -> InventoryGoodsIssueLineResponse:
        try:
            o = await IGE1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except IGE1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if o.header.Canceled == "Y":
            raise BadRequest(detail="Cannot delete lines of a canceled document.")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return InventoryGoodsIssueLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            Account=o.Account or "",
            Price=str(o.Price),
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )


class StockTakeCollection(APIView):
    """Inventory posting / count header (OINC): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> StockTakePage:
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
        qs = OINC.objects.all().order_by("-DocEntry")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            qs = qs.filter(Canceled="N")
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return StockTakePage(
            items=[
                StockTakeResponse(
                    DocEntry=o.DocEntry,
                    DocNum=o.DocNum,
                    CountDate=o.CountDate,
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: StockTakeCreateBody) -> StockTakeResponse:
        o = OINC(DocNum=data.DocNum, CountDate=data.CountDate)
        await o.asave()
        return StockTakeResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CountDate=o.CountDate,
            Canceled=o.Canceled,
        )


class StockTakeDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> StockTakeResponse:
        try:
            o = await OINC.objects.aget(pk=doc_entry)
        except OINC.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return StockTakeResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CountDate=o.CountDate,
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, data: StockTakePatchBody) -> StockTakeResponse:
        try:
            o = await OINC.objects.aget(pk=doc_entry)
        except OINC.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.DocNum is not None:
            o.DocNum = data.DocNum
        if data.CountDate is not None:
            o.CountDate = data.CountDate
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return StockTakeResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CountDate=o.CountDate,
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int) -> StockTakeResponse:
        try:
            o = await OINC.objects.aget(pk=doc_entry)
        except OINC.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return StockTakeResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CountDate=o.CountDate,
            Canceled=o.Canceled,
        )


class StockTakeLineCollection(APIView):
    """Inventory posting lines (INC1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> StockTakeLinePage:
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
        qd_de = getattr(self.request, "query", None) or {}
        raw_de = (qd_de.get("doc_entry") or "").strip()
        try:
            de = int(raw_de) if raw_de else None
        except ValueError:
            raise BadRequest(detail="doc_entry সঠিক পূর্ণসংখ্যা নয়।")
        qs = INC1.objects.all().order_by("header_id", "LineNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            qs = qs.filter(Canceled="N", header__Canceled="N")
        if de is not None:
            qs = qs.filter(header_id=de)
        if search_prefix:
            qs = qs.filter(Q(ItemCode__istartswith=search_prefix) | Q(WhsCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return StockTakeLinePage(
            items=[
                StockTakeLineResponse(
                    DocEntry=o.header_id,
                    LineNum=o.LineNum,
                    ItemCode=o.ItemCode,
                    WhsCode=o.WhsCode,
                    InQty=str(o.InQty),
                    OutQty=str(o.OutQty),
                    Difference=str(o.Difference),
                    Price=str(o.Price),
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: StockTakeLineCreateBody) -> StockTakeLineResponse:
        hdr = await OINC.objects.filter(pk=data.DocEntry).afirst()
        if not hdr:
            raise BadRequest(detail="Invalid DocEntry (OINC).")
        if hdr.Canceled == "Y":
            raise BadRequest(detail="Cannot add lines to a canceled document.")
        o = INC1(
            header_id=data.DocEntry,
            LineNum=int(data.LineNum),
            ItemCode=data.ItemCode.strip(),
            WhsCode=data.WhsCode.strip(),
            InQty=Decimal(str(data.InQty or "0")),
            OutQty=Decimal(str(data.OutQty or "0")),
            Difference=Decimal(str(data.Difference or "0")),
            Price=Decimal(str(data.Price or "0")),
        )
        try:
            await o.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        return StockTakeLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            WhsCode=o.WhsCode,
            InQty=str(o.InQty),
            OutQty=str(o.OutQty),
            Difference=str(o.Difference),
            Price=str(o.Price),
            Canceled=o.Canceled,
        )


class StockTakeLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> StockTakeLineResponse:
        try:
            o = await INC1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except INC1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return StockTakeLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            WhsCode=o.WhsCode,
            InQty=str(o.InQty),
            OutQty=str(o.OutQty),
            Difference=str(o.Difference),
            Price=str(o.Price),
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, line_num: int, data: StockTakeLinePatchBody) -> StockTakeLineResponse:
        try:
            o = await INC1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except INC1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if o.header.Canceled == "Y":
            raise BadRequest(detail="Cannot edit lines of a canceled document.")
        if data.ItemCode is not None:
            o.ItemCode = data.ItemCode.strip()
        if data.WhsCode is not None:
            o.WhsCode = data.WhsCode.strip()
        if data.InQty is not None:
            o.InQty = Decimal(str(data.InQty))
        if data.OutQty is not None:
            o.OutQty = Decimal(str(data.OutQty))
        if data.Difference is not None:
            o.Difference = Decimal(str(data.Difference))
        if data.Price is not None:
            o.Price = Decimal(str(data.Price))
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return StockTakeLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            WhsCode=o.WhsCode,
            InQty=str(o.InQty),
            OutQty=str(o.OutQty),
            Difference=str(o.Difference),
            Price=str(o.Price),
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int, line_num: int) -> StockTakeLineResponse:
        try:
            o = await INC1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except INC1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if o.header.Canceled == "Y":
            raise BadRequest(detail="Cannot delete lines of a canceled document.")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return StockTakeLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            WhsCode=o.WhsCode,
            InQty=str(o.InQty),
            OutQty=str(o.OutQty),
            Difference=str(o.Difference),
            Price=str(o.Price),
            Canceled=o.Canceled,
        )


class InventoryPostingCollection(APIView):
    """Stock ledger (OINM): list or append one movement row."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> InventoryPostingPage:
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
        qs = OINM.objects.all().order_by("-TransNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            qs = qs.filter(Canceled="N")
        if search_prefix:
            qs = qs.filter(
                Q(ItemCode__istartswith=search_prefix)
                | Q(Warehouse__istartswith=search_prefix)
                | Q(BASE_REF__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return InventoryPostingPage(
            items=[
                InventoryPostingResponse(
                    TransNum=o.TransNum,
                    TransType=o.TransType,
                    ItemCode=o.ItemCode,
                    Warehouse=o.Warehouse,
                    InQty=str(o.InQty),
                    OutQty=str(o.OutQty),
                    Price=str(o.Price),
                    BASE_REF=o.BASE_REF or "",
                    DocTime=o.DocTime,
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: InventoryPostingCreateBody) -> InventoryPostingResponse:
        dt = data.DocTime if data.DocTime is not None else timezone.now()
        o = OINM(
            TransType=int(data.TransType),
            ItemCode=data.ItemCode.strip(),
            Warehouse=data.Warehouse.strip(),
            InQty=Decimal(str(data.InQty or "0")),
            OutQty=Decimal(str(data.OutQty or "0")),
            Price=Decimal(str(data.Price or "0")),
            BASE_REF=(data.BASE_REF or "").strip(),
            DocTime=dt,
        )
        await o.asave()
        return InventoryPostingResponse(
            TransNum=o.TransNum,
            TransType=o.TransType,
            ItemCode=o.ItemCode,
            Warehouse=o.Warehouse,
            InQty=str(o.InQty),
            OutQty=str(o.OutQty),
            Price=str(o.Price),
            BASE_REF=o.BASE_REF or "",
            DocTime=o.DocTime,
            Canceled=o.Canceled,
        )


class InventoryPostingDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, trans_num: int) -> InventoryPostingResponse:
        try:
            o = await OINM.objects.aget(pk=int(trans_num))
        except OINM.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return InventoryPostingResponse(
            TransNum=o.TransNum,
            TransType=o.TransType,
            ItemCode=o.ItemCode,
            Warehouse=o.Warehouse,
            InQty=str(o.InQty),
            OutQty=str(o.OutQty),
            Price=str(o.Price),
            BASE_REF=o.BASE_REF or "",
            DocTime=o.DocTime,
            Canceled=o.Canceled,
        )

    async def patch(self, trans_num: int, data: InventoryPostingPatchBody) -> InventoryPostingResponse:
        try:
            o = await OINM.objects.aget(pk=int(trans_num))
        except OINM.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.TransType is not None:
            o.TransType = int(data.TransType)
        if data.ItemCode is not None:
            o.ItemCode = data.ItemCode.strip()
        if data.Warehouse is not None:
            o.Warehouse = data.Warehouse.strip()
        if data.InQty is not None:
            o.InQty = Decimal(str(data.InQty))
        if data.OutQty is not None:
            o.OutQty = Decimal(str(data.OutQty))
        if data.Price is not None:
            o.Price = Decimal(str(data.Price))
        if data.BASE_REF is not None:
            o.BASE_REF = data.BASE_REF.strip()
        if data.DocTime is not None:
            o.DocTime = data.DocTime
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return InventoryPostingResponse(
            TransNum=o.TransNum,
            TransType=o.TransType,
            ItemCode=o.ItemCode,
            Warehouse=o.Warehouse,
            InQty=str(o.InQty),
            OutQty=str(o.OutQty),
            Price=str(o.Price),
            BASE_REF=o.BASE_REF or "",
            DocTime=o.DocTime,
            Canceled=o.Canceled,
        )

    async def delete(self, trans_num: int) -> InventoryPostingResponse:
        try:
            o = await OINM.objects.aget(pk=int(trans_num))
        except OINM.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return InventoryPostingResponse(
            TransNum=o.TransNum,
            TransType=o.TransType,
            ItemCode=o.ItemCode,
            Warehouse=o.Warehouse,
            InQty=str(o.InQty),
            OutQty=str(o.OutQty),
            Price=str(o.Price),
            BASE_REF=o.BASE_REF or "",
            DocTime=o.DocTime,
            Canceled=o.Canceled,
        )


def attach_inventory_routes(api: BoltAPI) -> None:
    """Register all inventory Bolt routes on the given API object."""

    tag = ["inventory"]
    # Human-readable paths (legacy SAP-style paths kept for compatibility).
    api.view(INVENTORY_API_PREFIX + "/item-groups", methods=["GET", "POST"], status_code=200, tags=tag)(ItemGroupCollection)
    api.view(
        INVENTORY_API_PREFIX + "/item-groups/{itms_grp_cod}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(ItemGroupDetail)
    api.view(INVENTORY_API_PREFIX + "/items", methods=["GET", "POST"], status_code=200, tags=tag)(ItemCollection)
    api.view(INVENTORY_API_PREFIX + "/items/{item_code}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        ItemDetail
    )
    api.view(INVENTORY_API_PREFIX + "/item-warehouse-stock", methods=["GET", "POST"], status_code=200, tags=tag)(ItemWarehouseStockCollection)
    api.view(
        INVENTORY_API_PREFIX + "/item-warehouse-stock/{item_code}/{whs_code}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(ItemWarehouseStockDetail)
    api.view(INVENTORY_API_PREFIX + "/units-of-measure", methods=["GET", "POST"], status_code=200, tags=tag)(UnitOfMeasureCollection)
    api.view(
        INVENTORY_API_PREFIX + "/units-of-measure/{uom_entry}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(UnitOfMeasureDetail)
    api.view(INVENTORY_API_PREFIX + "/stock-transfer-requests", methods=["GET", "POST"], status_code=200, tags=tag)(StockTransferRequestCollection)
    api.view(
        INVENTORY_API_PREFIX + "/stock-transfer-requests/{doc_entry}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(StockTransferRequestDetail)
    api.view(
        INVENTORY_API_PREFIX + "/stock-transfer-request-lines",
        methods=["GET", "POST"],
        status_code=200,
        tags=tag,
    )(StockTransferRequestLineCollection)
    api.view(
        INVENTORY_API_PREFIX + "/stock-transfer-request-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(StockTransferRequestLineDetail)
    api.view(INVENTORY_API_PREFIX + "/stock-transfers", methods=["GET", "POST"], status_code=200, tags=tag)(StockTransferCollection)
    api.view(
        INVENTORY_API_PREFIX + "/stock-transfers/{doc_entry}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(StockTransferDetail)
    api.view(INVENTORY_API_PREFIX + "/stock-transfer-lines", methods=["GET", "POST"], status_code=200, tags=tag)(StockTransferLineCollection)
    api.view(
        INVENTORY_API_PREFIX + "/stock-transfer-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(StockTransferLineDetail)
    api.view(INVENTORY_API_PREFIX + "/goods-receipts", methods=["GET", "POST"], status_code=200, tags=tag)(InventoryGoodsReceiptCollection)
    api.view(
        INVENTORY_API_PREFIX + "/goods-receipts/{doc_entry}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(InventoryGoodsReceiptDetail)
    api.view(INVENTORY_API_PREFIX + "/goods-receipt-lines", methods=["GET", "POST"], status_code=200, tags=tag)(InventoryGoodsReceiptLineCollection)
    api.view(
        INVENTORY_API_PREFIX + "/goods-receipt-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(InventoryGoodsReceiptLineDetail)
    api.view(INVENTORY_API_PREFIX + "/goods-issues", methods=["GET", "POST"], status_code=200, tags=tag)(InventoryGoodsIssueCollection)
    api.view(
        INVENTORY_API_PREFIX + "/goods-issues/{doc_entry}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(InventoryGoodsIssueDetail)
    api.view(INVENTORY_API_PREFIX + "/goods-issue-lines", methods=["GET", "POST"], status_code=200, tags=tag)(InventoryGoodsIssueLineCollection)
    api.view(
        INVENTORY_API_PREFIX + "/goods-issue-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(InventoryGoodsIssueLineDetail)
    api.view(INVENTORY_API_PREFIX + "/stock-takes", methods=["GET", "POST"], status_code=200, tags=tag)(StockTakeCollection)
    api.view(
        INVENTORY_API_PREFIX + "/stock-takes/{doc_entry}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(StockTakeDetail)
    api.view(INVENTORY_API_PREFIX + "/stock-take-lines", methods=["GET", "POST"], status_code=200, tags=tag)(StockTakeLineCollection)
    api.view(
        INVENTORY_API_PREFIX + "/stock-take-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(StockTakeLineDetail)
    api.view(INVENTORY_API_PREFIX + "/inventory-postings", methods=["GET", "POST"], status_code=200, tags=tag)(InventoryPostingCollection)
    api.view(
        INVENTORY_API_PREFIX + "/inventory-postings/{trans_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(InventoryPostingDetail)
    api.view(INVENTORY_API_PREFIX + "/oitb", methods=["GET", "POST"], status_code=200, tags=tag)(ItemGroupCollection)
    api.view(INVENTORY_API_PREFIX + "/oitb/{itms_grp_cod}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        ItemGroupDetail
    )
    api.view(INVENTORY_API_PREFIX + "/oitm", methods=["GET", "POST"], status_code=200, tags=tag)(ItemCollection)
    api.view(INVENTORY_API_PREFIX + "/oitm/{item_code}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        ItemDetail
    )
    api.view(INVENTORY_API_PREFIX + "/oitw", methods=["GET", "POST"], status_code=200, tags=tag)(ItemWarehouseStockCollection)
    api.view(INVENTORY_API_PREFIX + "/oitw/{item_code}/{whs_code}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        ItemWarehouseStockDetail
    )
    api.view(INVENTORY_API_PREFIX + "/ouom", methods=["GET", "POST"], status_code=200, tags=tag)(UnitOfMeasureCollection)
    api.view(INVENTORY_API_PREFIX + "/ouom/{uom_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        UnitOfMeasureDetail
    )
    api.view(INVENTORY_API_PREFIX + "/owtq", methods=["GET", "POST"], status_code=200, tags=tag)(StockTransferRequestCollection)
    api.view(INVENTORY_API_PREFIX + "/owtq/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        StockTransferRequestDetail
    )
    api.view(INVENTORY_API_PREFIX + "/wtq1", methods=["GET", "POST"], status_code=200, tags=tag)(StockTransferRequestLineCollection)
    api.view(INVENTORY_API_PREFIX + "/wtq1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        StockTransferRequestLineDetail
    )
    api.view(INVENTORY_API_PREFIX + "/owtr", methods=["GET", "POST"], status_code=200, tags=tag)(StockTransferCollection)
    api.view(INVENTORY_API_PREFIX + "/owtr/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        StockTransferDetail
    )
    api.view(INVENTORY_API_PREFIX + "/wtr1", methods=["GET", "POST"], status_code=200, tags=tag)(StockTransferLineCollection)
    api.view(INVENTORY_API_PREFIX + "/wtr1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        StockTransferLineDetail
    )
    api.view(INVENTORY_API_PREFIX + "/oign", methods=["GET", "POST"], status_code=200, tags=tag)(InventoryGoodsReceiptCollection)
    api.view(INVENTORY_API_PREFIX + "/oign/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        InventoryGoodsReceiptDetail
    )
    api.view(INVENTORY_API_PREFIX + "/ign1", methods=["GET", "POST"], status_code=200, tags=tag)(InventoryGoodsReceiptLineCollection)
    api.view(INVENTORY_API_PREFIX + "/ign1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        InventoryGoodsReceiptLineDetail
    )
    api.view(INVENTORY_API_PREFIX + "/oige", methods=["GET", "POST"], status_code=200, tags=tag)(InventoryGoodsIssueCollection)
    api.view(INVENTORY_API_PREFIX + "/oige/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        InventoryGoodsIssueDetail
    )
    api.view(INVENTORY_API_PREFIX + "/ige1", methods=["GET", "POST"], status_code=200, tags=tag)(InventoryGoodsIssueLineCollection)
    api.view(INVENTORY_API_PREFIX + "/ige1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        InventoryGoodsIssueLineDetail
    )
    api.view(INVENTORY_API_PREFIX + "/oinc", methods=["GET", "POST"], status_code=200, tags=tag)(StockTakeCollection)
    api.view(INVENTORY_API_PREFIX + "/oinc/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        StockTakeDetail
    )
    api.view(INVENTORY_API_PREFIX + "/inc1", methods=["GET", "POST"], status_code=200, tags=tag)(StockTakeLineCollection)
    api.view(INVENTORY_API_PREFIX + "/inc1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        StockTakeLineDetail
    )
    api.view(INVENTORY_API_PREFIX + "/oinm", methods=["GET", "POST"], status_code=200, tags=tag)(InventoryPostingCollection)
    api.view(INVENTORY_API_PREFIX + "/oinm/{trans_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        InventoryPostingDetail
    )
