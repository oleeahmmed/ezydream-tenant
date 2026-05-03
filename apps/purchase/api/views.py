"""
Purchase Bolt API — ভিউ (``django_bolt_guide.md``: ``APIView``, ``BadRequest`` / ``NotFound``)।

সিরিয়ালাইজার: ``serializers.py``। কোনো ``bolt_tools`` নেই।
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from django_bolt import BoltAPI
from django_bolt.auth import IsAuthenticated, JWTAuthentication
from django_bolt.exceptions import BadRequest, NotFound
from django_bolt.views import APIView

from apps.businesspartner.services.bp_rollups import recalculate_bp_rollups
from apps.finance.services.auto_journal import sync_ap_invoice_journal
from apps.inventory.services import (
    rebuild_oitw_committed_and_on_order,
    resync_all_grpo_lines,
    resync_all_vendor_return_lines,
    sync_grpo_line_stock,
    sync_vendor_return_line_stock,
)
from apps.purchase.models import OPCH, OPDN, OPOR, OPRQ, ORPC, PCH1, PDN1, POR1, PRQ1, RPC1

from .serializers import (
    ApInvoiceCreateBody,
    ApInvoiceLineCreateBody,
    ApInvoiceLinePage,
    ApInvoiceLinePatchBody,
    ApInvoiceLineResponse,
    ApInvoicePage,
    ApInvoicePatchBody,
    ApInvoiceResponse,
    GoodsReceiptCreateBody,
    GoodsReceiptLineCreateBody,
    GoodsReceiptLinePage,
    GoodsReceiptLinePatchBody,
    GoodsReceiptLineResponse,
    GoodsReceiptPage,
    GoodsReceiptPatchBody,
    GoodsReceiptResponse,
    PurchaseOrderCreateBody,
    PurchaseOrderLineCreateBody,
    PurchaseOrderLinePage,
    PurchaseOrderLinePatchBody,
    PurchaseOrderLineResponse,
    PurchaseOrderPage,
    PurchaseOrderPatchBody,
    PurchaseOrderResponse,
    PurchaseRequestCreateBody,
    PurchaseRequestLineCreateBody,
    PurchaseRequestLinePage,
    PurchaseRequestLinePatchBody,
    PurchaseRequestLineResponse,
    PurchaseRequestPage,
    PurchaseRequestPatchBody,
    PurchaseRequestResponse,
    VendorReturnCreateBody,
    VendorReturnLineCreateBody,
    VendorReturnLinePage,
    VendorReturnLinePatchBody,
    VendorReturnLineResponse,
    VendorReturnPage,
    VendorReturnPatchBody,
    VendorReturnResponse,
)


PURCHASE_API_PREFIX = "/api/purchase"


async def _bp_recalc_cards(*card_codes: str | None) -> None:
    for cc in card_codes:
        s = (cc or "").strip()
        if s:
            await sync_to_async(recalculate_bp_rollups)(s)


async def _purchase_stock_sync(fn, *args) -> None:
    try:
        await sync_to_async(fn)(*args)
    except ValidationError as exc:
        msgs = list(getattr(exc, "messages", []))
        detail = "; ".join(str(m) for m in msgs) if msgs else str(exc)
        raise BadRequest(detail=detail) from exc


async def _rebuild_inv_totals() -> None:
    await sync_to_async(rebuild_oitw_committed_and_on_order)()


class PurchaseRequestCollection(APIView):
    """Purchase request header (OPRQ): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> PurchaseRequestPage:
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
        queryset = OPRQ.objects.all().order_by("-DocEntry")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N")
        if search_prefix:
            q = Q(Requester__istartswith=search_prefix)
            if search_prefix.isdigit():
                q |= Q(DocNum=int(search_prefix))
            queryset = queryset.filter(q)
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return PurchaseRequestPage(
            items=[
                PurchaseRequestResponse(
                    DocEntry=o.DocEntry,
                    DocNum=o.DocNum,
                    DocStatus=o.DocStatus,
                    Requester=o.Requester,
                    DocDate=o.DocDate,
                    DocDueDate=o.DocDueDate,
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: PurchaseRequestCreateBody) -> PurchaseRequestResponse:
        status = (data.DocStatus or "O").strip().upper()[:1] or "O"
        if status not in ("O", "C"):
            raise BadRequest(detail="DocStatus must be O or C.")
        header = OPRQ(
            DocNum=data.DocNum,
            DocStatus=status,
            Requester=data.Requester.strip(),
            DocDate=data.DocDate,
            DocDueDate=data.DocDueDate,
        )
        await header.asave()
        return PurchaseRequestResponse(
            DocEntry=header.DocEntry,
            DocNum=header.DocNum,
            DocStatus=header.DocStatus,
            Requester=header.Requester,
            DocDate=header.DocDate,
            DocDueDate=header.DocDueDate,
            Canceled=header.Canceled,
        )


class PurchaseRequestDetail(APIView):
    """Single purchase request header: GET / PATCH / DELETE (soft ``Canceled='Y'``)."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> PurchaseRequestResponse:
        try:
            o = await OPRQ.objects.aget(pk=doc_entry)
        except OPRQ.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return PurchaseRequestResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocStatus=o.DocStatus,
            Requester=o.Requester,
            DocDate=o.DocDate,
            DocDueDate=o.DocDueDate,
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, data: PurchaseRequestPatchBody) -> PurchaseRequestResponse:
        try:
            o = await OPRQ.objects.aget(pk=doc_entry)
        except OPRQ.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.DocNum is not None:
            o.DocNum = data.DocNum
        if data.DocStatus is not None:
            st = (data.DocStatus or "O").strip().upper()[:1] or "O"
            if st not in ("O", "C"):
                raise BadRequest(detail="DocStatus must be O or C.")
            o.DocStatus = st
        if data.Requester is not None:
            o.Requester = data.Requester.strip()
        if data.DocDate is not None:
            o.DocDate = data.DocDate
        if data.DocDueDate is not None:
            o.DocDueDate = data.DocDueDate
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return PurchaseRequestResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocStatus=o.DocStatus,
            Requester=o.Requester,
            DocDate=o.DocDate,
            DocDueDate=o.DocDueDate,
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int) -> PurchaseRequestResponse:
        try:
            o = await OPRQ.objects.aget(pk=doc_entry)
        except OPRQ.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return PurchaseRequestResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            DocStatus=o.DocStatus,
            Requester=o.Requester,
            DocDate=o.DocDate,
            DocDueDate=o.DocDueDate,
            Canceled=o.Canceled,
        )


class PurchaseRequestLineCollection(APIView):
    """Purchase request lines (PRQ1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> PurchaseRequestLinePage:
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
        queryset = PRQ1.objects.all().order_by("header_id", "LineNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N", header__Canceled="N")
        if doc_entry is not None:
            queryset = queryset.filter(header_id=doc_entry)
        if search_prefix:
            queryset = queryset.filter(
                Q(ItemCode__istartswith=search_prefix) | Q(Dscription__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return PurchaseRequestLinePage(
            items=[
                PurchaseRequestLineResponse(
                    DocEntry=o.header_id,
                    LineNum=o.LineNum,
                    ItemCode=o.ItemCode,
                    Dscription=o.Dscription or "",
                    Quantity=str(o.Quantity),
                    WhsCode=o.WhsCode,
                    LineStatus=o.LineStatus,
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: PurchaseRequestLineCreateBody) -> PurchaseRequestLineResponse:
        hdr = await OPRQ.objects.filter(pk=data.DocEntry).afirst()
        if not hdr:
            raise BadRequest(detail="Invalid DocEntry (OPRQ).")
        if hdr.Canceled == "Y":
            raise BadRequest(detail="Cannot add lines to a canceled document.")
        ls = (data.LineStatus or "O").strip().upper()[:1] or "O"
        if ls not in ("O", "C"):
            raise BadRequest(detail="LineStatus must be O or C.")
        line = PRQ1(
            header_id=data.DocEntry,
            LineNum=int(data.LineNum),
            ItemCode=data.ItemCode.strip(),
            Dscription=(data.Dscription or "").strip(),
            Quantity=Decimal(str(data.Quantity)),
            WhsCode=data.WhsCode.strip(),
            LineStatus=ls,
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        return PurchaseRequestLineResponse(
            DocEntry=line.header_id,
            LineNum=line.LineNum,
            ItemCode=line.ItemCode,
            Dscription=line.Dscription or "",
            Quantity=str(line.Quantity),
            WhsCode=line.WhsCode,
            LineStatus=line.LineStatus,
            Canceled=line.Canceled,
        )


class PurchaseRequestLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> PurchaseRequestLineResponse:
        try:
            o = await PRQ1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except PRQ1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return PurchaseRequestLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Dscription=o.Dscription or "",
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            LineStatus=o.LineStatus,
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, line_num: int, data: PurchaseRequestLinePatchBody) -> PurchaseRequestLineResponse:
        try:
            o = await PRQ1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except PRQ1.DoesNotExist:
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
        if data.Dscription is not None:
            o.Dscription = data.Dscription.strip()
        if data.Quantity is not None:
            o.Quantity = Decimal(str(data.Quantity))
        if data.WhsCode is not None:
            o.WhsCode = data.WhsCode.strip()
        if data.LineStatus is not None:
            ls = (data.LineStatus or "O").strip().upper()[:1] or "O"
            if ls not in ("O", "C"):
                raise BadRequest(detail="LineStatus must be O or C.")
            o.LineStatus = ls
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return PurchaseRequestLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Dscription=o.Dscription or "",
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            LineStatus=o.LineStatus,
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int, line_num: int) -> PurchaseRequestLineResponse:
        try:
            o = await PRQ1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except PRQ1.DoesNotExist:
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
        return PurchaseRequestLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Dscription=o.Dscription or "",
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            LineStatus=o.LineStatus,
            Canceled=o.Canceled,
        )


class PurchaseOrderCollection(APIView):
    """Purchase order header (OPOR): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> PurchaseOrderPage:
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
        queryset = OPOR.objects.all().order_by("-DocEntry")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N")
        if search_prefix:
            queryset = queryset.filter(
                Q(CardCode__istartswith=search_prefix) | Q(CardName__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return PurchaseOrderPage(
            items=[
                PurchaseOrderResponse(
                    DocEntry=o.DocEntry,
                    DocNum=o.DocNum,
                    CardCode=o.CardCode,
                    CardName=o.CardName or "",
                    DocStatus=o.DocStatus,
                    DocDate=o.DocDate,
                    DocTotal=str(o.DocTotal),
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: PurchaseOrderCreateBody) -> PurchaseOrderResponse:
        status = (data.DocStatus or "O").strip().upper()[:1] or "O"
        if status not in ("O", "C"):
            raise BadRequest(detail="DocStatus must be O or C.")
        header = OPOR(
            DocNum=data.DocNum,
            CardCode=data.CardCode.strip(),
            CardName=(data.CardName or "").strip(),
            DocStatus=status,
            DocDate=data.DocDate,
            DocTotal=Decimal(str(data.DocTotal or "0")),
        )
        await header.asave()
        await _rebuild_inv_totals()
        await _bp_recalc_cards(header.CardCode)
        return PurchaseOrderResponse(
            DocEntry=header.DocEntry,
            DocNum=header.DocNum,
            CardCode=header.CardCode,
            CardName=header.CardName or "",
            DocStatus=header.DocStatus,
            DocDate=header.DocDate,
            DocTotal=str(header.DocTotal),
            Canceled=header.Canceled,
        )


class PurchaseOrderDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> PurchaseOrderResponse:
        try:
            o = await OPOR.objects.aget(pk=doc_entry)
        except OPOR.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return PurchaseOrderResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocStatus=o.DocStatus,
            DocDate=o.DocDate,
            DocTotal=str(o.DocTotal),
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, data: PurchaseOrderPatchBody) -> PurchaseOrderResponse:
        try:
            o = await OPOR.objects.aget(pk=doc_entry)
        except OPOR.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        old_cc = o.CardCode.strip()
        if data.DocNum is not None:
            o.DocNum = data.DocNum
        if data.CardCode is not None:
            o.CardCode = data.CardCode.strip()
        if data.CardName is not None:
            o.CardName = data.CardName.strip()
        if data.DocStatus is not None:
            st = (data.DocStatus or "O").strip().upper()[:1] or "O"
            if st not in ("O", "C"):
                raise BadRequest(detail="DocStatus must be O or C.")
            o.DocStatus = st
        if data.DocDate is not None:
            o.DocDate = data.DocDate
        if data.DocTotal is not None:
            o.DocTotal = Decimal(str(data.DocTotal))
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        await _rebuild_inv_totals()
        await _bp_recalc_cards(old_cc, o.CardCode)
        return PurchaseOrderResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocStatus=o.DocStatus,
            DocDate=o.DocDate,
            DocTotal=str(o.DocTotal),
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int) -> PurchaseOrderResponse:
        try:
            o = await OPOR.objects.aget(pk=doc_entry)
        except OPOR.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        old_cc = o.CardCode.strip()
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        await _rebuild_inv_totals()
        await _bp_recalc_cards(old_cc)
        return PurchaseOrderResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocStatus=o.DocStatus,
            DocDate=o.DocDate,
            DocTotal=str(o.DocTotal),
            Canceled=o.Canceled,
        )


class PurchaseOrderLineCollection(APIView):
    """Purchase order lines (POR1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> PurchaseOrderLinePage:
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
        queryset = POR1.objects.all().order_by("header_id", "LineNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N", header__Canceled="N")
        if doc_entry is not None:
            queryset = queryset.filter(header_id=doc_entry)
        if search_prefix:
            queryset = queryset.filter(Q(ItemCode__istartswith=search_prefix) | Q(WhsCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return PurchaseOrderLinePage(
            items=[
                PurchaseOrderLineResponse(
                    DocEntry=o.header_id,
                    LineNum=o.LineNum,
                    ItemCode=o.ItemCode,
                    Quantity=str(o.Quantity),
                    Price=str(o.Price),
                    WhsCode=o.WhsCode,
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

    async def post(self, data: PurchaseOrderLineCreateBody) -> PurchaseOrderLineResponse:
        hdr = await OPOR.objects.filter(pk=data.DocEntry).afirst()
        if not hdr:
            raise BadRequest(detail="Invalid DocEntry (OPOR).")
        if hdr.Canceled == "Y":
            raise BadRequest(detail="Cannot add lines to a canceled document.")
        line = POR1(
            header_id=data.DocEntry,
            LineNum=int(data.LineNum),
            ItemCode=data.ItemCode.strip(),
            Quantity=Decimal(str(data.Quantity)),
            Price=Decimal(str(data.Price or "0")),
            WhsCode=data.WhsCode.strip(),
            BaseType=data.BaseType,
            BaseEntry=data.BaseEntry,
            BaseLine=data.BaseLine,
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        await _rebuild_inv_totals()
        await _bp_recalc_cards(hdr.CardCode)
        return PurchaseOrderLineResponse(
            DocEntry=line.header_id,
            LineNum=line.LineNum,
            ItemCode=line.ItemCode,
            Quantity=str(line.Quantity),
            Price=str(line.Price),
            WhsCode=line.WhsCode,
            BaseType=line.BaseType,
            BaseEntry=line.BaseEntry,
            BaseLine=line.BaseLine,
            Canceled=line.Canceled,
        )


class PurchaseOrderLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> PurchaseOrderLineResponse:
        try:
            o = await POR1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except POR1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return PurchaseOrderLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            Price=str(o.Price),
            WhsCode=o.WhsCode,
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, line_num: int, data: PurchaseOrderLinePatchBody) -> PurchaseOrderLineResponse:
        try:
            o = await POR1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except POR1.DoesNotExist:
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
        if data.Price is not None:
            o.Price = Decimal(str(data.Price))
        if data.WhsCode is not None:
            o.WhsCode = data.WhsCode.strip()
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
        await _rebuild_inv_totals()
        await _bp_recalc_cards(o.header.CardCode)
        return PurchaseOrderLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            Price=str(o.Price),
            WhsCode=o.WhsCode,
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int, line_num: int) -> PurchaseOrderLineResponse:
        try:
            o = await POR1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except POR1.DoesNotExist:
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
        await _rebuild_inv_totals()
        await _bp_recalc_cards(o.header.CardCode)
        return PurchaseOrderLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            Price=str(o.Price),
            WhsCode=o.WhsCode,
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )


class GoodsReceiptCollection(APIView):
    """GRPO header (OPDN): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> GoodsReceiptPage:
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
        queryset = OPDN.objects.all().order_by("-DocEntry")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N")
        if search_prefix:
            queryset = queryset.filter(
                Q(CardCode__istartswith=search_prefix) | Q(CardName__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return GoodsReceiptPage(
            items=[
                GoodsReceiptResponse(
                    DocEntry=o.DocEntry,
                    DocNum=o.DocNum,
                    CardCode=o.CardCode,
                    CardName=o.CardName or "",
                    DocDate=o.DocDate,
                    DocStatus=o.DocStatus,
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: GoodsReceiptCreateBody) -> GoodsReceiptResponse:
        status = (data.DocStatus or "O").strip().upper()[:1] or "O"
        if status not in ("O", "C"):
            raise BadRequest(detail="DocStatus must be O or C.")
        header = OPDN(
            DocNum=data.DocNum,
            CardCode=data.CardCode.strip(),
            CardName=(data.CardName or "").strip(),
            DocDate=data.DocDate,
            DocStatus=status,
        )
        await header.asave()
        return GoodsReceiptResponse(
            DocEntry=header.DocEntry,
            DocNum=header.DocNum,
            CardCode=header.CardCode,
            CardName=header.CardName or "",
            DocDate=header.DocDate,
            DocStatus=header.DocStatus,
            Canceled=header.Canceled,
        )


class GoodsReceiptDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> GoodsReceiptResponse:
        try:
            o = await OPDN.objects.aget(pk=doc_entry)
        except OPDN.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return GoodsReceiptResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            DocStatus=o.DocStatus,
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, data: GoodsReceiptPatchBody) -> GoodsReceiptResponse:
        try:
            o = await OPDN.objects.aget(pk=doc_entry)
        except OPDN.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.DocNum is not None:
            o.DocNum = data.DocNum
        if data.CardCode is not None:
            o.CardCode = data.CardCode.strip()
        if data.CardName is not None:
            o.CardName = data.CardName.strip()
        if data.DocDate is not None:
            o.DocDate = data.DocDate
        if data.DocStatus is not None:
            st = (data.DocStatus or "O").strip().upper()[:1] or "O"
            if st not in ("O", "C"):
                raise BadRequest(detail="DocStatus must be O or C.")
            o.DocStatus = st
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        await _purchase_stock_sync(resync_all_grpo_lines, int(doc_entry))
        return GoodsReceiptResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            DocStatus=o.DocStatus,
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int) -> GoodsReceiptResponse:
        try:
            o = await OPDN.objects.aget(pk=doc_entry)
        except OPDN.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        await _purchase_stock_sync(resync_all_grpo_lines, int(doc_entry))
        return GoodsReceiptResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            DocStatus=o.DocStatus,
            Canceled=o.Canceled,
        )


class GoodsReceiptLineCollection(APIView):
    """GRPO lines (PDN1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> GoodsReceiptLinePage:
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
        queryset = PDN1.objects.all().order_by("header_id", "LineNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N", header__Canceled="N")
        if doc_entry is not None:
            queryset = queryset.filter(header_id=doc_entry)
        if search_prefix:
            queryset = queryset.filter(Q(ItemCode__istartswith=search_prefix) | Q(WhsCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return GoodsReceiptLinePage(
            items=[
                GoodsReceiptLineResponse(
                    DocEntry=o.header_id,
                    LineNum=o.LineNum,
                    ItemCode=o.ItemCode,
                    Quantity=str(o.Quantity),
                    Price=str(o.Price),
                    WhsCode=o.WhsCode,
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

    async def post(self, data: GoodsReceiptLineCreateBody) -> GoodsReceiptLineResponse:
        hdr = await OPDN.objects.filter(pk=data.DocEntry).afirst()
        if not hdr:
            raise BadRequest(detail="Invalid DocEntry (OPDN).")
        if hdr.Canceled == "Y":
            raise BadRequest(detail="Cannot add lines to a canceled document.")
        line = PDN1(
            header_id=data.DocEntry,
            LineNum=int(data.LineNum),
            ItemCode=data.ItemCode.strip(),
            Quantity=Decimal(str(data.Quantity)),
            Price=Decimal(str(data.Price or "0")),
            WhsCode=data.WhsCode.strip(),
            BaseType=data.BaseType,
            BaseEntry=data.BaseEntry,
            BaseLine=data.BaseLine,
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        await _purchase_stock_sync(sync_grpo_line_stock, int(line.header_id), int(line.LineNum))
        return GoodsReceiptLineResponse(
            DocEntry=line.header_id,
            LineNum=line.LineNum,
            ItemCode=line.ItemCode,
            Quantity=str(line.Quantity),
            Price=str(line.Price),
            WhsCode=line.WhsCode,
            BaseType=line.BaseType,
            BaseEntry=line.BaseEntry,
            BaseLine=line.BaseLine,
            Canceled=line.Canceled,
        )


class GoodsReceiptLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> GoodsReceiptLineResponse:
        try:
            o = await PDN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except PDN1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return GoodsReceiptLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            Price=str(o.Price),
            WhsCode=o.WhsCode,
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, line_num: int, data: GoodsReceiptLinePatchBody) -> GoodsReceiptLineResponse:
        try:
            o = await PDN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except PDN1.DoesNotExist:
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
        if data.Price is not None:
            o.Price = Decimal(str(data.Price))
        if data.WhsCode is not None:
            o.WhsCode = data.WhsCode.strip()
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
        await _purchase_stock_sync(sync_grpo_line_stock, int(doc_entry), int(line_num))
        return GoodsReceiptLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            Price=str(o.Price),
            WhsCode=o.WhsCode,
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int, line_num: int) -> GoodsReceiptLineResponse:
        try:
            o = await PDN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except PDN1.DoesNotExist:
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
        await _purchase_stock_sync(sync_grpo_line_stock, int(doc_entry), int(line_num))
        return GoodsReceiptLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            Price=str(o.Price),
            WhsCode=o.WhsCode,
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )


class VendorReturnCollection(APIView):
    """Goods return header (ORPC): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> VendorReturnPage:
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
        queryset = ORPC.objects.all().order_by("-DocEntry")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N")
        if search_prefix:
            queryset = queryset.filter(
                Q(CardCode__istartswith=search_prefix) | Q(CardName__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return VendorReturnPage(
            items=[
                VendorReturnResponse(
                    DocEntry=o.DocEntry,
                    DocNum=o.DocNum,
                    CardCode=o.CardCode,
                    CardName=o.CardName or "",
                    DocDate=o.DocDate,
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: VendorReturnCreateBody) -> VendorReturnResponse:
        header = ORPC(
            DocNum=data.DocNum,
            CardCode=data.CardCode.strip(),
            CardName=(data.CardName or "").strip(),
            DocDate=data.DocDate,
        )
        await header.asave()
        return VendorReturnResponse(
            DocEntry=header.DocEntry,
            DocNum=header.DocNum,
            CardCode=header.CardCode,
            CardName=header.CardName or "",
            DocDate=header.DocDate,
            Canceled=header.Canceled,
        )


class VendorReturnDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> VendorReturnResponse:
        try:
            o = await ORPC.objects.aget(pk=doc_entry)
        except ORPC.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return VendorReturnResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, data: VendorReturnPatchBody) -> VendorReturnResponse:
        try:
            o = await ORPC.objects.aget(pk=doc_entry)
        except ORPC.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.DocNum is not None:
            o.DocNum = data.DocNum
        if data.CardCode is not None:
            o.CardCode = data.CardCode.strip()
        if data.CardName is not None:
            o.CardName = data.CardName.strip()
        if data.DocDate is not None:
            o.DocDate = data.DocDate
        if data.DocStatus is not None:
            st = (data.DocStatus or "O").strip().upper()[:1] or "O"
            if st not in ("O", "C"):
                raise BadRequest(detail="DocStatus must be O or C.")
            o.DocStatus = st
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        await _purchase_stock_sync(resync_all_vendor_return_lines, int(doc_entry))
        return VendorReturnResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int) -> VendorReturnResponse:
        try:
            o = await ORPC.objects.aget(pk=doc_entry)
        except ORPC.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        await _purchase_stock_sync(resync_all_vendor_return_lines, int(doc_entry))
        return VendorReturnResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            Canceled=o.Canceled,
        )


class VendorReturnLineCollection(APIView):
    """Goods return lines (RPC1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> VendorReturnLinePage:
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
        queryset = RPC1.objects.all().order_by("header_id", "LineNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N", header__Canceled="N")
        if doc_entry is not None:
            queryset = queryset.filter(header_id=doc_entry)
        if search_prefix:
            queryset = queryset.filter(Q(ItemCode__istartswith=search_prefix) | Q(WhsCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return VendorReturnLinePage(
            items=[
                VendorReturnLineResponse(
                    DocEntry=o.header_id,
                    LineNum=o.LineNum,
                    ItemCode=o.ItemCode,
                    Quantity=str(o.Quantity),
                    Price=str(o.Price),
                    WhsCode=o.WhsCode,
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

    async def post(self, data: VendorReturnLineCreateBody) -> VendorReturnLineResponse:
        hdr = await ORPC.objects.filter(pk=data.DocEntry).afirst()
        if not hdr:
            raise BadRequest(detail="Invalid DocEntry (ORPC).")
        if hdr.Canceled == "Y":
            raise BadRequest(detail="Cannot add lines to a canceled document.")
        line = RPC1(
            header_id=data.DocEntry,
            LineNum=int(data.LineNum),
            ItemCode=data.ItemCode.strip(),
            Quantity=Decimal(str(data.Quantity)),
            Price=Decimal(str(data.Price or "0")),
            WhsCode=data.WhsCode.strip(),
            BaseType=data.BaseType,
            BaseEntry=data.BaseEntry,
            BaseLine=data.BaseLine,
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        await _purchase_stock_sync(sync_vendor_return_line_stock, int(line.header_id), int(line.LineNum))
        return VendorReturnLineResponse(
            DocEntry=line.header_id,
            LineNum=line.LineNum,
            ItemCode=line.ItemCode,
            Quantity=str(line.Quantity),
            Price=str(line.Price),
            WhsCode=line.WhsCode,
            BaseType=line.BaseType,
            BaseEntry=line.BaseEntry,
            BaseLine=line.BaseLine,
            Canceled=line.Canceled,
        )


class VendorReturnLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> VendorReturnLineResponse:
        try:
            o = await RPC1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RPC1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return VendorReturnLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            Price=str(o.Price),
            WhsCode=o.WhsCode,
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, line_num: int, data: VendorReturnLinePatchBody) -> VendorReturnLineResponse:
        try:
            o = await RPC1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RPC1.DoesNotExist:
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
        if data.Price is not None:
            o.Price = Decimal(str(data.Price))
        if data.WhsCode is not None:
            o.WhsCode = data.WhsCode.strip()
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
        await _purchase_stock_sync(sync_vendor_return_line_stock, int(doc_entry), int(line_num))
        return VendorReturnLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            Price=str(o.Price),
            WhsCode=o.WhsCode,
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int, line_num: int) -> VendorReturnLineResponse:
        try:
            o = await RPC1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RPC1.DoesNotExist:
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
        await _purchase_stock_sync(sync_vendor_return_line_stock, int(doc_entry), int(line_num))
        return VendorReturnLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            Price=str(o.Price),
            WhsCode=o.WhsCode,
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )


class ApInvoiceCollection(APIView):
    """A/P invoice header (OPCH): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> ApInvoicePage:
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
        queryset = OPCH.objects.all().order_by("-DocEntry")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N")
        if search_prefix:
            queryset = queryset.filter(
                Q(CardCode__istartswith=search_prefix) | Q(CardName__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return ApInvoicePage(
            items=[
                ApInvoiceResponse(
                    DocEntry=o.DocEntry,
                    DocNum=o.DocNum,
                    CardCode=o.CardCode,
                    CardName=o.CardName or "",
                    DocDate=o.DocDate,
                    DocTotal=str(o.DocTotal),
                    VatSum=str(o.VatSum),
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: ApInvoiceCreateBody) -> ApInvoiceResponse:
        header = OPCH(
            DocNum=data.DocNum,
            CardCode=data.CardCode.strip(),
            CardName=(data.CardName or "").strip(),
            DocDate=data.DocDate,
            DocTotal=Decimal(str(data.DocTotal or "0")),
            VatSum=Decimal(str(data.VatSum or "0")),
        )
        await header.asave()
        await _purchase_stock_sync(sync_ap_invoice_journal, int(header.DocEntry))
        return ApInvoiceResponse(
            DocEntry=header.DocEntry,
            DocNum=header.DocNum,
            CardCode=header.CardCode,
            CardName=header.CardName or "",
            DocDate=header.DocDate,
            DocTotal=str(header.DocTotal),
            VatSum=str(header.VatSum),
            Canceled=header.Canceled,
        )


class ApInvoiceDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> ApInvoiceResponse:
        try:
            o = await OPCH.objects.aget(pk=doc_entry)
        except OPCH.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return ApInvoiceResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            DocTotal=str(o.DocTotal),
            VatSum=str(o.VatSum),
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, data: ApInvoicePatchBody) -> ApInvoiceResponse:
        try:
            o = await OPCH.objects.aget(pk=doc_entry)
        except OPCH.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.DocNum is not None:
            o.DocNum = data.DocNum
        if data.CardCode is not None:
            o.CardCode = data.CardCode.strip()
        if data.CardName is not None:
            o.CardName = data.CardName.strip()
        if data.DocDate is not None:
            o.DocDate = data.DocDate
        if data.DocTotal is not None:
            o.DocTotal = Decimal(str(data.DocTotal))
        if data.VatSum is not None:
            o.VatSum = Decimal(str(data.VatSum))
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        await _purchase_stock_sync(sync_ap_invoice_journal, int(doc_entry))
        return ApInvoiceResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            DocTotal=str(o.DocTotal),
            VatSum=str(o.VatSum),
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int) -> ApInvoiceResponse:
        try:
            o = await OPCH.objects.aget(pk=doc_entry)
        except OPCH.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        await _purchase_stock_sync(sync_ap_invoice_journal, int(doc_entry))
        return ApInvoiceResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            DocTotal=str(o.DocTotal),
            VatSum=str(o.VatSum),
            Canceled=o.Canceled,
        )


class ApInvoiceLineCollection(APIView):
    """A/P invoice lines (PCH1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> ApInvoiceLinePage:
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
        queryset = PCH1.objects.all().order_by("header_id", "LineNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N", header__Canceled="N")
        if doc_entry is not None:
            queryset = queryset.filter(header_id=doc_entry)
        if search_prefix:
            queryset = queryset.filter(Q(ItemCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return ApInvoiceLinePage(
            items=[
                ApInvoiceLineResponse(
                    DocEntry=o.header_id,
                    LineNum=o.LineNum,
                    ItemCode=o.ItemCode,
                    Quantity=str(o.Quantity),
                    Price=str(o.Price),
                    LineTotal=str(o.LineTotal),
                    BaseType=o.BaseType,
                    BaseEntry=o.BaseEntry,
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: ApInvoiceLineCreateBody) -> ApInvoiceLineResponse:
        hdr = await OPCH.objects.filter(pk=data.DocEntry).afirst()
        if not hdr:
            raise BadRequest(detail="Invalid DocEntry (OPCH).")
        if hdr.Canceled == "Y":
            raise BadRequest(detail="Cannot add lines to a canceled document.")
        line = PCH1(
            header_id=data.DocEntry,
            LineNum=int(data.LineNum),
            ItemCode=data.ItemCode.strip(),
            Quantity=Decimal(str(data.Quantity)),
            Price=Decimal(str(data.Price or "0")),
            LineTotal=Decimal(str(data.LineTotal or "0")),
            BaseType=data.BaseType,
            BaseEntry=data.BaseEntry,
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        await _purchase_stock_sync(sync_ap_invoice_journal, int(line.header_id))
        return ApInvoiceLineResponse(
            DocEntry=line.header_id,
            LineNum=line.LineNum,
            ItemCode=line.ItemCode,
            Quantity=str(line.Quantity),
            Price=str(line.Price),
            LineTotal=str(line.LineTotal),
            BaseType=line.BaseType,
            BaseEntry=line.BaseEntry,
            Canceled=line.Canceled,
        )


class ApInvoiceLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> ApInvoiceLineResponse:
        try:
            o = await PCH1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except PCH1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return ApInvoiceLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            Price=str(o.Price),
            LineTotal=str(o.LineTotal),
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, line_num: int, data: ApInvoiceLinePatchBody) -> ApInvoiceLineResponse:
        try:
            o = await PCH1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except PCH1.DoesNotExist:
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
        if data.Price is not None:
            o.Price = Decimal(str(data.Price))
        if data.LineTotal is not None:
            o.LineTotal = Decimal(str(data.LineTotal))
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
        await _purchase_stock_sync(sync_ap_invoice_journal, int(doc_entry))
        return ApInvoiceLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            Price=str(o.Price),
            LineTotal=str(o.LineTotal),
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int, line_num: int) -> ApInvoiceLineResponse:
        try:
            o = await PCH1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except PCH1.DoesNotExist:
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
        await _purchase_stock_sync(sync_ap_invoice_journal, int(doc_entry))
        return ApInvoiceLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            Price=str(o.Price),
            LineTotal=str(o.LineTotal),
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            Canceled=o.Canceled,
        )


def attach_purchase_routes(api: BoltAPI) -> None:
    """Register Purchase A/P Bolt routes under ``/api/purchase``."""
    tag = ["purchase"]
    # Human-readable paths (legacy SAP-style paths kept for compatibility).
    api.view(PURCHASE_API_PREFIX + "/purchase-requests", methods=["GET", "POST"], status_code=200, tags=tag)(PurchaseRequestCollection)
    api.view(
        PURCHASE_API_PREFIX + "/purchase-requests/{doc_entry}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(PurchaseRequestDetail)
    api.view(PURCHASE_API_PREFIX + "/purchase-request-lines", methods=["GET", "POST"], status_code=200, tags=tag)(PurchaseRequestLineCollection)
    api.view(
        PURCHASE_API_PREFIX + "/purchase-request-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(PurchaseRequestLineDetail)
    api.view(PURCHASE_API_PREFIX + "/purchase-orders", methods=["GET", "POST"], status_code=200, tags=tag)(PurchaseOrderCollection)
    api.view(
        PURCHASE_API_PREFIX + "/purchase-orders/{doc_entry}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(PurchaseOrderDetail)
    api.view(PURCHASE_API_PREFIX + "/purchase-order-lines", methods=["GET", "POST"], status_code=200, tags=tag)(PurchaseOrderLineCollection)
    api.view(
        PURCHASE_API_PREFIX + "/purchase-order-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(PurchaseOrderLineDetail)
    api.view(PURCHASE_API_PREFIX + "/goods-receipts", methods=["GET", "POST"], status_code=200, tags=tag)(GoodsReceiptCollection)
    api.view(
        PURCHASE_API_PREFIX + "/goods-receipts/{doc_entry}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(GoodsReceiptDetail)
    api.view(PURCHASE_API_PREFIX + "/goods-receipt-lines", methods=["GET", "POST"], status_code=200, tags=tag)(GoodsReceiptLineCollection)
    api.view(
        PURCHASE_API_PREFIX + "/goods-receipt-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(GoodsReceiptLineDetail)
    api.view(PURCHASE_API_PREFIX + "/vendor-returns", methods=["GET", "POST"], status_code=200, tags=tag)(VendorReturnCollection)
    api.view(
        PURCHASE_API_PREFIX + "/vendor-returns/{doc_entry}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(VendorReturnDetail)
    api.view(PURCHASE_API_PREFIX + "/vendor-return-lines", methods=["GET", "POST"], status_code=200, tags=tag)(VendorReturnLineCollection)
    api.view(
        PURCHASE_API_PREFIX + "/vendor-return-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(VendorReturnLineDetail)
    api.view(PURCHASE_API_PREFIX + "/ap-invoices", methods=["GET", "POST"], status_code=200, tags=tag)(ApInvoiceCollection)
    api.view(
        PURCHASE_API_PREFIX + "/ap-invoices/{doc_entry}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(ApInvoiceDetail)
    api.view(PURCHASE_API_PREFIX + "/ap-invoice-lines", methods=["GET", "POST"], status_code=200, tags=tag)(ApInvoiceLineCollection)
    api.view(
        PURCHASE_API_PREFIX + "/ap-invoice-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(ApInvoiceLineDetail)
    api.view(PURCHASE_API_PREFIX + "/oprq", methods=["GET", "POST"], status_code=200, tags=tag)(PurchaseRequestCollection)
    api.view(PURCHASE_API_PREFIX + "/oprq/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        PurchaseRequestDetail
    )
    api.view(PURCHASE_API_PREFIX + "/prq1", methods=["GET", "POST"], status_code=200, tags=tag)(PurchaseRequestLineCollection)
    api.view(PURCHASE_API_PREFIX + "/prq1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        PurchaseRequestLineDetail
    )
    api.view(PURCHASE_API_PREFIX + "/opor", methods=["GET", "POST"], status_code=200, tags=tag)(PurchaseOrderCollection)
    api.view(PURCHASE_API_PREFIX + "/opor/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        PurchaseOrderDetail
    )
    api.view(PURCHASE_API_PREFIX + "/por1", methods=["GET", "POST"], status_code=200, tags=tag)(PurchaseOrderLineCollection)
    api.view(PURCHASE_API_PREFIX + "/por1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        PurchaseOrderLineDetail
    )
    api.view(PURCHASE_API_PREFIX + "/opdn", methods=["GET", "POST"], status_code=200, tags=tag)(GoodsReceiptCollection)
    api.view(PURCHASE_API_PREFIX + "/opdn/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        GoodsReceiptDetail
    )
    api.view(PURCHASE_API_PREFIX + "/pdn1", methods=["GET", "POST"], status_code=200, tags=tag)(GoodsReceiptLineCollection)
    api.view(PURCHASE_API_PREFIX + "/pdn1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        GoodsReceiptLineDetail
    )
    api.view(PURCHASE_API_PREFIX + "/orpc", methods=["GET", "POST"], status_code=200, tags=tag)(VendorReturnCollection)
    api.view(PURCHASE_API_PREFIX + "/orpc/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        VendorReturnDetail
    )
    api.view(PURCHASE_API_PREFIX + "/rpc1", methods=["GET", "POST"], status_code=200, tags=tag)(VendorReturnLineCollection)
    api.view(PURCHASE_API_PREFIX + "/rpc1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        VendorReturnLineDetail
    )
    api.view(PURCHASE_API_PREFIX + "/opch", methods=["GET", "POST"], status_code=200, tags=tag)(ApInvoiceCollection)
    api.view(PURCHASE_API_PREFIX + "/opch/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        ApInvoiceDetail
    )
    api.view(PURCHASE_API_PREFIX + "/pch1", methods=["GET", "POST"], status_code=200, tags=tag)(ApInvoiceLineCollection)
    api.view(PURCHASE_API_PREFIX + "/pch1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        ApInvoiceLineDetail
    )
