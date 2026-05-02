"""
Production Bolt API — BOM (``OITT``/``ITT1``), প্রোডাকশন অর্ডার (``OWOR``/``WOR1``)।

``django_bolt_guide.md``: ``APIView``, ``BadRequest`` / ``NotFound``। সিরিয়ালাইজার: ``serializers.py``।
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated

from asgiref.sync import sync_to_async
from django.db import IntegrityError
from django.db.models import Q
from django_bolt import BoltAPI
from django_bolt.auth import IsAuthenticated, JWTAuthentication
from django_bolt.exceptions import BadRequest, NotFound
from django_bolt.views import APIView

from apps.production.models import ITT1, OITT, OWOR, WOR1

from .serializers import (
    BomHeaderCreateBody,
    BomHeaderPage,
    BomHeaderPatchBody,
    BomHeaderResponse,
    BomLineCreateBody,
    BomLinePage,
    BomLinePatchBody,
    BomLineResponse,
    ProductionOrderCreateBody,
    ProductionOrderLineCreateBody,
    ProductionOrderLinePage,
    ProductionOrderLinePatchBody,
    ProductionOrderLineResponse,
    ProductionOrderPage,
    ProductionOrderPatchBody,
    ProductionOrderResponse,
)


PRODUCTION_API_PREFIX = "/api/production"


class BomHeaderCollection(APIView):
    """BOM header (OITT): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> BomHeaderPage:
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
        queryset = OITT.objects.all().order_by("Code")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N")
        if search_prefix:
            queryset = queryset.filter(Code__istartswith=search_prefix)
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return BomHeaderPage(
            items=[
                BomHeaderResponse(
                    Code=o.Code,
                    TreeType=o.TreeType,
                    Quantity=str(o.Quantity),
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: BomHeaderCreateBody) -> BomHeaderResponse:
        tt = (data.TreeType or "P").strip().upper()[:1] or "P"
        if tt not in ("P", "S", "A", "T"):
            raise BadRequest(detail="TreeType must be P, S, A, or T.")
        header = OITT(
            Code=data.Code.strip(),
            TreeType=tt,
            Quantity=Decimal(str(data.Quantity or "1")),
        )
        try:
            await header.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate Code or invalid BOM header.")
        return BomHeaderResponse(
            Code=header.Code,
            TreeType=header.TreeType,
            Quantity=str(header.Quantity),
            Canceled=header.Canceled,
        )


class BomHeaderDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, code: str) -> BomHeaderResponse:
        try:
            o = await OITT.objects.aget(pk=code.strip())
        except OITT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return BomHeaderResponse(
            Code=o.Code,
            TreeType=o.TreeType,
            Quantity=str(o.Quantity),
            Canceled=o.Canceled,
        )

    async def patch(self, code: str, data: BomHeaderPatchBody) -> BomHeaderResponse:
        try:
            o = await OITT.objects.aget(pk=code.strip())
        except OITT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.TreeType is not None:
            tt = (data.TreeType or "P").strip().upper()[:1] or "P"
            if tt not in ("P", "S", "A", "T"):
                raise BadRequest(detail="TreeType must be P, S, A, or T.")
            o.TreeType = tt
        if data.Quantity is not None:
            o.Quantity = Decimal(str(data.Quantity))
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return BomHeaderResponse(
            Code=o.Code,
            TreeType=o.TreeType,
            Quantity=str(o.Quantity),
            Canceled=o.Canceled,
        )

    async def delete(self, code: str) -> BomHeaderResponse:
        try:
            o = await OITT.objects.aget(pk=code.strip())
        except OITT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return BomHeaderResponse(
            Code=o.Code,
            TreeType=o.TreeType,
            Quantity=str(o.Quantity),
            Canceled=o.Canceled,
        )


class BomLineCollection(APIView):
    """BOM lines (ITT1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> BomLinePage:
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
        qd_f = getattr(self.request, "query", None) or {}
        father = (qd_f.get("father") or "").strip() or None
        queryset = ITT1.objects.all().order_by("header_id", "LineNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N", header__Canceled="N")
        if father is not None:
            queryset = queryset.filter(header_id=father.strip())
        if search_prefix:
            queryset = queryset.filter(
                Q(ItemCode__istartswith=search_prefix) | Q(WhsCode__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return BomLinePage(
            items=[
                BomLineResponse(
                    Father=o.header_id,
                    LineNum=o.LineNum,
                    ItemCode=o.ItemCode,
                    Quantity=str(o.Quantity),
                    WhsCode=o.WhsCode,
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: BomLineCreateBody) -> BomLineResponse:
        hdr = await OITT.objects.filter(pk=data.Father.strip()).afirst()
        if not hdr:
            raise BadRequest(detail="Invalid Father (OITT.Code).")
        if hdr.Canceled == "Y":
            raise BadRequest(detail="Cannot add lines to a canceled BOM.")
        line = ITT1(
            header_id=data.Father.strip(),
            LineNum=int(data.LineNum),
            ItemCode=data.ItemCode.strip(),
            Quantity=Decimal(str(data.Quantity)),
            WhsCode=data.WhsCode.strip(),
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid Father.")
        return BomLineResponse(
            Father=line.header_id,
            LineNum=line.LineNum,
            ItemCode=line.ItemCode,
            Quantity=str(line.Quantity),
            WhsCode=line.WhsCode,
            Canceled=line.Canceled,
        )


class BomLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, father: str, line_num: int) -> BomLineResponse:
        try:
            o = await ITT1.objects.select_related("header").aget(header_id=father.strip(), LineNum=int(line_num))
        except ITT1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return BomLineResponse(
            Father=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            Canceled=o.Canceled,
        )

    async def patch(self, father: str, line_num: int, data: BomLinePatchBody) -> BomLineResponse:
        try:
            o = await ITT1.objects.select_related("header").aget(header_id=father.strip(), LineNum=int(line_num))
        except ITT1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if o.header.Canceled == "Y":
            raise BadRequest(detail="Cannot edit lines of a canceled BOM.")
        if data.ItemCode is not None:
            o.ItemCode = data.ItemCode.strip()
        if data.Quantity is not None:
            o.Quantity = Decimal(str(data.Quantity))
        if data.WhsCode is not None:
            o.WhsCode = data.WhsCode.strip()
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return BomLineResponse(
            Father=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            Canceled=o.Canceled,
        )

    async def delete(self, father: str, line_num: int) -> BomLineResponse:
        try:
            o = await ITT1.objects.select_related("header").aget(header_id=father.strip(), LineNum=int(line_num))
        except ITT1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if o.header.Canceled == "Y":
            raise BadRequest(detail="Cannot delete lines of a canceled BOM.")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return BomLineResponse(
            Father=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            Canceled=o.Canceled,
        )


class ProductionOrderCollection(APIView):
    """Production order header (OWOR): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> ProductionOrderPage:
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
        queryset = OWOR.objects.all().order_by("-DocEntry")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N")
        if search_prefix:
            queryset = queryset.filter(ItemCode__istartswith=search_prefix)
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return ProductionOrderPage(
            items=[
                ProductionOrderResponse(
                    DocEntry=o.DocEntry,
                    DocNum=o.DocNum,
                    ItemCode=o.ItemCode,
                    Status=o.Status,
                    PlannedQty=str(o.PlannedQty),
                    CmpltQty=str(o.CmpltQty),
                    PostDate=o.PostDate,
                    WhsCode=o.WhsCode,
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: ProductionOrderCreateBody) -> ProductionOrderResponse:
        st = (data.Status or "P").strip().upper()[:1] or "P"
        if st not in ("P", "R", "L"):
            raise BadRequest(detail="Status must be P, R, or L.")
        header = OWOR(
            DocNum=data.DocNum,
            ItemCode=data.ItemCode.strip(),
            Status=st,
            PlannedQty=Decimal(str(data.PlannedQty)),
            CmpltQty=Decimal(str(data.CmpltQty or "0")),
            PostDate=data.PostDate,
            WhsCode=data.WhsCode.strip(),
        )
        await header.asave()
        return ProductionOrderResponse(
            DocEntry=header.DocEntry,
            DocNum=header.DocNum,
            ItemCode=header.ItemCode,
            Status=header.Status,
            PlannedQty=str(header.PlannedQty),
            CmpltQty=str(header.CmpltQty),
            PostDate=header.PostDate,
            WhsCode=header.WhsCode,
            Canceled=header.Canceled,
        )


class ProductionOrderDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> ProductionOrderResponse:
        try:
            o = await OWOR.objects.aget(pk=doc_entry)
        except OWOR.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return ProductionOrderResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            ItemCode=o.ItemCode,
            Status=o.Status,
            PlannedQty=str(o.PlannedQty),
            CmpltQty=str(o.CmpltQty),
            PostDate=o.PostDate,
            WhsCode=o.WhsCode,
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, data: ProductionOrderPatchBody) -> ProductionOrderResponse:
        try:
            o = await OWOR.objects.aget(pk=doc_entry)
        except OWOR.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.DocNum is not None:
            o.DocNum = data.DocNum
        if data.ItemCode is not None:
            o.ItemCode = data.ItemCode.strip()
        if data.Status is not None:
            st = (data.Status or "P").strip().upper()[:1] or "P"
            if st not in ("P", "R", "L"):
                raise BadRequest(detail="Status must be P, R, or L.")
            o.Status = st
        if data.PlannedQty is not None:
            o.PlannedQty = Decimal(str(data.PlannedQty))
        if data.CmpltQty is not None:
            o.CmpltQty = Decimal(str(data.CmpltQty))
        if data.PostDate is not None:
            o.PostDate = data.PostDate
        if data.WhsCode is not None:
            o.WhsCode = data.WhsCode.strip()
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return ProductionOrderResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            ItemCode=o.ItemCode,
            Status=o.Status,
            PlannedQty=str(o.PlannedQty),
            CmpltQty=str(o.CmpltQty),
            PostDate=o.PostDate,
            WhsCode=o.WhsCode,
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int) -> ProductionOrderResponse:
        try:
            o = await OWOR.objects.aget(pk=doc_entry)
        except OWOR.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return ProductionOrderResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            ItemCode=o.ItemCode,
            Status=o.Status,
            PlannedQty=str(o.PlannedQty),
            CmpltQty=str(o.CmpltQty),
            PostDate=o.PostDate,
            WhsCode=o.WhsCode,
            Canceled=o.Canceled,
        )


