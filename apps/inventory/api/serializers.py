"""
Inventory — ইনপুট ও আউটপুট সিরিয়ালাইজার (``django_bolt_guide.md`` ধারণা)।

নামগুলো বিশেষ্য (``ItemGroupResponse``, ``StockTransferPage``, …)।
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Any

from django_bolt.serializers import Serializer, field
from django_bolt.serializers.nested import Nested

PAGE_MAX_ITEMS = 100


class ItemGroupResponse(Serializer):
    ItmsGrpCod: int
    ItmsGrpNam: str
    Canceled: str




class ItemGroupPage(Serializer):
    items: Annotated[list[ItemGroupResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class ItemGroupCreateBody(Serializer):
    ItmsGrpCod: int
    ItmsGrpNam: str




class ItemGroupPatchBody(Serializer):
    ItmsGrpNam: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class ItemResponse(Serializer):
    ItemCode: str
    ItemName: str
    ItmsGrpCod: int
    ItmsGrpNam: str = field(default="")
    InvntItem: str
    OnHand: str
    IsCommited: str
    OnOrder: str
    ByWh: str
    DfltWH: str = field(default="")
    FrgnName: str = field(default="")
    CodeBars: str = field(default="")
    SalItem: str = field(default="Y")
    PrchseItem: str = field(default="Y")
    SalUnitMsr: str = field(default="")
    BuyUnitMsr: str = field(default="")
    ValidFor: str




class ItemPage(Serializer):
    items: Annotated[list[ItemResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class ItemCreateBody(Serializer):
    ItemCode: str
    ItemName: str
    ItmsGrpCod: int
    InvntItem: str = field(default="Y")
    OnHand: str = field(default="0")
    IsCommited: str = field(default="0")
    OnOrder: str = field(default="0")
    ByWh: str = field(default="N")
    DfltWH: str = field(default="")
    FrgnName: str = field(default="")
    CodeBars: str = field(default="")
    SalItem: str = field(default="Y")
    PrchseItem: str = field(default="Y")
    SalUnitMsr: str = field(default="")
    BuyUnitMsr: str = field(default="")




class ItemPatchBody(Serializer):
    ItemName: str | None = field(default=None)
    ItmsGrpCod: int | None = field(default=None)
    InvntItem: str | None = field(default=None)
    OnHand: str | None = field(default=None)
    IsCommited: str | None = field(default=None)
    OnOrder: str | None = field(default=None)
    ByWh: str | None = field(default=None)
    DfltWH: str | None = field(default=None)
    FrgnName: str | None = field(default=None)
    CodeBars: str | None = field(default=None)
    SalItem: str | None = field(default=None)
    PrchseItem: str | None = field(default=None)
    SalUnitMsr: str | None = field(default=None)
    BuyUnitMsr: str | None = field(default=None)
    ValidFor: str | None = field(default=None)




class ItemWarehouseStockResponse(Serializer):
    ItemCode: str
    WhsCode: str
    OnHand: str
    IsCommited: str
    AvgPrice: str
    OrderQty: str = field(default="0")
    MinStock: str = field(default="0")
    MaxStock: str = field(default="0")
    Locked: str = field(default="N")
    Canceled: str




class ItemWarehouseStockPage(Serializer):
    items: Annotated[list[ItemWarehouseStockResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class ItemWarehouseStockCreateBody(Serializer):
    ItemCode: str
    WhsCode: str
    OnHand: str = field(default="0")
    IsCommited: str = field(default="0")
    AvgPrice: str = field(default="0")
    OrderQty: str = field(default="0")
    MinStock: str = field(default="0")
    MaxStock: str = field(default="0")
    Locked: str = field(default="N")




class ItemWarehouseStockPatchBody(Serializer):
    OnHand: str | None = field(default=None)
    IsCommited: str | None = field(default=None)
    AvgPrice: str | None = field(default=None)
    OrderQty: str | None = field(default=None)
    MinStock: str | None = field(default=None)
    MaxStock: str | None = field(default=None)
    Locked: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class UnitOfMeasureResponse(Serializer):
    UomEntry: int
    UomCode: str
    UomName: str
    Locked: str
    DataSource: str




class UnitOfMeasurePage(Serializer):
    items: Annotated[list[UnitOfMeasureResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class UnitOfMeasureCreateBody(Serializer):
    UomCode: str
    UomName: str
    Locked: str = field(default="N")
    DataSource: str = field(default="N")




class UnitOfMeasurePatchBody(Serializer):
    UomCode: str | None = field(default=None)
    UomName: str | None = field(default=None)
    Locked: str | None = field(default=None)
    DataSource: str | None = field(default=None)




class StockTransferRequestResponse(Serializer):
    DocEntry: int
    DocNum: int | None = field(default=None)
    DocDate: date
    Filler: str
    Comments: str = field(default="")
    JrnlMemo: str = field(default="")
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")
    Canceled: str




class StockTransferRequestPage(Serializer):
    items: Annotated[list[StockTransferRequestResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class StockTransferRequestCreateBody(Serializer):
    DocNum: int | None = field(default=None)
    DocDate: date
    Filler: str
    Comments: str = field(default="")
    JrnlMemo: str = field(default="")
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")




class StockTransferRequestPatchBody(Serializer):
    DocNum: int | None = field(default=None)
    DocDate: date | None = field(default=None)
    Filler: str | None = field(default=None)
    Comments: str | None = field(default=None)
    JrnlMemo: str | None = field(default=None)
    U_UserFld1: str | None = field(default=None)
    U_UserFld2: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class StockTransferRequestLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Quantity: str
    OpenQty: str
    Price: str
    FromWhsCod: str
    WhsCode: str
    LineStatus: str
    TargetType: int
    TrgetEntry: int | None = field(default=None)
    BaseRef: str = field(default="")
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str




class StockTransferRequestLinePage(Serializer):
    items: Annotated[list[StockTransferRequestLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class StockTransferRequestLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Quantity: str
    OpenQty: str | None = field(default=None)
    Price: str = field(default="0")
    FromWhsCod: str
    WhsCode: str
    LineStatus: str = field(default="O")
    TargetType: int = field(default=-1)
    TrgetEntry: int | None = field(default=None)
    BaseRef: str = field(default="")
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)




class StockTransferRequestLinePatchBody(Serializer):
    ItemCode: str | None = field(default=None)
    Quantity: str | None = field(default=None)
    OpenQty: str | None = field(default=None)
    Price: str | None = field(default=None)
    FromWhsCod: str | None = field(default=None)
    WhsCode: str | None = field(default=None)
    LineStatus: str | None = field(default=None)
    TargetType: int | None = field(default=None)
    TrgetEntry: int | None = field(default=None)
    BaseRef: str | None = field(default=None)
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str | None = field(default=None)




class StockTransferResponse(Serializer):
    DocEntry: int
    DocNum: int | None = field(default=None)
    DocDate: date
    Filler: str
    Comments: str = field(default="")
    JrnlMemo: str = field(default="")
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")
    Canceled: str




class StockTransferPage(Serializer):
    items: Annotated[list[StockTransferResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class StockTransferCreateBody(Serializer):
    DocNum: int | None = field(default=None)
    DocDate: date
    Filler: str
    Comments: str = field(default="")
    JrnlMemo: str = field(default="")
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")




class StockTransferPatchBody(Serializer):
    DocNum: int | None = field(default=None)
    DocDate: date | None = field(default=None)
    Filler: str | None = field(default=None)
    Comments: str | None = field(default=None)
    JrnlMemo: str | None = field(default=None)
    U_UserFld1: str | None = field(default=None)
    U_UserFld2: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class StockTransferLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Quantity: str
    FromWhsCod: str
    WhsCode: str
    Price: str
    Canceled: str




class StockTransferLinePage(Serializer):
    items: Annotated[list[StockTransferLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class StockTransferLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Quantity: str
    FromWhsCod: str = field(default="")
    WhsCode: str
    Price: str = field(default="0")




class StockTransferLinePatchBody(Serializer):
    ItemCode: str | None = field(default=None)
    Quantity: str | None = field(default=None)
    FromWhsCod: str | None = field(default=None)
    WhsCode: str | None = field(default=None)
    Price: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class InventoryGoodsReceiptResponse(Serializer):
    DocEntry: int
    DocNum: int | None = field(default=None)
    DocDate: date
    Comments: str = field(default="")
    JrnlMemo: str = field(default="")
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")
    Canceled: str




class InventoryGoodsReceiptPage(Serializer):
    items: Annotated[list[InventoryGoodsReceiptResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class InventoryGoodsReceiptCreateBody(Serializer):
    DocNum: int | None = field(default=None)
    DocDate: date
    Comments: str = field(default="")
    JrnlMemo: str = field(default="")
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")




class InventoryGoodsReceiptPatchBody(Serializer):
    DocNum: int | None = field(default=None)
    DocDate: date | None = field(default=None)
    Comments: str | None = field(default=None)
    JrnlMemo: str | None = field(default=None)
    U_UserFld1: str | None = field(default=None)
    U_UserFld2: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class InventoryGoodsReceiptLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Quantity: str
    WhsCode: str
    Price: str
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str




class InventoryGoodsReceiptLinePage(Serializer):
    items: Annotated[list[InventoryGoodsReceiptLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class InventoryGoodsReceiptLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Quantity: str
    WhsCode: str
    Price: str = field(default="0")
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)




class InventoryGoodsReceiptLinePatchBody(Serializer):
    ItemCode: str | None = field(default=None)
    Quantity: str | None = field(default=None)
    WhsCode: str | None = field(default=None)
    Price: str | None = field(default=None)
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str | None = field(default=None)




class InventoryGoodsIssueResponse(Serializer):
    DocEntry: int
    DocNum: int | None = field(default=None)
    DocDate: date
    Comments: str = field(default="")
    JrnlMemo: str = field(default="")
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")
    Canceled: str




class InventoryGoodsIssuePage(Serializer):
    items: Annotated[list[InventoryGoodsIssueResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class InventoryGoodsIssueCreateBody(Serializer):
    DocNum: int | None = field(default=None)
    DocDate: date
    Comments: str = field(default="")
    JrnlMemo: str = field(default="")
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")




class InventoryGoodsIssuePatchBody(Serializer):
    DocNum: int | None = field(default=None)
    DocDate: date | None = field(default=None)
    Comments: str | None = field(default=None)
    JrnlMemo: str | None = field(default=None)
    U_UserFld1: str | None = field(default=None)
    U_UserFld2: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class InventoryGoodsIssueLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Quantity: str
    WhsCode: str
    Account: str = field(default="")
    Price: str
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str




class InventoryGoodsIssueLinePage(Serializer):
    items: Annotated[list[InventoryGoodsIssueLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class InventoryGoodsIssueLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    Quantity: str
    WhsCode: str
    Account: str = field(default="")
    Price: str = field(default="0")
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)




class InventoryGoodsIssueLinePatchBody(Serializer):
    ItemCode: str | None = field(default=None)
    Quantity: str | None = field(default=None)
    WhsCode: str | None = field(default=None)
    Account: str | None = field(default=None)
    Price: str | None = field(default=None)
    BaseType: int | None = field(default=None)
    BaseEntry: int | None = field(default=None)
    BaseLine: int | None = field(default=None)
    Canceled: str | None = field(default=None)




class StockTakeResponse(Serializer):
    DocEntry: int
    DocNum: int | None = field(default=None)
    CountDate: date
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")
    Canceled: str




class StockTakePage(Serializer):
    items: Annotated[list[StockTakeResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class StockTakeCreateBody(Serializer):
    DocNum: int | None = field(default=None)
    CountDate: date
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")




class StockTakePatchBody(Serializer):
    DocNum: int | None = field(default=None)
    CountDate: date | None = field(default=None)
    U_UserFld1: str | None = field(default=None)
    U_UserFld2: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class StockTakeLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    WhsCode: str
    InQty: str
    OutQty: str
    Difference: str
    Price: str
    Canceled: str




class StockTakeLinePage(Serializer):
    items: Annotated[list[StockTakeLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class StockTakeLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    ItemCode: str
    WhsCode: str
    InQty: str = field(default="0")
    OutQty: str = field(default="0")
    Difference: str = field(default="0")
    Price: str = field(default="0")




class StockTakeLinePatchBody(Serializer):
    ItemCode: str | None = field(default=None)
    WhsCode: str | None = field(default=None)
    InQty: str | None = field(default=None)
    OutQty: str | None = field(default=None)
    Difference: str | None = field(default=None)
    Price: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class InventoryPostingResponse(Serializer):
    TransNum: int
    TransType: int
    ItemCode: str
    Warehouse: str
    InQty: str
    OutQty: str
    Price: str
    BASE_REF: str = field(default="")
    DocTime: datetime
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")
    Canceled: str




class InventoryPostingPage(Serializer):
    items: Annotated[list[InventoryPostingResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class InventoryPostingCreateBody(Serializer):
    TransType: int
    ItemCode: str
    Warehouse: str
    InQty: str = field(default="0")
    OutQty: str = field(default="0")
    Price: str = field(default="0")
    BASE_REF: str = field(default="")
    DocTime: datetime | None = field(default=None)
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")




class InventoryPostingPatchBody(Serializer):
    TransType: int | None = field(default=None)
    ItemCode: str | None = field(default=None)
    Warehouse: str | None = field(default=None)
    InQty: str | None = field(default=None)
    OutQty: str | None = field(default=None)
    Price: str | None = field(default=None)
    BASE_REF: str | None = field(default=None)
    DocTime: datetime | None = field(default=None)
    U_UserFld1: str | None = field(default=None)
    U_UserFld2: str | None = field(default=None)
    Canceled: str | None = field(default=None)
