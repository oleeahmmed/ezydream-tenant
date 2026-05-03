"""
Purchase — ইনপুট ও আউটপুট সিরিয়ালাইজার (``django_bolt_guide.md`` ধারণা)।

নামগুলো বিশেষ্য (``PurchaseRequestResponse``, ``PurchaseOrderPage``, …)।
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated, Any

from django_bolt.serializers import Serializer, field
from django_bolt.serializers.nested import Nested

PAGE_MAX_ITEMS = 100


class PurchaseRequestResponse(Serializer):
    DocEntry: int
    DocNum: int | None = field(default=None)
    DocStatus: str
    Requester: str
    DocDate: date
    DocDueDate: date
    Canceled: str




class PurchaseRequestPage(Serializer):
    items: Annotated[list[PurchaseRequestResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class PurchaseRequestCreateBody(Serializer):
    DocNum: int | None = field(default=None)
    DocStatus: str = field(default="O")
    Requester: str
    DocDate: date
    DocDueDate: date




class PurchaseRequestPatchBody(Serializer):
    DocNum: int | None = field(default=None)
    DocStatus: str | None = field(default=None)
    Requester: str | None = field(default=None)
    DocDate: date | None = field(default=None)
    DocDueDate: date | None = field(default=None)
    Canceled: str | None = field(default=None)




class PurchaseRequestLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Dscription: str = field(default="")
    Quantity: str
    WhsCode: str
    LineStatus: str
    Canceled: str




class PurchaseRequestLinePage(Serializer):
    items: Annotated[list[PurchaseRequestLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class PurchaseRequestLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Dscription: str = field(default="")
    Quantity: str
    WhsCode: str
    LineStatus: str = field(default="O")




class PurchaseRequestLinePatchBody(Serializer):
    ItemCode: str | None = field(default=None)
    Dscription: str | None = field(default=None)
    Quantity: str | None = field(default=None)
    WhsCode: str | None = field(default=None)
    LineStatus: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class PurchaseOrderResponse(Serializer):
    DocEntry: int
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    DocStatus: str
    DocDate: date
    DocTotal: str
    Canceled: str




class PurchaseOrderPage(Serializer):
    items: Annotated[list[PurchaseOrderResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class PurchaseOrderCreateBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    DocStatus: str = field(default="O")
    DocDate: date
    DocTotal: str = field(default="0")




class PurchaseOrderPatchBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str | None = field(default=None)
    CardName: str | None = field(default=None)
    DocStatus: str | None = field(default=None)
    DocDate: date | None = field(default=None)
    DocTotal: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class PurchaseOrderLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Quantity: str
    Price: str
    WhsCode: str
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str




class PurchaseOrderLinePage(Serializer):
    items: Annotated[list[PurchaseOrderLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class PurchaseOrderLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Quantity: str
    Price: str = field(default="0")
    WhsCode: str
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)




class PurchaseOrderLinePatchBody(Serializer):
    ItemCode: str | None = field(default=None)
    Quantity: str | None = field(default=None)
    Price: str | None = field(default=None)
    WhsCode: str | None = field(default=None)
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str | None = field(default=None)




class GoodsReceiptResponse(Serializer):
    DocEntry: int
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    DocDate: date
    DocStatus: str
    Canceled: str




class GoodsReceiptPage(Serializer):
    items: Annotated[list[GoodsReceiptResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class GoodsReceiptCreateBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    DocDate: date
    DocStatus: str = field(default="O")




class GoodsReceiptPatchBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str | None = field(default=None)
    CardName: str | None = field(default=None)
    DocDate: date | None = field(default=None)
    DocStatus: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class GoodsReceiptLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Quantity: str
    Price: str
    WhsCode: str
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str




class GoodsReceiptLinePage(Serializer):
    items: Annotated[list[GoodsReceiptLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class GoodsReceiptLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Quantity: str
    Price: str = field(default="0")
    WhsCode: str
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)




class GoodsReceiptLinePatchBody(Serializer):
    ItemCode: str | None = field(default=None)
    Quantity: str | None = field(default=None)
    Price: str | None = field(default=None)
    WhsCode: str | None = field(default=None)
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str | None = field(default=None)




class VendorReturnResponse(Serializer):
    DocEntry: int
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    DocDate: date
    Canceled: str




class VendorReturnPage(Serializer):
    items: Annotated[list[VendorReturnResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class VendorReturnCreateBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    DocDate: date




class VendorReturnPatchBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str | None = field(default=None)
    CardName: str | None = field(default=None)
    DocDate: date | None = field(default=None)
    DocStatus: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class VendorReturnLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Quantity: str
    Price: str
    WhsCode: str
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str




class VendorReturnLinePage(Serializer):
    items: Annotated[list[VendorReturnLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class VendorReturnLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Quantity: str
    Price: str = field(default="0")
    WhsCode: str
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)




class VendorReturnLinePatchBody(Serializer):
    ItemCode: str | None = field(default=None)
    Quantity: str | None = field(default=None)
    Price: str | None = field(default=None)
    WhsCode: str | None = field(default=None)
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str | None = field(default=None)




class ApInvoiceResponse(Serializer):
    DocEntry: int
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    DocDate: date
    DocTotal: str
    VatSum: str
    Canceled: str




class ApInvoicePage(Serializer):
    items: Annotated[list[ApInvoiceResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class ApInvoiceCreateBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str
    CardName: str = field(default="")
    DocDate: date
    DocTotal: str = field(default="0")
    VatSum: str = field(default="0")




class ApInvoicePatchBody(Serializer):
    DocNum: int | None = field(default=None)
    CardCode: str | None = field(default=None)
    CardName: str | None = field(default=None)
    DocDate: date | None = field(default=None)
    DocTotal: str | None = field(default=None)
    VatSum: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class ApInvoiceLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Quantity: str
    Price: str
    LineTotal: str
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    Canceled: str




class ApInvoiceLinePage(Serializer):
    items: Annotated[list[ApInvoiceLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class ApInvoiceLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Quantity: str
    Price: str = field(default="0")
    LineTotal: str = field(default="0")
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)




class ApInvoiceLinePatchBody(Serializer):
    ItemCode: str | None = field(default=None)
    Quantity: str | None = field(default=None)
    Price: str | None = field(default=None)
    LineTotal: str | None = field(default=None)
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    Canceled: str | None = field(default=None)