class ProductionOrderLineCollection(APIView):
    """Production order lines (WOR1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> ProductionOrderLinePage:
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
        qd2 = getattr(self.request, "query", None) or {}
        raw_de = (qd2.get("doc_entry") or "").strip()
        doc_entry = int(raw_de) if raw_de else None
        queryset = WOR1.objects.all().order_by("header_id", "LineNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N", header__Canceled="N")
        if doc_entry is not None:
            queryset = queryset.filter(header_id=doc_entry)
        if search_prefix:
            queryset = queryset.filter(Q(ItemCode__istartswith=search_prefix) | Q(WhsCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return ProductionOrderLinePage(
            items=[
                ProductionOrderLineResponse(
                    DocEntry=o.header_id,
                    LineNum=o.LineNum,
                    ItemCode=o.ItemCode,
                    PlannedQty=str(o.PlannedQty),
                    IssuedQty=str(o.IssuedQty),
                    WhsCode=o.WhsCode,
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: ProductionOrderLineCreateBody) -> ProductionOrderLineResponse:
        hdr = await OWOR.objects.filter(pk=data.DocEntry).afirst()
        if not hdr:
            raise BadRequest(detail="Invalid DocEntry (OWOR).")
        if hdr.Canceled == "Y":
            raise BadRequest(detail="Cannot add lines to a canceled document.")
        line = WOR1(
            header_id=data.DocEntry,
            LineNum=int(data.LineNum),
            ItemCode=data.ItemCode.strip(),
            PlannedQty=Decimal(str(data.PlannedQty)),
            IssuedQty=Decimal(str(data.IssuedQty or "0")),
            WhsCode=data.WhsCode.strip(),
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        return ProductionOrderLineResponse(
            DocEntry=line.header_id,
            LineNum=line.LineNum,
            ItemCode=line.ItemCode,
            PlannedQty=str(line.PlannedQty),
            IssuedQty=str(line.IssuedQty),
            WhsCode=line.WhsCode,
            Canceled=line.Canceled,
        )


class ProductionOrderLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> ProductionOrderLineResponse:
        try:
            o = await WOR1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except WOR1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return ProductionOrderLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            PlannedQty=str(o.PlannedQty),
            IssuedQty=str(o.IssuedQty),
            WhsCode=o.WhsCode,
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, line_num: int, data: ProductionOrderLinePatchBody) -> ProductionOrderLineResponse:
        try:
            o = await WOR1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except WOR1.DoesNotExist:
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
        if data.PlannedQty is not None:
            o.PlannedQty = Decimal(str(data.PlannedQty))
        if data.IssuedQty is not None:
            o.IssuedQty = Decimal(str(data.IssuedQty))
        if data.WhsCode is not None:
            o.WhsCode = data.WhsCode.strip()
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return ProductionOrderLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            PlannedQty=str(o.PlannedQty),
            IssuedQty=str(o.IssuedQty),
            WhsCode=o.WhsCode,
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int, line_num: int) -> ProductionOrderLineResponse:
        try:
            o = await WOR1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except WOR1.DoesNotExist:
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
        return ProductionOrderLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            PlannedQty=str(o.PlannedQty),
            IssuedQty=str(o.IssuedQty),
            WhsCode=o.WhsCode,
            Canceled=o.Canceled,
        )


def attach_production_routes(api: BoltAPI) -> None:
    """Register Production Bolt routes under ``/api/production``."""
    tag = ["production"]
    # Human-readable paths (legacy SAP table names kept for compatibility).
    api.view(PRODUCTION_API_PREFIX + "/bom-headers", methods=["GET", "POST"], status_code=200, tags=tag)(BomHeaderCollection)
    api.view(PRODUCTION_API_PREFIX + "/bom-headers/{code}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        BomHeaderDetail
    )
    api.view(PRODUCTION_API_PREFIX + "/bom-lines", methods=["GET", "POST"], status_code=200, tags=tag)(BomLineCollection)
    api.view(
        PRODUCTION_API_PREFIX + "/bom-lines/{father}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(BomLineDetail)
    api.view(PRODUCTION_API_PREFIX + "/production-orders", methods=["GET", "POST"], status_code=200, tags=tag)(ProductionOrderCollection)
    api.view(
        PRODUCTION_API_PREFIX + "/production-orders/{doc_entry}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(ProductionOrderDetail)
    api.view(PRODUCTION_API_PREFIX + "/production-order-lines", methods=["GET", "POST"], status_code=200, tags=tag)(ProductionOrderLineCollection)
    api.view(
        PRODUCTION_API_PREFIX + "/production-order-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(ProductionOrderLineDetail)
    api.view(PRODUCTION_API_PREFIX + "/oitt", methods=["GET", "POST"], status_code=200, tags=tag)(BomHeaderCollection)
    api.view(PRODUCTION_API_PREFIX + "/oitt/{code}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        BomHeaderDetail
    )
    api.view(PRODUCTION_API_PREFIX + "/itt1", methods=["GET", "POST"], status_code=200, tags=tag)(BomLineCollection)
    api.view(PRODUCTION_API_PREFIX + "/itt1/{father}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        BomLineDetail
    )
    api.view(PRODUCTION_API_PREFIX + "/owor", methods=["GET", "POST"], status_code=200, tags=tag)(ProductionOrderCollection)
    api.view(PRODUCTION_API_PREFIX + "/owor/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        ProductionOrderDetail
    )
    api.view(PRODUCTION_API_PREFIX + "/wor1", methods=["GET", "POST"], status_code=200, tags=tag)(ProductionOrderLineCollection)
    api.view(PRODUCTION_API_PREFIX + "/wor1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        ProductionOrderLineDetail
    )
