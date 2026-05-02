"""
Sales Bolt API — ভিউ (``django_bolt_guide.md``: ``APIView``, ``BadRequest`` / ``NotFound``)।

সিরিয়ালাইজার: ``serializers.py``। কোনো আলাদা হেল্পার মডিউল বা ফাংশন নেই।
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from asgiref.sync import sync_to_async
from django.db import IntegrityError
from django.db.models import Q
from django_bolt import BoltAPI
from django_bolt.auth import IsAuthenticated, JWTAuthentication
from django_bolt.exceptions import BadRequest, NotFound
from django_bolt.views import APIView

from apps.sales.models import DLN1, INV1, ODLN, OINV, OQUT, ORDN, ORDR, QUT1, RDN1, RDR1

from .serializers import (
    CustomerReturnCreateBody,
    CustomerReturnLineCreateBody,
    CustomerReturnLinePage,
    CustomerReturnLinePatchBody,
    CustomerReturnLineResponse,
    CustomerReturnPage,
    CustomerReturnPatchBody,
    CustomerReturnResponse,
    DeliveryLineCreateBody,
    DeliveryLinePage,
    DeliveryLinePatchBody,
    DeliveryLineResponse,
    DeliveryNoteCreateBody,
    DeliveryNotePage,
    DeliveryNotePatchBody,
    DeliveryNoteResponse,
    SalesInvoiceCreateBody,
    SalesInvoiceLineCreateBody,
    SalesInvoiceLinePage,
    SalesInvoiceLinePatchBody,
    SalesInvoiceLineResponse,
    SalesInvoicePage,
    SalesInvoicePatchBody,
    SalesInvoiceResponse,
    SalesOrderCreateBody,
    SalesOrderLineCreateBody,
    SalesOrderLinePage,
    SalesOrderLinePatchBody,
    SalesOrderLineResponse,
    SalesOrderPage,
    SalesOrderPatchBody,
    SalesOrderResponse,
    SalesQuotationCreateBody,
    SalesQuotationLineCreateBody,
    SalesQuotationLinePage,
    SalesQuotationLinePatchBody,
    SalesQuotationLineResponse,
    SalesQuotationPage,
    SalesQuotationPatchBody,
    SalesQuotationResponse,
)


SALES_API_PREFIX = "/api/sales"


def _sales_order_response(o: ORDR) -> SalesOrderResponse:
    return SalesOrderResponse(
        DocEntry=o.DocEntry,
        DocNum=o.DocNum,
        CardCode=o.CardCode,
        CardName=o.CardName or "",
        NumAtCard=o.NumAtCard or "",
        CntctPrsn=o.CntctPrsn or "",
        DocCur=o.DocCur or "",
        DocStatus=o.DocStatus,
        DocDate=o.DocDate,
        DocDueDate=o.DocDueDate,
        TaxDate=o.TaxDate,
        DocTotal=str(o.DocTotal),
        VatSum=str(o.VatSum),
        DiscSum=str(o.DiscSum),
        Comments=o.Comments or "",
        SlpCode=o.SlpCode,
        OwnerCode=o.OwnerCode or "",
        Canceled=o.Canceled,
    )


def _sales_order_line_response(o: RDR1) -> SalesOrderLineResponse:
    return SalesOrderLineResponse(
        DocEntry=o.header_id,
        LineNum=o.LineNum,
        ItemCode=o.ItemCode,
        Dscription=o.Dscription or "",
        Quantity=str(o.Quantity),
        Price=str(o.Price),
        DiscPrcnt=str(o.DiscPrcnt),
        WhsCode=o.WhsCode,
        LineTotal=str(o.LineTotal),
        BaseEntry=o.BaseEntry,
        BaseLine=o.BaseLine,
        Canceled=o.Canceled,
    )


def _sales_quotation_response(o: OQUT) -> SalesQuotationResponse:
    return SalesQuotationResponse(
        DocEntry=o.DocEntry,
        DocNum=o.DocNum,
        CardCode=o.CardCode,
        CardName=o.CardName or "",
        NumAtCard=o.NumAtCard or "",
        CntctPrsn=o.CntctPrsn or "",
        DocCur=o.DocCur or "",
        DocStatus=o.DocStatus,
        DocDate=o.DocDate,
        DocDueDate=o.DocDueDate,
        TaxDate=o.TaxDate,
        DocTotal=str(o.DocTotal),
        VatSum=str(o.VatSum),
        DiscSum=str(o.DiscSum),
        Comments=o.Comments or "",
        SlpCode=o.SlpCode,
        OwnerCode=o.OwnerCode or "",
        Canceled=o.Canceled,
    )


def _sales_quotation_line_response(o: QUT1) -> SalesQuotationLineResponse:
    return SalesQuotationLineResponse(
        DocEntry=o.header_id,
        LineNum=o.LineNum,
        ItemCode=o.ItemCode,
        Dscription=o.Dscription or "",
        Quantity=str(o.Quantity),
        Price=str(o.Price),
        DiscPrcnt=str(o.DiscPrcnt),
        WhsCode=o.WhsCode,
        LineTotal=str(o.LineTotal),
        Canceled=o.Canceled,
    )


def _delivery_note_response(o: ODLN) -> DeliveryNoteResponse:
    return DeliveryNoteResponse(
        DocEntry=o.DocEntry,
        DocNum=o.DocNum,
        CardCode=o.CardCode,
        CardName=o.CardName or "",
        NumAtCard=o.NumAtCard or "",
        CntctPrsn=o.CntctPrsn or "",
        DocCur=o.DocCur or "",
        DocStatus=o.DocStatus,
        DocDate=o.DocDate,
        DocDueDate=o.DocDueDate,
        TaxDate=o.TaxDate,
        DocTotal=str(o.DocTotal),
        VatSum=str(o.VatSum),
        DiscSum=str(o.DiscSum),
        Comments=o.Comments or "",
        SlpCode=o.SlpCode,
        OwnerCode=o.OwnerCode or "",
        Canceled=o.Canceled,
    )


def _delivery_line_response(o: DLN1) -> DeliveryLineResponse:
    return DeliveryLineResponse(
        DocEntry=o.header_id,
        LineNum=o.LineNum,
        ItemCode=o.ItemCode,
        Dscription=o.Dscription or "",
        Quantity=str(o.Quantity),
        Price=str(o.Price),
        DiscPrcnt=str(o.DiscPrcnt),
        LineTotal=str(o.LineTotal),
        WhsCode=o.WhsCode,
        BaseType=o.BaseType,
        BaseEntry=o.BaseEntry,
        BaseLine=o.BaseLine,
        Canceled=o.Canceled,
    )


def _customer_return_response(o: ORDN) -> CustomerReturnResponse:
    return CustomerReturnResponse(
        DocEntry=o.DocEntry,
        DocNum=o.DocNum,
        CardCode=o.CardCode,
        CardName=o.CardName or "",
        NumAtCard=o.NumAtCard or "",
        CntctPrsn=o.CntctPrsn or "",
        DocCur=o.DocCur or "",
        DocStatus=o.DocStatus,
        DocDate=o.DocDate,
        DocDueDate=o.DocDueDate,
        TaxDate=o.TaxDate,
        DocTotal=str(o.DocTotal),
        VatSum=str(o.VatSum),
        DiscSum=str(o.DiscSum),
        Comments=o.Comments or "",
        SlpCode=o.SlpCode,
        OwnerCode=o.OwnerCode or "",
        Canceled=o.Canceled,
    )


def _customer_return_line_response(o: RDN1) -> CustomerReturnLineResponse:
    return CustomerReturnLineResponse(
        DocEntry=o.header_id,
        LineNum=o.LineNum,
        ItemCode=o.ItemCode,
        Dscription=o.Dscription or "",
        Quantity=str(o.Quantity),
        Price=str(o.Price),
        DiscPrcnt=str(o.DiscPrcnt),
        LineTotal=str(o.LineTotal),
        WhsCode=o.WhsCode,
        BaseType=o.BaseType,
        BaseEntry=o.BaseEntry,
        BaseLine=o.BaseLine,
        Canceled=o.Canceled,
    )


def _sales_invoice_response(o: OINV) -> SalesInvoiceResponse:
    return SalesInvoiceResponse(
        DocEntry=o.DocEntry,
        DocNum=o.DocNum,
        CardCode=o.CardCode,
        CardName=o.CardName or "",
        NumAtCard=o.NumAtCard or "",
        CntctPrsn=o.CntctPrsn or "",
        DocCur=o.DocCur or "",
        DocDate=o.DocDate,
        DocDueDate=o.DocDueDate,
        TaxDate=o.TaxDate,
        DocTotal=str(o.DocTotal),
        VatSum=str(o.VatSum),
        DiscSum=str(o.DiscSum),
        Comments=o.Comments or "",
        SlpCode=o.SlpCode,
        OwnerCode=o.OwnerCode or "",
        Canceled=o.Canceled,
    )


def _sales_invoice_line_response(o: INV1) -> SalesInvoiceLineResponse:
    return SalesInvoiceLineResponse(
        DocEntry=o.header_id,
        LineNum=o.LineNum,
        ItemCode=o.ItemCode,
        Dscription=o.Dscription or "",
        Quantity=str(o.Quantity),
        Price=str(o.Price),
        DiscPrcnt=str(o.DiscPrcnt),
        LineTotal=str(o.LineTotal),
        WhsCode=o.WhsCode or "",
        BaseType=o.BaseType,
        BaseEntry=o.BaseEntry,
        BaseLine=o.BaseLine,
        Canceled=o.Canceled,
    )


class SalesQuotationCollection(APIView):
    """Sales quotation header (OQUT): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> SalesQuotationPage:
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
        queryset = OQUT.objects.all().order_by("-DocEntry")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N")
        if search_prefix:
            queryset = queryset.filter(
                Q(CardCode__istartswith=search_prefix) | Q(CardName__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return SalesQuotationPage(
            items=[_sales_quotation_response(o) for o in rows],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: SalesQuotationCreateBody) -> SalesQuotationResponse:
        status = (data.DocStatus or "O").strip().upper()[:1] or "O"
        if status not in ("O", "C"):
            raise BadRequest(detail="DocStatus must be O or C.")
        header = OQUT(
            DocNum=data.DocNum,
            CardCode=data.CardCode.strip(),
            CardName=(data.CardName or "").strip(),
            NumAtCard=(data.NumAtCard or "").strip(),
            CntctPrsn=(data.CntctPrsn or "").strip(),
            DocCur=(data.DocCur or "").strip()[:15],
            DocStatus=status,
            DocDate=data.DocDate,
            DocDueDate=data.DocDueDate,
            TaxDate=data.TaxDate,
            DocTotal=Decimal(str(data.DocTotal or "0")),
            VatSum=Decimal(str(data.VatSum or "0")),
            DiscSum=Decimal(str(data.DiscSum or "0")),
            Comments=(data.Comments or "").strip(),
            SlpCode=data.SlpCode,
            OwnerCode=(data.OwnerCode or "").strip()[:50],
        )
        await header.asave()
        return _sales_quotation_response(header)


class SalesQuotationDetail(APIView):
    """Single quotation header: GET / PATCH / DELETE (soft ``Canceled='Y'``)."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> SalesQuotationResponse:
        try:
            o = await OQUT.objects.aget(pk=doc_entry)
        except OQUT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return _sales_quotation_response(o)

    async def patch(self, doc_entry: int, data: SalesQuotationPatchBody) -> SalesQuotationResponse:
        try:
            o = await OQUT.objects.aget(pk=doc_entry)
        except OQUT.DoesNotExist:
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
        if data.NumAtCard is not None:
            o.NumAtCard = data.NumAtCard.strip()
        if data.CntctPrsn is not None:
            o.CntctPrsn = data.CntctPrsn.strip()
        if data.DocCur is not None:
            o.DocCur = data.DocCur.strip()[:15]
        if data.DocStatus is not None:
            st = (data.DocStatus or "O").strip().upper()[:1] or "O"
            if st not in ("O", "C"):
                raise BadRequest(detail="DocStatus must be O or C.")
            o.DocStatus = st
        if data.DocDate is not None:
            o.DocDate = data.DocDate
        if data.DocDueDate is not None:
            o.DocDueDate = data.DocDueDate
        if data.TaxDate is not None:
            o.TaxDate = data.TaxDate
        if data.DocTotal is not None:
            o.DocTotal = Decimal(str(data.DocTotal))
        if data.VatSum is not None:
            o.VatSum = Decimal(str(data.VatSum))
        if data.DiscSum is not None:
            o.DiscSum = Decimal(str(data.DiscSum))
        if data.Comments is not None:
            o.Comments = data.Comments.strip()
        if data.SlpCode is not None:
            o.SlpCode = data.SlpCode
        if data.OwnerCode is not None:
            o.OwnerCode = data.OwnerCode.strip()[:50]
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return _sales_quotation_response(o)

    async def delete(self, doc_entry: int) -> SalesQuotationResponse:
        try:
            o = await OQUT.objects.aget(pk=doc_entry)
        except OQUT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return _sales_quotation_response(o)


class SalesQuotationLineCollection(APIView):
    """Quotation lines (QUT1): list (optional ``doc_entry``) or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> SalesQuotationLinePage:
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
        queryset = QUT1.objects.all().order_by("header_id", "LineNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N", header__Canceled="N")
        if doc_entry is not None:
            queryset = queryset.filter(header_id=doc_entry)
        if search_prefix:
            queryset = queryset.filter(
                Q(ItemCode__istartswith=search_prefix) | Q(Dscription__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return SalesQuotationLinePage(
            items=[_sales_quotation_line_response(o) for o in rows],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: SalesQuotationLineCreateBody) -> SalesQuotationLineResponse:
        hdr = await OQUT.objects.filter(pk=data.DocEntry).afirst()
        if not hdr:
            raise BadRequest(detail="Invalid DocEntry (OQUT).")
        if hdr.Canceled == "Y":
            raise BadRequest(detail="Cannot add lines to a canceled document.")
        line = QUT1(
            header_id=data.DocEntry,
            LineNum=int(data.LineNum),
            ItemCode=data.ItemCode.strip(),
            Dscription=(data.Dscription or "").strip(),
            Quantity=Decimal(str(data.Quantity)),
            Price=Decimal(str(data.Price or "0")),
            DiscPrcnt=Decimal(str(data.DiscPrcnt or "0")),
            WhsCode=data.WhsCode.strip(),
            LineTotal=Decimal(str(data.LineTotal or "0")),
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        return _sales_quotation_line_response(line)


class SalesQuotationLineDetail(APIView):
    """Single quotation line."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> SalesQuotationLineResponse:
        try:
            o = await QUT1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except QUT1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return _sales_quotation_line_response(o)

    async def patch(self, doc_entry: int, line_num: int, data: SalesQuotationLinePatchBody) -> SalesQuotationLineResponse:
        try:
            o = await QUT1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except QUT1.DoesNotExist:
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
        if data.Price is not None:
            o.Price = Decimal(str(data.Price))
        if data.DiscPrcnt is not None:
            o.DiscPrcnt = Decimal(str(data.DiscPrcnt))
        if data.WhsCode is not None:
            o.WhsCode = data.WhsCode.strip()
        if data.LineTotal is not None:
            o.LineTotal = Decimal(str(data.LineTotal))
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return _sales_quotation_line_response(o)

    async def delete(self, doc_entry: int, line_num: int) -> SalesQuotationLineResponse:
        try:
            o = await QUT1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except QUT1.DoesNotExist:
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
        return _sales_quotation_line_response(o)


class SalesOrderCollection(APIView):
    """Sales order header (ORDR): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> SalesOrderPage:
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
        queryset = ORDR.objects.all().order_by("-DocEntry")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N")
        if search_prefix:
            queryset = queryset.filter(
                Q(CardCode__istartswith=search_prefix)
                | Q(CardName__istartswith=search_prefix)
                | Q(NumAtCard__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return SalesOrderPage(
            items=[_sales_order_response(o) for o in rows],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: SalesOrderCreateBody) -> SalesOrderResponse:
        status = (data.DocStatus or "O").strip().upper()[:1] or "O"
        if status not in ("O", "C"):
            raise BadRequest(detail="DocStatus must be O or C.")
        header = ORDR(
            DocNum=data.DocNum,
            CardCode=data.CardCode.strip(),
            CardName=(data.CardName or "").strip(),
            NumAtCard=(data.NumAtCard or "").strip(),
            CntctPrsn=(data.CntctPrsn or "").strip(),
            DocCur=(data.DocCur or "").strip()[:15],
            DocStatus=status,
            DocDate=data.DocDate,
            DocDueDate=data.DocDueDate,
            TaxDate=data.TaxDate,
            DocTotal=Decimal(str(data.DocTotal or "0")),
            VatSum=Decimal(str(data.VatSum or "0")),
            DiscSum=Decimal(str(data.DiscSum or "0")),
            Comments=(data.Comments or "").strip(),
            SlpCode=data.SlpCode,
            OwnerCode=(data.OwnerCode or "").strip()[:50],
        )
        await header.asave()
        return _sales_order_response(header)


class SalesOrderDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> SalesOrderResponse:
        try:
            o = await ORDR.objects.aget(pk=doc_entry)
        except ORDR.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return _sales_order_response(o)

    async def patch(self, doc_entry: int, data: SalesOrderPatchBody) -> SalesOrderResponse:
        try:
            o = await ORDR.objects.aget(pk=doc_entry)
        except ORDR.DoesNotExist:
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
        if data.NumAtCard is not None:
            o.NumAtCard = data.NumAtCard.strip()
        if data.CntctPrsn is not None:
            o.CntctPrsn = data.CntctPrsn.strip()
        if data.DocCur is not None:
            o.DocCur = data.DocCur.strip()[:15]
        if data.DocStatus is not None:
            st = (data.DocStatus or "O").strip().upper()[:1] or "O"
            if st not in ("O", "C"):
                raise BadRequest(detail="DocStatus must be O or C.")
            o.DocStatus = st
        if data.DocDate is not None:
            o.DocDate = data.DocDate
        if data.DocDueDate is not None:
            o.DocDueDate = data.DocDueDate
        if data.TaxDate is not None:
            o.TaxDate = data.TaxDate
        if data.DocTotal is not None:
            o.DocTotal = Decimal(str(data.DocTotal))
        if data.VatSum is not None:
            o.VatSum = Decimal(str(data.VatSum))
        if data.DiscSum is not None:
            o.DiscSum = Decimal(str(data.DiscSum))
        if data.Comments is not None:
            o.Comments = data.Comments.strip()
        if data.SlpCode is not None:
            o.SlpCode = data.SlpCode
        if data.OwnerCode is not None:
            o.OwnerCode = data.OwnerCode.strip()[:50]
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return _sales_order_response(o)

    async def delete(self, doc_entry: int) -> SalesOrderResponse:
        try:
            o = await ORDR.objects.aget(pk=doc_entry)
        except ORDR.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return _sales_order_response(o)


class SalesOrderLineCollection(APIView):
    """Sales order lines (RDR1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> SalesOrderLinePage:
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
        queryset = RDR1.objects.all().order_by("header_id", "LineNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N", header__Canceled="N")
        if doc_entry is not None:
            queryset = queryset.filter(header_id=doc_entry)
        if search_prefix:
            queryset = queryset.filter(Q(ItemCode__istartswith=search_prefix) | Q(WhsCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return SalesOrderLinePage(
            items=[_sales_order_line_response(o) for o in rows],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: SalesOrderLineCreateBody) -> SalesOrderLineResponse:
        hdr = await ORDR.objects.filter(pk=data.DocEntry).afirst()
        if not hdr:
            raise BadRequest(detail="Invalid DocEntry (ORDR).")
        if hdr.Canceled == "Y":
            raise BadRequest(detail="Cannot add lines to a canceled document.")
        line = RDR1(
            header_id=data.DocEntry,
            LineNum=int(data.LineNum),
            ItemCode=data.ItemCode.strip(),
            Dscription=(data.Dscription or "").strip(),
            Quantity=Decimal(str(data.Quantity)),
            Price=Decimal(str(data.Price or "0")),
            DiscPrcnt=Decimal(str(data.DiscPrcnt or "0")),
            WhsCode=data.WhsCode.strip(),
            LineTotal=Decimal(str(data.LineTotal or "0")),
            BaseEntry=data.BaseEntry,
            BaseLine=data.BaseLine,
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        return _sales_order_line_response(line)


class SalesOrderLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> SalesOrderLineResponse:
        try:
            o = await RDR1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RDR1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return _sales_order_line_response(o)

    async def patch(self, doc_entry: int, line_num: int, data: SalesOrderLinePatchBody) -> SalesOrderLineResponse:
        try:
            o = await RDR1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RDR1.DoesNotExist:
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
        if data.Price is not None:
            o.Price = Decimal(str(data.Price))
        if data.DiscPrcnt is not None:
            o.DiscPrcnt = Decimal(str(data.DiscPrcnt))
        if data.WhsCode is not None:
            o.WhsCode = data.WhsCode.strip()
        if data.LineTotal is not None:
            o.LineTotal = Decimal(str(data.LineTotal))
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
        return _sales_order_line_response(o)

    async def delete(self, doc_entry: int, line_num: int) -> SalesOrderLineResponse:
        try:
            o = await RDR1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RDR1.DoesNotExist:
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
        return _sales_order_line_response(o)


class DeliveryNoteCollection(APIView):
    """Delivery header (ODLN): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> DeliveryNotePage:
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
        queryset = ODLN.objects.all().order_by("-DocEntry")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N")
        if search_prefix:
            queryset = queryset.filter(
                Q(CardCode__istartswith=search_prefix) | Q(CardName__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return DeliveryNotePage(
            items=[
                DeliveryNoteResponse(
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

    async def post(self, data: DeliveryNoteCreateBody) -> DeliveryNoteResponse:
        header = ODLN(
            DocNum=data.DocNum,
            CardCode=data.CardCode.strip(),
            CardName=(data.CardName or "").strip(),
            DocDate=data.DocDate,
        )
        await header.asave()
        return DeliveryNoteResponse(
            DocEntry=header.DocEntry,
            DocNum=header.DocNum,
            CardCode=header.CardCode,
            CardName=header.CardName or "",
            DocDate=header.DocDate,
            Canceled=header.Canceled,
        )


class DeliveryNoteDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> DeliveryNoteResponse:
        try:
            o = await ODLN.objects.aget(pk=doc_entry)
        except ODLN.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return DeliveryNoteResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, data: DeliveryNotePatchBody) -> DeliveryNoteResponse:
        try:
            o = await ODLN.objects.aget(pk=doc_entry)
        except ODLN.DoesNotExist:
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
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return DeliveryNoteResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int) -> DeliveryNoteResponse:
        try:
            o = await ODLN.objects.aget(pk=doc_entry)
        except ODLN.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return DeliveryNoteResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            Canceled=o.Canceled,
        )


class DeliveryLineCollection(APIView):
    """Delivery lines (DLN1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> DeliveryLinePage:
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
        queryset = DLN1.objects.all().order_by("header_id", "LineNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N", header__Canceled="N")
        if doc_entry is not None:
            queryset = queryset.filter(header_id=doc_entry)
        if search_prefix:
            queryset = queryset.filter(Q(ItemCode__istartswith=search_prefix) | Q(WhsCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return DeliveryLinePage(
            items=[
                DeliveryLineResponse(
                    DocEntry=o.header_id,
                    LineNum=o.LineNum,
                    ItemCode=o.ItemCode,
                    Quantity=str(o.Quantity),
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

    async def post(self, data: DeliveryLineCreateBody) -> DeliveryLineResponse:
        hdr = await ODLN.objects.filter(pk=data.DocEntry).afirst()
        if not hdr:
            raise BadRequest(detail="Invalid DocEntry (ODLN).")
        if hdr.Canceled == "Y":
            raise BadRequest(detail="Cannot add lines to a canceled document.")
        line = DLN1(
            header_id=data.DocEntry,
            LineNum=int(data.LineNum),
            ItemCode=data.ItemCode.strip(),
            Quantity=Decimal(str(data.Quantity)),
            WhsCode=data.WhsCode.strip(),
            BaseType=data.BaseType,
            BaseEntry=data.BaseEntry,
            BaseLine=data.BaseLine,
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        return DeliveryLineResponse(
            DocEntry=line.header_id,
            LineNum=line.LineNum,
            ItemCode=line.ItemCode,
            Quantity=str(line.Quantity),
            WhsCode=line.WhsCode,
            BaseType=line.BaseType,
            BaseEntry=line.BaseEntry,
            BaseLine=line.BaseLine,
            Canceled=line.Canceled,
        )


class DeliveryLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> DeliveryLineResponse:
        try:
            o = await DLN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except DLN1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return DeliveryLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, line_num: int, data: DeliveryLinePatchBody) -> DeliveryLineResponse:
        try:
            o = await DLN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except DLN1.DoesNotExist:
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
        return DeliveryLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int, line_num: int) -> DeliveryLineResponse:
        try:
            o = await DLN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except DLN1.DoesNotExist:
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
        return DeliveryLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            BaseType=o.BaseType,
            BaseEntry=o.BaseEntry,
            BaseLine=o.BaseLine,
            Canceled=o.Canceled,
        )


class CustomerReturnCollection(APIView):
    """Return header (ORDN): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> CustomerReturnPage:
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
        queryset = ORDN.objects.all().order_by("-DocEntry")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N")
        if search_prefix:
            queryset = queryset.filter(
                Q(CardCode__istartswith=search_prefix) | Q(CardName__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return CustomerReturnPage(
            items=[
                CustomerReturnResponse(
                    DocEntry=o.DocEntry,
                    DocNum=o.DocNum,
                    CardCode=o.CardCode,
                    CardName=o.CardName or "",
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: CustomerReturnCreateBody) -> CustomerReturnResponse:
        header = ORDN(
            DocNum=data.DocNum,
            CardCode=data.CardCode.strip(),
            CardName=(data.CardName or "").strip(),
        )
        await header.asave()
        return CustomerReturnResponse(
            DocEntry=header.DocEntry,
            DocNum=header.DocNum,
            CardCode=header.CardCode,
            CardName=header.CardName or "",
            Canceled=header.Canceled,
        )


class CustomerReturnDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> CustomerReturnResponse:
        try:
            o = await ORDN.objects.aget(pk=doc_entry)
        except ORDN.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return CustomerReturnResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, data: CustomerReturnPatchBody) -> CustomerReturnResponse:
        try:
            o = await ORDN.objects.aget(pk=doc_entry)
        except ORDN.DoesNotExist:
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
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return CustomerReturnResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int) -> CustomerReturnResponse:
        try:
            o = await ORDN.objects.aget(pk=doc_entry)
        except ORDN.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return CustomerReturnResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            Canceled=o.Canceled,
        )


class CustomerReturnLineCollection(APIView):
    """Return lines (RDN1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> CustomerReturnLinePage:
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
        queryset = RDN1.objects.all().order_by("header_id", "LineNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N", header__Canceled="N")
        if doc_entry is not None:
            queryset = queryset.filter(header_id=doc_entry)
        if search_prefix:
            queryset = queryset.filter(Q(ItemCode__istartswith=search_prefix) | Q(WhsCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return CustomerReturnLinePage(
            items=[
                CustomerReturnLineResponse(
                    DocEntry=o.header_id,
                    LineNum=o.LineNum,
                    ItemCode=o.ItemCode,
                    Quantity=str(o.Quantity),
                    WhsCode=o.WhsCode,
                    BaseEntry=o.BaseEntry,
                    Canceled=o.Canceled,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: CustomerReturnLineCreateBody) -> CustomerReturnLineResponse:
        hdr = await ORDN.objects.filter(pk=data.DocEntry).afirst()
        if not hdr:
            raise BadRequest(detail="Invalid DocEntry (ORDN).")
        if hdr.Canceled == "Y":
            raise BadRequest(detail="Cannot add lines to a canceled document.")
        line = RDN1(
            header_id=data.DocEntry,
            LineNum=int(data.LineNum),
            ItemCode=data.ItemCode.strip(),
            Quantity=Decimal(str(data.Quantity)),
            WhsCode=data.WhsCode.strip(),
            BaseEntry=data.BaseEntry,
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        return CustomerReturnLineResponse(
            DocEntry=line.header_id,
            LineNum=line.LineNum,
            ItemCode=line.ItemCode,
            Quantity=str(line.Quantity),
            WhsCode=line.WhsCode,
            BaseEntry=line.BaseEntry,
            Canceled=line.Canceled,
        )


class CustomerReturnLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> CustomerReturnLineResponse:
        try:
            o = await RDN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RDN1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return CustomerReturnLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            BaseEntry=o.BaseEntry,
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, line_num: int, data: CustomerReturnLinePatchBody) -> CustomerReturnLineResponse:
        try:
            o = await RDN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RDN1.DoesNotExist:
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
        if data.BaseEntry is not None:
            o.BaseEntry = data.BaseEntry
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return CustomerReturnLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            BaseEntry=o.BaseEntry,
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int, line_num: int) -> CustomerReturnLineResponse:
        try:
            o = await RDN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RDN1.DoesNotExist:
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
        return CustomerReturnLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            ItemCode=o.ItemCode,
            Quantity=str(o.Quantity),
            WhsCode=o.WhsCode,
            BaseEntry=o.BaseEntry,
            Canceled=o.Canceled,
        )


class SalesInvoiceCollection(APIView):
    """A/R invoice header (OINV): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> SalesInvoicePage:
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
        queryset = OINV.objects.all().order_by("-DocEntry")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N")
        if search_prefix:
            queryset = queryset.filter(
                Q(CardCode__istartswith=search_prefix) | Q(CardName__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return SalesInvoicePage(
            items=[
                SalesInvoiceResponse(
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

    async def post(self, data: SalesInvoiceCreateBody) -> SalesInvoiceResponse:
        header = OINV(
            DocNum=data.DocNum,
            CardCode=data.CardCode.strip(),
            CardName=(data.CardName or "").strip(),
            DocDate=data.DocDate,
            DocTotal=Decimal(str(data.DocTotal or "0")),
            VatSum=Decimal(str(data.VatSum or "0")),
        )
        await header.asave()
        return SalesInvoiceResponse(
            DocEntry=header.DocEntry,
            DocNum=header.DocNum,
            CardCode=header.CardCode,
            CardName=header.CardName or "",
            DocDate=header.DocDate,
            DocTotal=str(header.DocTotal),
            VatSum=str(header.VatSum),
            Canceled=header.Canceled,
        )


class SalesInvoiceDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> SalesInvoiceResponse:
        try:
            o = await OINV.objects.aget(pk=doc_entry)
        except OINV.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return SalesInvoiceResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            DocTotal=str(o.DocTotal),
            VatSum=str(o.VatSum),
            Canceled=o.Canceled,
        )

    async def patch(self, doc_entry: int, data: SalesInvoicePatchBody) -> SalesInvoiceResponse:
        try:
            o = await OINV.objects.aget(pk=doc_entry)
        except OINV.DoesNotExist:
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
        return SalesInvoiceResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            DocTotal=str(o.DocTotal),
            VatSum=str(o.VatSum),
            Canceled=o.Canceled,
        )

    async def delete(self, doc_entry: int) -> SalesInvoiceResponse:
        try:
            o = await OINV.objects.aget(pk=doc_entry)
        except OINV.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return SalesInvoiceResponse(
            DocEntry=o.DocEntry,
            DocNum=o.DocNum,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            DocTotal=str(o.DocTotal),
            VatSum=str(o.VatSum),
            Canceled=o.Canceled,
        )


class SalesInvoiceLineCollection(APIView):
    """A/R invoice lines (INV1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> SalesInvoiceLinePage:
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
        queryset = INV1.objects.all().order_by("header_id", "LineNum")
        if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):
            queryset = queryset.filter(Canceled="N", header__Canceled="N")
        if doc_entry is not None:
            queryset = queryset.filter(header_id=doc_entry)
        if search_prefix:
            queryset = queryset.filter(Q(ItemCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return SalesInvoiceLinePage(
            items=[
                SalesInvoiceLineResponse(
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

    async def post(self, data: SalesInvoiceLineCreateBody) -> SalesInvoiceLineResponse:
        hdr = await OINV.objects.filter(pk=data.DocEntry).afirst()
        if not hdr:
            raise BadRequest(detail="Invalid DocEntry (OINV).")
        if hdr.Canceled == "Y":
            raise BadRequest(detail="Cannot add lines to a canceled document.")
        line = INV1(
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
        return SalesInvoiceLineResponse(
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


class SalesInvoiceLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> SalesInvoiceLineResponse:
        try:
            o = await INV1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except INV1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return SalesInvoiceLineResponse(
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

    async def patch(self, doc_entry: int, line_num: int, data: SalesInvoiceLinePatchBody) -> SalesInvoiceLineResponse:
        try:
            o = await INV1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except INV1.DoesNotExist:
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
        return SalesInvoiceLineResponse(
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

    async def delete(self, doc_entry: int, line_num: int) -> SalesInvoiceLineResponse:
        try:
            o = await INV1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except INV1.DoesNotExist:
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
        return SalesInvoiceLineResponse(
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


def attach_sales_routes(api: BoltAPI) -> None:
    """Register Sales A/R Bolt routes."""
    tag = ["sales"]
    # Human-readable paths (legacy SAP-style paths kept for compatibility).
    api.view(SALES_API_PREFIX + "/quotations", methods=["GET", "POST"], status_code=200, tags=tag)(SalesQuotationCollection)
    api.view(SALES_API_PREFIX + "/quotations/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesQuotationDetail
    )
    api.view(SALES_API_PREFIX + "/quotation-lines", methods=["GET", "POST"], status_code=200, tags=tag)(SalesQuotationLineCollection)
    api.view(
        SALES_API_PREFIX + "/quotation-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(SalesQuotationLineDetail)
    api.view(SALES_API_PREFIX + "/sales-orders", methods=["GET", "POST"], status_code=200, tags=tag)(SalesOrderCollection)
    api.view(SALES_API_PREFIX + "/sales-orders/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesOrderDetail
    )
    api.view(SALES_API_PREFIX + "/sales-order-lines", methods=["GET", "POST"], status_code=200, tags=tag)(SalesOrderLineCollection)
    api.view(
        SALES_API_PREFIX + "/sales-order-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(SalesOrderLineDetail)
    api.view(SALES_API_PREFIX + "/deliveries", methods=["GET", "POST"], status_code=200, tags=tag)(DeliveryNoteCollection)
    api.view(SALES_API_PREFIX + "/deliveries/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        DeliveryNoteDetail
    )
    api.view(SALES_API_PREFIX + "/delivery-lines", methods=["GET", "POST"], status_code=200, tags=tag)(DeliveryLineCollection)
    api.view(
        SALES_API_PREFIX + "/delivery-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(DeliveryLineDetail)
    api.view(SALES_API_PREFIX + "/customer-returns", methods=["GET", "POST"], status_code=200, tags=tag)(CustomerReturnCollection)
    api.view(SALES_API_PREFIX + "/customer-returns/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        CustomerReturnDetail
    )
    api.view(SALES_API_PREFIX + "/customer-return-lines", methods=["GET", "POST"], status_code=200, tags=tag)(CustomerReturnLineCollection)
    api.view(
        SALES_API_PREFIX + "/customer-return-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(CustomerReturnLineDetail)
    api.view(SALES_API_PREFIX + "/invoices", methods=["GET", "POST"], status_code=200, tags=tag)(SalesInvoiceCollection)
    api.view(SALES_API_PREFIX + "/invoices/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesInvoiceDetail
    )
    api.view(SALES_API_PREFIX + "/invoice-lines", methods=["GET", "POST"], status_code=200, tags=tag)(SalesInvoiceLineCollection)
    api.view(
        SALES_API_PREFIX + "/invoice-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(SalesInvoiceLineDetail)
    api.view(SALES_API_PREFIX + "/oqut", methods=["GET", "POST"], status_code=200, tags=tag)(SalesQuotationCollection)
    api.view(SALES_API_PREFIX + "/oqut/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesQuotationDetail
    )
    api.view(SALES_API_PREFIX + "/qut1", methods=["GET", "POST"], status_code=200, tags=tag)(SalesQuotationLineCollection)
    api.view(SALES_API_PREFIX + "/qut1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesQuotationLineDetail
    )
    api.view(SALES_API_PREFIX + "/ordr", methods=["GET", "POST"], status_code=200, tags=tag)(SalesOrderCollection)
    api.view(SALES_API_PREFIX + "/ordr/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesOrderDetail
    )
    api.view(SALES_API_PREFIX + "/rdr1", methods=["GET", "POST"], status_code=200, tags=tag)(SalesOrderLineCollection)
    api.view(SALES_API_PREFIX + "/rdr1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesOrderLineDetail
    )
    api.view(SALES_API_PREFIX + "/odln", methods=["GET", "POST"], status_code=200, tags=tag)(DeliveryNoteCollection)
    api.view(SALES_API_PREFIX + "/odln/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        DeliveryNoteDetail
    )
    api.view(SALES_API_PREFIX + "/dln1", methods=["GET", "POST"], status_code=200, tags=tag)(DeliveryLineCollection)
    api.view(SALES_API_PREFIX + "/dln1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        DeliveryLineDetail
    )
    api.view(SALES_API_PREFIX + "/ordn", methods=["GET", "POST"], status_code=200, tags=tag)(CustomerReturnCollection)
    api.view(SALES_API_PREFIX + "/ordn/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        CustomerReturnDetail
    )
    api.view(SALES_API_PREFIX + "/rdn1", methods=["GET", "POST"], status_code=200, tags=tag)(CustomerReturnLineCollection)
    api.view(SALES_API_PREFIX + "/rdn1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        CustomerReturnLineDetail
    )
    api.view(SALES_API_PREFIX + "/oinv", methods=["GET", "POST"], status_code=200, tags=tag)(SalesInvoiceCollection)
    api.view(SALES_API_PREFIX + "/oinv/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesInvoiceDetail
    )
    api.view(SALES_API_PREFIX + "/inv1", methods=["GET", "POST"], status_code=200, tags=tag)(SalesInvoiceLineCollection)
    api.view(SALES_API_PREFIX + "/inv1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesInvoiceLineDetail
    )
