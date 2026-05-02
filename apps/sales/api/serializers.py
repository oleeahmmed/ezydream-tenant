"""
Sales — ইনপুট ও আউটপুট সিরিয়ালাইজার (``django_bolt_guide.md`` ধারণা)।

নামগুলো বিশেষ্য (``SalesQuotationResponse``, ``SalesOrderPage``, …)।
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated, Any

from django_bolt.serializers import Serializer, field
from django_bolt.serializers.nested import Nested

PAGE_MAX_ITEMS = 100


class SalesQuotationResponse(Serializer):
    DocEntry: int
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    NumAtCard: str = field(default="")
    CntctPrsn: str = field(default="")
    DocCur: str = field(default="")
    DocStatus: str
    DocDate: date
    DocDueDate: date | None = field(default=None)
    TaxDate: date | None = field(default=None)
    DocTotal: str
    VatSum: str = field(default="0")
    DiscSum: str = field(default="0")
    Comments: str = field(default="")
    SlpCode: int | None = field(default=None)
    OwnerCode: str = field(default="")
    Canceled: str




class SalesQuotationPage(Serializer):
    items: Annotated[list[SalesQuotationResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class SalesQuotationCreateBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    NumAtCard: str = field(default="")
    CntctPrsn: str = field(default="")
    DocCur: str = field(default="")
    DocStatus: str = field(default="O")
    DocDate: date
    DocDueDate: date | None = field(default=None)
    TaxDate: date | None = field(default=None)
    DocTotal: str = field(default="0")
    VatSum: str = field(default="0")
    DiscSum: str = field(default="0")
    Comments: str = field(default="")
    SlpCode: int | None = field(default=None)
    OwnerCode: str = field(default="")




class SalesQuotationPatchBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str | None = field(default=None)
    CardName: str | None = field(default=None)
    NumAtCard: str | None = field(default=None)
    CntctPrsn: str | None = field(default=None)
    DocCur: str | None = field(default=None)
    DocStatus: str | None = field(default=None)
    DocDate: date | None = field(default=None)
    DocDueDate: date | None = field(default=None)
    TaxDate: date | None = field(default=None)
    DocTotal: str | None = field(default=None)
    VatSum: str | None = field(default=None)
    DiscSum: str | None = field(default=None)
    Comments: str | None = field(default=None)
    SlpCode: int | None = field(default=None)
    OwnerCode: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class SalesQuotationLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Dscription: str = field(default="")
    Quantity: str
    Price: str
    DiscPrcnt: str = field(default="0")
    WhsCode: str
    LineTotal: str
    Canceled: str




class SalesQuotationLinePage(Serializer):
    items: Annotated[list[SalesQuotationLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class SalesQuotationLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Dscription: str = field(default="")
    Quantity: str
    Price: str = field(default="0")
    DiscPrcnt: str = field(default="0")
    WhsCode: str
    LineTotal: str = field(default="0")




class SalesQuotationLinePatchBody(Serializer):
    ItemCode: str | None = field(default=None)
    Dscription: str | None = field(default=None)
    Quantity: str | None = field(default=None)
    Price: str | None = field(default=None)
    DiscPrcnt: str | None = field(default=None)
    WhsCode: str | None = field(default=None)
    LineTotal: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class SalesOrderResponse(Serializer):
    DocEntry: int
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    NumAtCard: str = field(default="")
    CntctPrsn: str = field(default="")
    DocCur: str = field(default="")
    DocStatus: str
    DocDate: date
    DocDueDate: date | None = field(default=None)
    TaxDate: date | None = field(default=None)
    DocTotal: str = field(default="0")
    VatSum: str = field(default="0")
    DiscSum: str = field(default="0")
    Comments: str = field(default="")
    SlpCode: int | None = field(default=None)
    OwnerCode: str = field(default="")
    Canceled: str




class SalesOrderPage(Serializer):
    items: Annotated[list[SalesOrderResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class SalesOrderCreateBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    NumAtCard: str = field(default="")
    CntctPrsn: str = field(default="")
    DocCur: str = field(default="")
    DocStatus: str = field(default="O")
    DocDate: date
    DocDueDate: date | None = field(default=None)
    TaxDate: date | None = field(default=None)
    DocTotal: str = field(default="0")
    VatSum: str = field(default="0")
    DiscSum: str = field(default="0")
    Comments: str = field(default="")
    SlpCode: int | None = field(default=None)
    OwnerCode: str = field(default="")




class SalesOrderPatchBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str | None = field(default=None)
    CardName: str | None = field(default=None)
    NumAtCard: str | None = field(default=None)
    CntctPrsn: str | None = field(default=None)
    DocCur: str | None = field(default=None)
    DocStatus: str | None = field(default=None)
    DocDate: date | None = field(default=None)
    DocDueDate: date | None = field(default=None)
    TaxDate: date | None = field(default=None)
    DocTotal: str | None = field(default=None)
    VatSum: str | None = field(default=None)
    DiscSum: str | None = field(default=None)
    Comments: str | None = field(default=None)
    SlpCode: int | None = field(default=None)
    OwnerCode: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class SalesOrderLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Dscription: str = field(default="")
    Quantity: str
    Price: str
    DiscPrcnt: str = field(default="0")
    WhsCode: str
    LineTotal: str = field(default="0")
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str




class SalesOrderLinePage(Serializer):
    items: Annotated[list[SalesOrderLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class SalesOrderLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Dscription: str = field(default="")
    Quantity: str
    Price: str = field(default="0")
    DiscPrcnt: str = field(default="0")
    WhsCode: str
    LineTotal: str = field(default="0")
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)




class SalesOrderLinePatchBody(Serializer):
    ItemCode: str | None = field(default=None)
    Dscription: str | None = field(default=None)
    Quantity: str | None = field(default=None)
    Price: str | None = field(default=None)
    DiscPrcnt: str | None = field(default=None)
    WhsCode: str | None = field(default=None)
    LineTotal: str | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str | None = field(default=None)




class DeliveryNoteResponse(Serializer):
    DocEntry: int
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    NumAtCard: str = field(default="")
    CntctPrsn: str = field(default="")
    DocCur: str = field(default="")
    DocStatus: str
    DocDate: date
    DocDueDate: date | None = field(default=None)
    TaxDate: date | None = field(default=None)
    DocTotal: str = field(default="0")
    VatSum: str = field(default="0")
    DiscSum: str = field(default="0")
    Comments: str = field(default="")
    SlpCode: int | None = field(default=None)
    OwnerCode: str = field(default="")
    Canceled: str




class DeliveryNotePage(Serializer):
    items: Annotated[list[DeliveryNoteResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class DeliveryNoteCreateBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    NumAtCard: str = field(default="")
    CntctPrsn: str = field(default="")
    DocCur: str = field(default="")
    DocStatus: str = field(default="O")
    DocDate: date
    DocDueDate: date | None = field(default=None)
    TaxDate: date | None = field(default=None)
    DocTotal: str = field(default="0")
    VatSum: str = field(default="0")
    DiscSum: str = field(default="0")
    Comments: str = field(default="")
    SlpCode: int | None = field(default=None)
    OwnerCode: str = field(default="")




class DeliveryNotePatchBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str | None = field(default=None)
    CardName: str | None = field(default=None)
    NumAtCard: str | None = field(default=None)
    CntctPrsn: str | None = field(default=None)
    DocCur: str | None = field(default=None)
    DocStatus: str | None = field(default=None)
    DocDate: date | None = field(default=None)
    DocDueDate: date | None = field(default=None)
    TaxDate: date | None = field(default=None)
    DocTotal: str | None = field(default=None)
    VatSum: str | None = field(default=None)
    DiscSum: str | None = field(default=None)
    Comments: str | None = field(default=None)
    SlpCode: int | None = field(default=None)
    OwnerCode: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class DeliveryLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Dscription: str = field(default="")
    Quantity: str
    Price: str
    DiscPrcnt: str = field(default="0")
    LineTotal: str = field(default="0")
    WhsCode: str
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str




class DeliveryLinePage(Serializer):
    items: Annotated[list[DeliveryLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class DeliveryLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Dscription: str = field(default="")
    Quantity: str
    Price: str = field(default="0")
    DiscPrcnt: str = field(default="0")
    LineTotal: str = field(default="0")
    WhsCode: str
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)




class DeliveryLinePatchBody(Serializer):
    ItemCode: str | None = field(default=None)
    Dscription: str | None = field(default=None)
    Quantity: str | None = field(default=None)
    Price: str | None = field(default=None)
    DiscPrcnt: str | None = field(default=None)
    LineTotal: str | None = field(default=None)
    WhsCode: str | None = field(default=None)
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str | None = field(default=None)




class CustomerReturnResponse(Serializer):
    DocEntry: int
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    NumAtCard: str = field(default="")
    CntctPrsn: str = field(default="")
    DocCur: str = field(default="")
    DocStatus: str
    DocDate: date
    DocDueDate: date | None = field(default=None)
    TaxDate: date | None = field(default=None)
    DocTotal: str = field(default="0")
    VatSum: str = field(default="0")
    DiscSum: str = field(default="0")
    Comments: str = field(default="")
    SlpCode: int | None = field(default=None)
    OwnerCode: str = field(default="")
    Canceled: str




class CustomerReturnPage(Serializer):
    items: Annotated[list[CustomerReturnResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class CustomerReturnCreateBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    NumAtCard: str = field(default="")
    CntctPrsn: str = field(default="")
    DocCur: str = field(default="")
    DocStatus: str = field(default="O")
    DocDate: date
    DocDueDate: date | None = field(default=None)
    TaxDate: date | None = field(default=None)
    DocTotal: str = field(default="0")
    VatSum: str = field(default="0")
    DiscSum: str = field(default="0")
    Comments: str = field(default="")
    SlpCode: int | None = field(default=None)
    OwnerCode: str = field(default="")




class CustomerReturnPatchBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str | None = field(default=None)
    CardName: str | None = field(default=None)
    NumAtCard: str | None = field(default=None)
    CntctPrsn: str | None = field(default=None)
    DocCur: str | None = field(default=None)
    DocStatus: str | None = field(default=None)
    DocDate: date | None = field(default=None)
    DocDueDate: date | None = field(default=None)
    TaxDate: date | None = field(default=None)
    DocTotal: str | None = field(default=None)
    VatSum: str | None = field(default=None)
    DiscSum: str | None = field(default=None)
    Comments: str | None = field(default=None)
    SlpCode: int | None = field(default=None)
    OwnerCode: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class CustomerReturnLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Dscription: str = field(default="")
    Quantity: str
    Price: str
    DiscPrcnt: str = field(default="0")
    LineTotal: str = field(default="0")
    WhsCode: str
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str




class CustomerReturnLinePage(Serializer):
    items: Annotated[list[CustomerReturnLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class CustomerReturnLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Dscription: str = field(default="")
    Quantity: str
    Price: str = field(default="0")
    DiscPrcnt: str = field(default="0")
    LineTotal: str = field(default="0")
    WhsCode: str
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)




class CustomerReturnLinePatchBody(Serializer):
    ItemCode: str | None = field(default=None)
    Dscription: str | None = field(default=None)
    Quantity: str | None = field(default=None)
    Price: str | None = field(default=None)
    DiscPrcnt: str | None = field(default=None)
    LineTotal: str | None = field(default=None)
    WhsCode: str | None = field(default=None)
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str | None = field(default=None)




class SalesInvoiceResponse(Serializer):
    DocEntry: int
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    NumAtCard: str = field(default="")
    CntctPrsn: str = field(default="")
    DocCur: str = field(default="")
    DocDate: date
    DocDueDate: date | None = field(default=None)
    TaxDate: date | None = field(default=None)
    DocTotal: str
    VatSum: str
    DiscSum: str = field(default="0")
    Comments: str = field(default="")
    SlpCode: int | None = field(default=None)
    OwnerCode: str = field(default="")
    Canceled: str




class SalesInvoicePage(Serializer):
    items: Annotated[list[SalesInvoiceResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class SalesInvoiceCreateBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    NumAtCard: str = field(default="")
    CntctPrsn: str = field(default="")
    DocCur: str = field(default="")
    DocDate: date
    DocDueDate: date | None = field(default=None)
    TaxDate: date | None = field(default=None)
    DocTotal: str = field(default="0")
    VatSum: str = field(default="0")
    DiscSum: str = field(default="0")
    Comments: str = field(default="")
    SlpCode: int | None = field(default=None)
    OwnerCode: str = field(default="")




class SalesInvoicePatchBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str | None = field(default=None)
    CardName: str | None = field(default=None)
    NumAtCard: str | None = field(default=None)
    CntctPrsn: str | None = field(default=None)
    DocCur: str | None = field(default=None)
    DocDate: date | None = field(default=None)
    DocDueDate: date | None = field(default=None)
    TaxDate: date | None = field(default=None)
    DocTotal: str | None = field(default=None)
    VatSum: str | None = field(default=None)
    DiscSum: str | None = field(default=None)
    Comments: str | None = field(default=None)
    SlpCode: int | None = field(default=None)
    OwnerCode: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class SalesInvoiceLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Dscription: str = field(default="")
    Quantity: str
    Price: str
    DiscPrcnt: str = field(default="0")
    LineTotal: str
    WhsCode: str = field(default="")
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str




class SalesInvoiceLinePage(Serializer):
    items: Annotated[list[SalesInvoiceLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class SalesInvoiceLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Dscription: str = field(default="")
    Quantity: str
    Price: str = field(default="0")
    DiscPrcnt: str = field(default="0")
    LineTotal: str = field(default="0")
    WhsCode: str = field(default="")
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)




class SalesInvoiceLinePatchBody(Serializer):
    ItemCode: str | None = field(default=None)
    Dscription: str | None = field(default=None)
    Quantity: str | None = field(default=None)
    Price: str | None = field(default=None)
    DiscPrcnt: str | None = field(default=None)
    LineTotal: str | None = field(default=None)
    WhsCode: str | None = field(default=None)
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str | None = field(default=None)


# ═══════════════════════════════════════════════════════════════════════════
