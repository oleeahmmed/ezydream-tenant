"""
Sales Bolt API — quotations, orders, deliveries, returns, invoices (Bolt ``APIView``).

List endpoints use ``get_list_pagination_for_request`` and ``get_boolean_query_flag_is_true``;
see ``apps.core.beginner_style``. Serializers live in ``serializers.py``.
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
from django_bolt.request import Request
from django_bolt.views import APIView

from apps.core.beginner_style import (
    async_recalculate_business_partner_rollups_for_card_codes,
    async_run_sync_callable_and_map_validation_error_to_bad_request,
    get_boolean_query_flag_is_true,
    get_list_pagination_for_request,
    get_optional_int_from_query,
)
from apps.finance.services.auto_journal import sync_ar_invoice_journal
from apps.inventory.services import (
    rebuild_oitw_committed_and_on_order,
    resync_all_delivery_lines,
    resync_all_return_lines,
    sync_delivery_line_stock,
    sync_return_line_stock,
)
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


async def async_rebuild_inventory_open_totals_after_sales_change() -> None:
    await sync_to_async(rebuild_oitw_committed_and_on_order)()


def sales_order_header_to_bolt_response(o: ORDR) -> SalesOrderResponse:
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
        U_UserFld1=o.U_UserFld1 or "",
        U_UserFld2=o.U_UserFld2 or "",
        Canceled=o.Canceled,
    )


def sales_order_line_to_bolt_response(o: RDR1) -> SalesOrderLineResponse:
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


def sales_quotation_header_to_bolt_response(o: OQUT) -> SalesQuotationResponse:
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
        U_UserFld1=o.U_UserFld1 or "",
        U_UserFld2=o.U_UserFld2 or "",
        Canceled=o.Canceled,
    )


def sales_quotation_line_to_bolt_response(o: QUT1) -> SalesQuotationLineResponse:
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


def delivery_note_header_to_bolt_response(o: ODLN) -> DeliveryNoteResponse:
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
        U_UserFld1=o.U_UserFld1 or "",
        U_UserFld2=o.U_UserFld2 or "",
        Canceled=o.Canceled,
    )


def delivery_note_line_to_bolt_response(o: DLN1) -> DeliveryLineResponse:
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


def customer_return_header_to_bolt_response(o: ORDN) -> CustomerReturnResponse:
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
        U_UserFld1=o.U_UserFld1 or "",
        U_UserFld2=o.U_UserFld2 or "",
        Canceled=o.Canceled,
    )


def customer_return_line_to_bolt_response(o: RDN1) -> CustomerReturnLineResponse:
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


def sales_invoice_header_to_bolt_response(o: OINV) -> SalesInvoiceResponse:
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
        U_UserFld1=o.U_UserFld1 or "",
        U_UserFld2=o.U_UserFld2 or "",
        Canceled=o.Canceled,
    )


def sales_invoice_line_to_bolt_response(o: INV1) -> SalesInvoiceLineResponse:
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


class SalesQuotationListCreateView(APIView):
    """Sales quotation header (OQUT): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, request: Request) -> SalesQuotationPage:
        # STEP 1 — Bolt list parameters: ``limit``, ``offset``, optional ``q`` prefix.
        limit, offset, search_prefix = get_list_pagination_for_request(self.request)
        queryset = OQUT.objects.all().order_by("-DocEntry")
        if not get_boolean_query_flag_is_true(self.request, "include_deleted"):
            queryset = queryset.filter(Canceled="N")
        if search_prefix:
            queryset = queryset.filter(
                Q(CardCode__istartswith=search_prefix) | Q(CardName__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return SalesQuotationPage(
            items=[sales_quotation_header_to_bolt_response(o) for o in rows],
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
            U_UserFld1=(data.U_UserFld1 or "").strip()[:254],
            U_UserFld2=(data.U_UserFld2 or "").strip()[:254],
        )
        await header.asave()
        return sales_quotation_header_to_bolt_response(header)


class SalesQuotationDetailView(APIView):
    """Single quotation header: GET / PATCH / DELETE (soft ``Canceled='Y'``)."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> SalesQuotationResponse:
        try:
            o = await OQUT.objects.aget(pk=doc_entry)
        except OQUT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return sales_quotation_header_to_bolt_response(o)

    async def patch(self, doc_entry: int, data: SalesQuotationPatchBody) -> SalesQuotationResponse:
        try:
            o = await OQUT.objects.aget(pk=doc_entry)
        except OQUT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and getattr(o, "Canceled", "N") == "Y":
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
        if data.U_UserFld1 is not None:
            o.U_UserFld1 = (data.U_UserFld1 or "").strip()[:254]
        if data.U_UserFld2 is not None:
            o.U_UserFld2 = (data.U_UserFld2 or "").strip()[:254]
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        return sales_quotation_header_to_bolt_response(o)

    async def delete(self, doc_entry: int) -> SalesQuotationResponse:
        try:
            o = await OQUT.objects.aget(pk=doc_entry)
        except OQUT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return sales_quotation_header_to_bolt_response(o)


class SalesQuotationLineListCreateView(APIView):
    """Quotation lines (QUT1): list (optional ``doc_entry``) or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, request: Request) -> SalesQuotationLinePage:
        # STEP 1 — Bolt list parameters: ``limit``, ``offset``, optional ``q`` prefix.
        limit, offset, search_prefix = get_list_pagination_for_request(self.request)
        doc_entry = get_optional_int_from_query(self.request, "doc_entry")
        queryset = QUT1.objects.all().order_by("header_id", "LineNum")
        if not get_boolean_query_flag_is_true(self.request, "include_deleted"):
            queryset = queryset.filter(Canceled="N", header__Canceled="N")
        if doc_entry is not None:
            queryset = queryset.filter(header_id=doc_entry)
        if search_prefix:
            queryset = queryset.filter(
                Q(ItemCode__istartswith=search_prefix) | Q(Dscription__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return SalesQuotationLinePage(
            items=[sales_quotation_line_to_bolt_response(o) for o in rows],
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
        return sales_quotation_line_to_bolt_response(line)


class SalesQuotationLineDetailView(APIView):
    """Single quotation line."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> SalesQuotationLineResponse:
        try:
            o = await QUT1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except QUT1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return sales_quotation_line_to_bolt_response(o)

    async def patch(self, doc_entry: int, line_num: int, data: SalesQuotationLinePatchBody) -> SalesQuotationLineResponse:
        try:
            o = await QUT1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except QUT1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and (
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
        return sales_quotation_line_to_bolt_response(o)

    async def delete(self, doc_entry: int, line_num: int) -> SalesQuotationLineResponse:
        try:
            o = await QUT1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except QUT1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if o.header.Canceled == "Y":
            raise BadRequest(detail="Cannot delete lines of a canceled document.")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return sales_quotation_line_to_bolt_response(o)


class SalesOrderListCreateView(APIView):
    """Sales order header (ORDR): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, request: Request) -> SalesOrderPage:
        # STEP 1 — Bolt list parameters: ``limit``, ``offset``, optional ``q`` prefix.
        limit, offset, search_prefix = get_list_pagination_for_request(self.request)
        queryset = ORDR.objects.all().order_by("-DocEntry")
        if not get_boolean_query_flag_is_true(self.request, "include_deleted"):
            queryset = queryset.filter(Canceled="N")
        if search_prefix:
            queryset = queryset.filter(
                Q(CardCode__istartswith=search_prefix)
                | Q(CardName__istartswith=search_prefix)
                | Q(NumAtCard__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return SalesOrderPage(
            items=[sales_order_header_to_bolt_response(o) for o in rows],
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
            U_UserFld1=(data.U_UserFld1 or "").strip()[:254],
            U_UserFld2=(data.U_UserFld2 or "").strip()[:254],
        )
        await header.asave()
        await async_rebuild_inventory_open_totals_after_sales_change()
        await async_recalculate_business_partner_rollups_for_card_codes(header.CardCode)
        return sales_order_header_to_bolt_response(header)


class SalesOrderDetailView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> SalesOrderResponse:
        try:
            o = await ORDR.objects.aget(pk=doc_entry)
        except ORDR.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return sales_order_header_to_bolt_response(o)

    async def patch(self, doc_entry: int, data: SalesOrderPatchBody) -> SalesOrderResponse:
        try:
            o = await ORDR.objects.aget(pk=doc_entry)
        except ORDR.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        old_cc = o.CardCode
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
        if data.U_UserFld1 is not None:
            o.U_UserFld1 = (data.U_UserFld1 or "").strip()[:254]
        if data.U_UserFld2 is not None:
            o.U_UserFld2 = (data.U_UserFld2 or "").strip()[:254]
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        await async_rebuild_inventory_open_totals_after_sales_change()
        await async_recalculate_business_partner_rollups_for_card_codes(old_cc, o.CardCode)
        return sales_order_header_to_bolt_response(o)

    async def delete(self, doc_entry: int) -> SalesOrderResponse:
        try:
            o = await ORDR.objects.aget(pk=doc_entry)
        except ORDR.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        old_cc = o.CardCode
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        await async_rebuild_inventory_open_totals_after_sales_change()
        await async_recalculate_business_partner_rollups_for_card_codes(old_cc)
        return sales_order_header_to_bolt_response(o)


class SalesOrderLineListCreateView(APIView):
    """Sales order lines (RDR1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, request: Request) -> SalesOrderLinePage:
        # STEP 1 — Bolt list parameters: ``limit``, ``offset``, optional ``q`` prefix.
        limit, offset, search_prefix = get_list_pagination_for_request(self.request)
        doc_entry = get_optional_int_from_query(self.request, "doc_entry")
        queryset = RDR1.objects.all().order_by("header_id", "LineNum")
        if not get_boolean_query_flag_is_true(self.request, "include_deleted"):
            queryset = queryset.filter(Canceled="N", header__Canceled="N")
        if doc_entry is not None:
            queryset = queryset.filter(header_id=doc_entry)
        if search_prefix:
            queryset = queryset.filter(Q(ItemCode__istartswith=search_prefix) | Q(WhsCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return SalesOrderLinePage(
            items=[sales_order_line_to_bolt_response(o) for o in rows],
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
        await async_rebuild_inventory_open_totals_after_sales_change()
        await async_recalculate_business_partner_rollups_for_card_codes(hdr.CardCode)
        return sales_order_line_to_bolt_response(line)


class SalesOrderLineDetailView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> SalesOrderLineResponse:
        try:
            o = await RDR1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RDR1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return sales_order_line_to_bolt_response(o)

    async def patch(self, doc_entry: int, line_num: int, data: SalesOrderLinePatchBody) -> SalesOrderLineResponse:
        try:
            o = await RDR1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RDR1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and (
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
        await async_rebuild_inventory_open_totals_after_sales_change()
        await async_recalculate_business_partner_rollups_for_card_codes(o.header.CardCode)
        return sales_order_line_to_bolt_response(o)

    async def delete(self, doc_entry: int, line_num: int) -> SalesOrderLineResponse:
        try:
            o = await RDR1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RDR1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if o.header.Canceled == "Y":
            raise BadRequest(detail="Cannot delete lines of a canceled document.")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        await async_rebuild_inventory_open_totals_after_sales_change()
        await async_recalculate_business_partner_rollups_for_card_codes(o.header.CardCode)
        return sales_order_line_to_bolt_response(o)


class DeliveryNoteListCreateView(APIView):
    """Delivery header (ODLN): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, request: Request) -> DeliveryNotePage:
        # STEP 1 — Bolt list parameters: ``limit``, ``offset``, optional ``q`` prefix.
        limit, offset, search_prefix = get_list_pagination_for_request(self.request)
        queryset = ODLN.objects.all().order_by("-DocEntry")
        if not get_boolean_query_flag_is_true(self.request, "include_deleted"):
            queryset = queryset.filter(Canceled="N")
        if search_prefix:
            queryset = queryset.filter(
                Q(CardCode__istartswith=search_prefix) | Q(CardName__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return DeliveryNotePage(
            items=[delivery_note_header_to_bolt_response(o) for o in rows],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: DeliveryNoteCreateBody) -> DeliveryNoteResponse:
        st = (data.DocStatus or "O").strip().upper()[:1] or "O"
        if st not in ("O", "C"):
            raise BadRequest(detail="DocStatus must be O or C.")
        header = ODLN(
            DocNum=data.DocNum,
            CardCode=data.CardCode.strip(),
            CardName=(data.CardName or "").strip(),
            NumAtCard=(data.NumAtCard or "").strip(),
            CntctPrsn=(data.CntctPrsn or "").strip(),
            DocCur=(data.DocCur or "").strip()[:15],
            DocStatus=st,
            DocDate=data.DocDate,
            DocDueDate=data.DocDueDate,
            TaxDate=data.TaxDate,
            DocTotal=Decimal(str(data.DocTotal or "0")),
            VatSum=Decimal(str(data.VatSum or "0")),
            DiscSum=Decimal(str(data.DiscSum or "0")),
            Comments=(data.Comments or "").strip(),
            SlpCode=data.SlpCode,
            OwnerCode=(data.OwnerCode or "").strip()[:50],
            U_UserFld1=(data.U_UserFld1 or "").strip()[:254],
            U_UserFld2=(data.U_UserFld2 or "").strip()[:254],
        )
        await header.asave()
        await async_recalculate_business_partner_rollups_for_card_codes(header.CardCode)
        return delivery_note_header_to_bolt_response(header)


class DeliveryNoteDetailView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> DeliveryNoteResponse:
        try:
            o = await ODLN.objects.aget(pk=doc_entry)
        except ODLN.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return delivery_note_header_to_bolt_response(o)

    async def patch(self, doc_entry: int, data: DeliveryNotePatchBody) -> DeliveryNoteResponse:
        try:
            o = await ODLN.objects.aget(pk=doc_entry)
        except ODLN.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        old_cc = o.CardCode
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
        if data.U_UserFld1 is not None:
            o.U_UserFld1 = (data.U_UserFld1 or "").strip()[:254]
        if data.U_UserFld2 is not None:
            o.U_UserFld2 = (data.U_UserFld2 or "").strip()[:254]
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        await async_run_sync_callable_and_map_validation_error_to_bad_request(resync_all_delivery_lines, doc_entry)
        await async_recalculate_business_partner_rollups_for_card_codes(old_cc, o.CardCode)
        return delivery_note_header_to_bolt_response(o)

    async def delete(self, doc_entry: int) -> DeliveryNoteResponse:
        try:
            o = await ODLN.objects.aget(pk=doc_entry)
        except ODLN.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        old_cc = o.CardCode
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        await async_run_sync_callable_and_map_validation_error_to_bad_request(resync_all_delivery_lines, doc_entry)
        await async_recalculate_business_partner_rollups_for_card_codes(old_cc)
        return delivery_note_header_to_bolt_response(o)


class DeliveryLineListCreateView(APIView):
    """Delivery lines (DLN1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, request: Request) -> DeliveryLinePage:
        # STEP 1 — Bolt list parameters: ``limit``, ``offset``, optional ``q`` prefix.
        limit, offset, search_prefix = get_list_pagination_for_request(self.request)
        doc_entry = get_optional_int_from_query(self.request, "doc_entry")
        queryset = DLN1.objects.all().order_by("header_id", "LineNum")
        if not get_boolean_query_flag_is_true(self.request, "include_deleted"):
            queryset = queryset.filter(Canceled="N", header__Canceled="N")
        if doc_entry is not None:
            queryset = queryset.filter(header_id=doc_entry)
        if search_prefix:
            queryset = queryset.filter(Q(ItemCode__istartswith=search_prefix) | Q(WhsCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return DeliveryLinePage(
            items=[delivery_note_line_to_bolt_response(o) for o in rows],
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
            Dscription=(data.Dscription or "").strip(),
            Quantity=Decimal(str(data.Quantity)),
            Price=Decimal(str(data.Price or "0")),
            DiscPrcnt=Decimal(str(data.DiscPrcnt or "0")),
            LineTotal=Decimal(str(data.LineTotal or "0")),
            WhsCode=data.WhsCode.strip(),
            BaseType=data.BaseType,
            BaseEntry=data.BaseEntry,
            BaseLine=data.BaseLine,
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        await async_run_sync_callable_and_map_validation_error_to_bad_request(sync_delivery_line_stock, line.header_id, int(line.LineNum))
        hdr = await ODLN.objects.filter(pk=line.header_id).afirst()
        if hdr:
            await async_recalculate_business_partner_rollups_for_card_codes(hdr.CardCode)
        return delivery_note_line_to_bolt_response(line)


class DeliveryLineDetailView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> DeliveryLineResponse:
        try:
            o = await DLN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except DLN1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return delivery_note_line_to_bolt_response(o)

    async def patch(self, doc_entry: int, line_num: int, data: DeliveryLinePatchBody) -> DeliveryLineResponse:
        try:
            o = await DLN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except DLN1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and (
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
        if data.LineTotal is not None:
            o.LineTotal = Decimal(str(data.LineTotal))
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
        await async_run_sync_callable_and_map_validation_error_to_bad_request(sync_delivery_line_stock, doc_entry, int(line_num))
        await async_recalculate_business_partner_rollups_for_card_codes(o.header.CardCode)
        return delivery_note_line_to_bolt_response(o)

    async def delete(self, doc_entry: int, line_num: int) -> DeliveryLineResponse:
        try:
            o = await DLN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except DLN1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if o.header.Canceled == "Y":
            raise BadRequest(detail="Cannot delete lines of a canceled document.")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        await async_run_sync_callable_and_map_validation_error_to_bad_request(sync_delivery_line_stock, doc_entry, int(line_num))
        await async_recalculate_business_partner_rollups_for_card_codes(o.header.CardCode)
        return delivery_note_line_to_bolt_response(o)


class CustomerReturnListCreateView(APIView):
    """Return header (ORDN): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, request: Request) -> CustomerReturnPage:
        # STEP 1 — Bolt list parameters: ``limit``, ``offset``, optional ``q`` prefix.
        limit, offset, search_prefix = get_list_pagination_for_request(self.request)
        queryset = ORDN.objects.all().order_by("-DocEntry")
        if not get_boolean_query_flag_is_true(self.request, "include_deleted"):
            queryset = queryset.filter(Canceled="N")
        if search_prefix:
            queryset = queryset.filter(
                Q(CardCode__istartswith=search_prefix) | Q(CardName__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return CustomerReturnPage(
            items=[customer_return_header_to_bolt_response(o) for o in rows],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: CustomerReturnCreateBody) -> CustomerReturnResponse:
        st = (data.DocStatus or "O").strip().upper()[:1] or "O"
        if st not in ("O", "C"):
            raise BadRequest(detail="DocStatus must be O or C.")
        header = ORDN(
            DocNum=data.DocNum,
            CardCode=data.CardCode.strip(),
            CardName=(data.CardName or "").strip(),
            NumAtCard=(data.NumAtCard or "").strip(),
            CntctPrsn=(data.CntctPrsn or "").strip(),
            DocCur=(data.DocCur or "").strip()[:15],
            DocStatus=st,
            DocDate=data.DocDate,
            DocDueDate=data.DocDueDate,
            TaxDate=data.TaxDate,
            DocTotal=Decimal(str(data.DocTotal or "0")),
            VatSum=Decimal(str(data.VatSum or "0")),
            DiscSum=Decimal(str(data.DiscSum or "0")),
            Comments=(data.Comments or "").strip(),
            SlpCode=data.SlpCode,
            OwnerCode=(data.OwnerCode or "").strip()[:50],
            U_UserFld1=(data.U_UserFld1 or "").strip()[:254],
            U_UserFld2=(data.U_UserFld2 or "").strip()[:254],
        )
        await header.asave()
        await async_recalculate_business_partner_rollups_for_card_codes(header.CardCode)
        return customer_return_header_to_bolt_response(header)


class CustomerReturnDetailView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> CustomerReturnResponse:
        try:
            o = await ORDN.objects.aget(pk=doc_entry)
        except ORDN.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return customer_return_header_to_bolt_response(o)

    async def patch(self, doc_entry: int, data: CustomerReturnPatchBody) -> CustomerReturnResponse:
        try:
            o = await ORDN.objects.aget(pk=doc_entry)
        except ORDN.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        old_cc = o.CardCode
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
        if data.U_UserFld1 is not None:
            o.U_UserFld1 = (data.U_UserFld1 or "").strip()[:254]
        if data.U_UserFld2 is not None:
            o.U_UserFld2 = (data.U_UserFld2 or "").strip()[:254]
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        await async_run_sync_callable_and_map_validation_error_to_bad_request(resync_all_return_lines, doc_entry)
        await async_recalculate_business_partner_rollups_for_card_codes(old_cc, o.CardCode)
        return customer_return_header_to_bolt_response(o)

    async def delete(self, doc_entry: int) -> CustomerReturnResponse:
        try:
            o = await ORDN.objects.aget(pk=doc_entry)
        except ORDN.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        old_cc = o.CardCode
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        await async_run_sync_callable_and_map_validation_error_to_bad_request(resync_all_return_lines, doc_entry)
        await async_recalculate_business_partner_rollups_for_card_codes(old_cc)
        return customer_return_header_to_bolt_response(o)


class CustomerReturnLineListCreateView(APIView):
    """Return lines (RDN1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, request: Request) -> CustomerReturnLinePage:
        # STEP 1 — Bolt list parameters: ``limit``, ``offset``, optional ``q`` prefix.
        limit, offset, search_prefix = get_list_pagination_for_request(self.request)
        doc_entry = get_optional_int_from_query(self.request, "doc_entry")
        queryset = RDN1.objects.all().order_by("header_id", "LineNum")
        if not get_boolean_query_flag_is_true(self.request, "include_deleted"):
            queryset = queryset.filter(Canceled="N", header__Canceled="N")
        if doc_entry is not None:
            queryset = queryset.filter(header_id=doc_entry)
        if search_prefix:
            queryset = queryset.filter(Q(ItemCode__istartswith=search_prefix) | Q(WhsCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return CustomerReturnLinePage(
            items=[customer_return_line_to_bolt_response(o) for o in rows],
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
            Dscription=(data.Dscription or "").strip(),
            Quantity=Decimal(str(data.Quantity)),
            Price=Decimal(str(data.Price or "0")),
            DiscPrcnt=Decimal(str(data.DiscPrcnt or "0")),
            LineTotal=Decimal(str(data.LineTotal or "0")),
            WhsCode=data.WhsCode.strip(),
            BaseType=data.BaseType,
            BaseEntry=data.BaseEntry,
            BaseLine=data.BaseLine,
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        await async_run_sync_callable_and_map_validation_error_to_bad_request(sync_return_line_stock, line.header_id, int(line.LineNum))
        hdr = await ORDN.objects.filter(pk=line.header_id).afirst()
        if hdr:
            await async_recalculate_business_partner_rollups_for_card_codes(hdr.CardCode)
        return customer_return_line_to_bolt_response(line)


class CustomerReturnLineDetailView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> CustomerReturnLineResponse:
        try:
            o = await RDN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RDN1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return customer_return_line_to_bolt_response(o)

    async def patch(self, doc_entry: int, line_num: int, data: CustomerReturnLinePatchBody) -> CustomerReturnLineResponse:
        try:
            o = await RDN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RDN1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and (
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
        if data.LineTotal is not None:
            o.LineTotal = Decimal(str(data.LineTotal))
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
        await async_run_sync_callable_and_map_validation_error_to_bad_request(sync_return_line_stock, doc_entry, int(line_num))
        await async_recalculate_business_partner_rollups_for_card_codes(o.header.CardCode)
        return customer_return_line_to_bolt_response(o)

    async def delete(self, doc_entry: int, line_num: int) -> CustomerReturnLineResponse:
        try:
            o = await RDN1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RDN1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if o.header.Canceled == "Y":
            raise BadRequest(detail="Cannot delete lines of a canceled document.")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        await async_run_sync_callable_and_map_validation_error_to_bad_request(sync_return_line_stock, doc_entry, int(line_num))
        await async_recalculate_business_partner_rollups_for_card_codes(o.header.CardCode)
        return customer_return_line_to_bolt_response(o)


class SalesInvoiceListCreateView(APIView):
    """A/R invoice header (OINV): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, request: Request) -> SalesInvoicePage:
        # STEP 1 — Bolt list parameters: ``limit``, ``offset``, optional ``q`` prefix.
        limit, offset, search_prefix = get_list_pagination_for_request(self.request)
        queryset = OINV.objects.all().order_by("-DocEntry")
        if not get_boolean_query_flag_is_true(self.request, "include_deleted"):
            queryset = queryset.filter(Canceled="N")
        if search_prefix:
            queryset = queryset.filter(
                Q(CardCode__istartswith=search_prefix) | Q(CardName__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return SalesInvoicePage(
            items=[sales_invoice_header_to_bolt_response(o) for o in rows],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: SalesInvoiceCreateBody) -> SalesInvoiceResponse:
        header = OINV(
            DocNum=data.DocNum,
            CardCode=data.CardCode.strip(),
            CardName=(data.CardName or "").strip(),
            NumAtCard=(data.NumAtCard or "").strip(),
            CntctPrsn=(data.CntctPrsn or "").strip(),
            DocCur=(data.DocCur or "").strip()[:15],
            DocDate=data.DocDate,
            DocDueDate=data.DocDueDate,
            TaxDate=data.TaxDate,
            DocTotal=Decimal(str(data.DocTotal or "0")),
            VatSum=Decimal(str(data.VatSum or "0")),
            DiscSum=Decimal(str(data.DiscSum or "0")),
            Comments=(data.Comments or "").strip(),
            SlpCode=data.SlpCode,
            OwnerCode=(data.OwnerCode or "").strip()[:50],
            U_UserFld1=(data.U_UserFld1 or "").strip()[:254],
            U_UserFld2=(data.U_UserFld2 or "").strip()[:254],
        )
        await header.asave()
        await async_recalculate_business_partner_rollups_for_card_codes(header.CardCode)
        await async_run_sync_callable_and_map_validation_error_to_bad_request(sync_ar_invoice_journal, int(header.DocEntry))
        return sales_invoice_header_to_bolt_response(header)


class SalesInvoiceDetailView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> SalesInvoiceResponse:
        try:
            o = await OINV.objects.aget(pk=doc_entry)
        except OINV.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return sales_invoice_header_to_bolt_response(o)

    async def patch(self, doc_entry: int, data: SalesInvoicePatchBody) -> SalesInvoiceResponse:
        try:
            o = await OINV.objects.aget(pk=doc_entry)
        except OINV.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        old_cc = o.CardCode
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
        if data.U_UserFld1 is not None:
            o.U_UserFld1 = (data.U_UserFld1 or "").strip()[:254]
        if data.U_UserFld2 is not None:
            o.U_UserFld2 = (data.U_UserFld2 or "").strip()[:254]
        if data.Canceled is not None:
            c = (data.Canceled or "N").strip().upper()[:1] or "N"
            if c not in ("Y", "N"):
                raise BadRequest(detail="Canceled must be Y or N.")
            o.Canceled = c
        await o.asave()
        await async_recalculate_business_partner_rollups_for_card_codes(old_cc, o.CardCode)
        await async_run_sync_callable_and_map_validation_error_to_bad_request(sync_ar_invoice_journal, int(doc_entry))
        return sales_invoice_header_to_bolt_response(o)

    async def delete(self, doc_entry: int) -> SalesInvoiceResponse:
        try:
            o = await OINV.objects.aget(pk=doc_entry)
        except OINV.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and getattr(o, "Canceled", "N") == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        old_cc = o.CardCode
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        await async_recalculate_business_partner_rollups_for_card_codes(old_cc)
        await async_run_sync_callable_and_map_validation_error_to_bad_request(sync_ar_invoice_journal, int(doc_entry))
        return sales_invoice_header_to_bolt_response(o)


class SalesInvoiceLineListCreateView(APIView):
    """A/R invoice lines (INV1): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, request: Request) -> SalesInvoiceLinePage:
        # STEP 1 — Bolt list parameters: ``limit``, ``offset``, optional ``q`` prefix.
        limit, offset, search_prefix = get_list_pagination_for_request(self.request)
        doc_entry = get_optional_int_from_query(self.request, "doc_entry")
        queryset = INV1.objects.all().order_by("header_id", "LineNum")
        if not get_boolean_query_flag_is_true(self.request, "include_deleted"):
            queryset = queryset.filter(Canceled="N", header__Canceled="N")
        if doc_entry is not None:
            queryset = queryset.filter(header_id=doc_entry)
        if search_prefix:
            queryset = queryset.filter(Q(ItemCode__istartswith=search_prefix))
        rows = await sync_to_async(list)(queryset[offset : offset + limit])
        return SalesInvoiceLinePage(
            items=[sales_invoice_line_to_bolt_response(o) for o in rows],
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
            Dscription=(data.Dscription or "").strip(),
            Quantity=Decimal(str(data.Quantity)),
            Price=Decimal(str(data.Price or "0")),
            DiscPrcnt=Decimal(str(data.DiscPrcnt or "0")),
            LineTotal=Decimal(str(data.LineTotal or "0")),
            WhsCode=(data.WhsCode or "").strip(),
            BaseType=data.BaseType,
            BaseEntry=data.BaseEntry,
            BaseLine=data.BaseLine,
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        await async_recalculate_business_partner_rollups_for_card_codes(hdr.CardCode)
        await async_run_sync_callable_and_map_validation_error_to_bad_request(sync_ar_invoice_journal, int(hdr.DocEntry))
        return sales_invoice_line_to_bolt_response(line)


class SalesInvoiceLineDetailView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> SalesInvoiceLineResponse:
        try:
            o = await INV1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except INV1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return sales_invoice_line_to_bolt_response(o)

    async def patch(self, doc_entry: int, line_num: int, data: SalesInvoiceLinePatchBody) -> SalesInvoiceLineResponse:
        try:
            o = await INV1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except INV1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and (
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
        if data.LineTotal is not None:
            o.LineTotal = Decimal(str(data.LineTotal))
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
        await async_recalculate_business_partner_rollups_for_card_codes(o.header.CardCode)
        await async_run_sync_callable_and_map_validation_error_to_bad_request(sync_ar_invoice_journal, int(doc_entry))
        return sales_invoice_line_to_bolt_response(o)

    async def delete(self, doc_entry: int, line_num: int) -> SalesInvoiceLineResponse:
        try:
            o = await INV1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except INV1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        if not get_boolean_query_flag_is_true(self.request, "include_deleted") and (
            getattr(o, "Canceled", "N") == "Y" or getattr(o.header, "Canceled", "N") == "Y"
        ):
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if o.header.Canceled == "Y":
            raise BadRequest(detail="Cannot delete lines of a canceled document.")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        await async_recalculate_business_partner_rollups_for_card_codes(o.header.CardCode)
        await async_run_sync_callable_and_map_validation_error_to_bad_request(sync_ar_invoice_journal, int(doc_entry))
        return sales_invoice_line_to_bolt_response(o)


def attach_sales_routes(api: BoltAPI) -> None:
    """Register Sales A/R Bolt routes."""
    tag = ["sales"]
    # Human-readable paths (legacy SAP-style paths kept for compatibility).
    api.view(SALES_API_PREFIX + "/quotations", methods=["GET", "POST"], status_code=200, tags=tag)(SalesQuotationListCreateView)
    api.view(SALES_API_PREFIX + "/quotations/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesQuotationDetailView
    )
    api.view(SALES_API_PREFIX + "/quotation-lines", methods=["GET", "POST"], status_code=200, tags=tag)(SalesQuotationLineListCreateView)
    api.view(
        SALES_API_PREFIX + "/quotation-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(SalesQuotationLineDetailView)
    api.view(SALES_API_PREFIX + "/sales-orders", methods=["GET", "POST"], status_code=200, tags=tag)(SalesOrderListCreateView)
    api.view(SALES_API_PREFIX + "/sales-orders/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesOrderDetailView
    )
    api.view(SALES_API_PREFIX + "/sales-order-lines", methods=["GET", "POST"], status_code=200, tags=tag)(SalesOrderLineListCreateView)
    api.view(
        SALES_API_PREFIX + "/sales-order-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(SalesOrderLineDetailView)
    api.view(SALES_API_PREFIX + "/deliveries", methods=["GET", "POST"], status_code=200, tags=tag)(DeliveryNoteListCreateView)
    api.view(SALES_API_PREFIX + "/deliveries/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        DeliveryNoteDetailView
    )
    api.view(SALES_API_PREFIX + "/delivery-lines", methods=["GET", "POST"], status_code=200, tags=tag)(DeliveryLineListCreateView)
    api.view(
        SALES_API_PREFIX + "/delivery-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(DeliveryLineDetailView)
    api.view(SALES_API_PREFIX + "/customer-returns", methods=["GET", "POST"], status_code=200, tags=tag)(CustomerReturnListCreateView)
    api.view(SALES_API_PREFIX + "/customer-returns/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        CustomerReturnDetailView
    )
    api.view(SALES_API_PREFIX + "/customer-return-lines", methods=["GET", "POST"], status_code=200, tags=tag)(CustomerReturnLineListCreateView)
    api.view(
        SALES_API_PREFIX + "/customer-return-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(CustomerReturnLineDetailView)
    api.view(SALES_API_PREFIX + "/invoices", methods=["GET", "POST"], status_code=200, tags=tag)(SalesInvoiceListCreateView)
    api.view(SALES_API_PREFIX + "/invoices/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesInvoiceDetailView
    )
    api.view(SALES_API_PREFIX + "/invoice-lines", methods=["GET", "POST"], status_code=200, tags=tag)(SalesInvoiceLineListCreateView)
    api.view(
        SALES_API_PREFIX + "/invoice-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(SalesInvoiceLineDetailView)
    api.view(SALES_API_PREFIX + "/oqut", methods=["GET", "POST"], status_code=200, tags=tag)(SalesQuotationListCreateView)
    api.view(SALES_API_PREFIX + "/oqut/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesQuotationDetailView
    )
    api.view(SALES_API_PREFIX + "/qut1", methods=["GET", "POST"], status_code=200, tags=tag)(SalesQuotationLineListCreateView)
    api.view(SALES_API_PREFIX + "/qut1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesQuotationLineDetailView
    )
    api.view(SALES_API_PREFIX + "/ordr", methods=["GET", "POST"], status_code=200, tags=tag)(SalesOrderListCreateView)
    api.view(SALES_API_PREFIX + "/ordr/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesOrderDetailView
    )
    api.view(SALES_API_PREFIX + "/rdr1", methods=["GET", "POST"], status_code=200, tags=tag)(SalesOrderLineListCreateView)
    api.view(SALES_API_PREFIX + "/rdr1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesOrderLineDetailView
    )
    api.view(SALES_API_PREFIX + "/odln", methods=["GET", "POST"], status_code=200, tags=tag)(DeliveryNoteListCreateView)
    api.view(SALES_API_PREFIX + "/odln/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        DeliveryNoteDetailView
    )
    api.view(SALES_API_PREFIX + "/dln1", methods=["GET", "POST"], status_code=200, tags=tag)(DeliveryLineListCreateView)
    api.view(SALES_API_PREFIX + "/dln1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        DeliveryLineDetailView
    )
    api.view(SALES_API_PREFIX + "/ordn", methods=["GET", "POST"], status_code=200, tags=tag)(CustomerReturnListCreateView)
    api.view(SALES_API_PREFIX + "/ordn/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        CustomerReturnDetailView
    )
    api.view(SALES_API_PREFIX + "/rdn1", methods=["GET", "POST"], status_code=200, tags=tag)(CustomerReturnLineListCreateView)
    api.view(SALES_API_PREFIX + "/rdn1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        CustomerReturnLineDetailView
    )
    api.view(SALES_API_PREFIX + "/oinv", methods=["GET", "POST"], status_code=200, tags=tag)(SalesInvoiceListCreateView)
    api.view(SALES_API_PREFIX + "/oinv/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesInvoiceDetailView
    )
    api.view(SALES_API_PREFIX + "/inv1", methods=["GET", "POST"], status_code=200, tags=tag)(SalesInvoiceLineListCreateView)
    api.view(SALES_API_PREFIX + "/inv1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        SalesInvoiceLineDetailView
    )
