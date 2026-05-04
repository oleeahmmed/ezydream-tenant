#!/usr/bin/env python3
"""
One-off refactor: Collection/Detail -> ListCreateView/DetailView, shared pagination,
include_deleted helper, optional doc_entry query parsing.

Run from repo root: python tools/refactor_bolt_list_views.py
"""

from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

PAGINATION_OLD = """        qd = getattr(self.request, "query", None) or {}
        try:
            limit = min(100, max(1, int(qd.get("limit", "50"))))
        except ValueError:
            limit = 50
        try:
            offset = max(0, int(qd.get("offset", "0")))
        except ValueError:
            offset = 0
        search_prefix = (qd.get("q") or "").strip()
"""

PAGINATION_NEW = """        # STEP 1 — Bolt list parameters: ``limit``, ``offset``, optional ``q`` prefix.
        limit, offset, search_prefix = get_list_pagination_for_request(self.request)
"""

INCLUDE_LIST = """if (getattr(self.request, "query", None) or {}).get("include_deleted", "").strip().lower() not in ("1", "true", "yes"):"""
INCLUDE_LIST_NEW = """if not get_boolean_query_flag_is_true(self.request, "include_deleted"):"""

INCLUDE_QD = """if (qd.get("include_deleted") or "").strip().lower() not in ("1", "true", "yes")"""
INCLUDE_QD_NEW = """if not get_boolean_query_flag_is_true(self.request, "include_deleted")"""

DOC_ENTRY_BLOCK = """        qd2 = getattr(self.request, "query", None) or {}
        raw_de = (qd2.get("doc_entry") or "").strip()
        doc_entry = int(raw_de) if raw_de else None
"""

DOC_ENTRY_NEW = """        doc_entry = get_optional_int_from_query(self.request, "doc_entry")
"""

INVENTORY_DOC_BLOCK = """        qd_de = getattr(self.request, "query", None) or {}
        raw_de = (qd_de.get("doc_entry") or "").strip()
        try:
            de = int(raw_de) if raw_de else None
        except ValueError:
            raise BadRequest(detail="doc_entry সঠিক পূর্ণসংখ্যা নয়।")
"""

INVENTORY_DOC_NEW = """        de = get_optional_int_from_query(self.request, "doc_entry")
"""


def class_pairs_for_file(rel: str) -> list[tuple[str, str]]:
    if rel == "apps/purchase/api/views.py":
        return [
            ("PurchaseRequestLineCollection", "PurchaseRequestLineListCreateView"),
            ("PurchaseRequestLineDetail", "PurchaseRequestLineDetailView"),
            ("PurchaseRequestCollection", "PurchaseRequestListCreateView"),
            ("PurchaseRequestDetail", "PurchaseRequestDetailView"),
            ("PurchaseOrderLineCollection", "PurchaseOrderLineListCreateView"),
            ("PurchaseOrderLineDetail", "PurchaseOrderLineDetailView"),
            ("PurchaseOrderCollection", "PurchaseOrderListCreateView"),
            ("PurchaseOrderDetail", "PurchaseOrderDetailView"),
            ("GoodsReceiptLineCollection", "GoodsReceiptLineListCreateView"),
            ("GoodsReceiptLineDetail", "GoodsReceiptLineDetailView"),
            ("GoodsReceiptCollection", "GoodsReceiptListCreateView"),
            ("GoodsReceiptDetail", "GoodsReceiptDetailView"),
            ("VendorReturnLineCollection", "VendorReturnLineListCreateView"),
            ("VendorReturnLineDetail", "VendorReturnLineDetailView"),
            ("VendorReturnCollection", "VendorReturnListCreateView"),
            ("VendorReturnDetail", "VendorReturnDetailView"),
            ("ApInvoiceLineCollection", "ApInvoiceLineListCreateView"),
            ("ApInvoiceLineDetail", "ApInvoiceLineDetailView"),
            ("ApInvoiceCollection", "ApInvoiceListCreateView"),
            ("ApInvoiceDetail", "ApInvoiceDetailView"),
        ]
    if rel == "apps/sales/api/views.py":
        return [
            ("SalesQuotationLineCollection", "SalesQuotationLineListCreateView"),
            ("SalesQuotationLineDetail", "SalesQuotationLineDetailView"),
            ("SalesQuotationCollection", "SalesQuotationListCreateView"),
            ("SalesQuotationDetail", "SalesQuotationDetailView"),
            ("SalesOrderLineCollection", "SalesOrderLineListCreateView"),
            ("SalesOrderLineDetail", "SalesOrderLineDetailView"),
            ("SalesOrderCollection", "SalesOrderListCreateView"),
            ("SalesOrderDetail", "SalesOrderDetailView"),
            ("DeliveryLineCollection", "DeliveryLineListCreateView"),
            ("DeliveryLineDetail", "DeliveryLineDetailView"),
            ("DeliveryNoteCollection", "DeliveryNoteListCreateView"),
            ("DeliveryNoteDetail", "DeliveryNoteDetailView"),
            ("CustomerReturnLineCollection", "CustomerReturnLineListCreateView"),
            ("CustomerReturnLineDetail", "CustomerReturnLineDetailView"),
            ("CustomerReturnCollection", "CustomerReturnListCreateView"),
            ("CustomerReturnDetail", "CustomerReturnDetailView"),
            ("SalesInvoiceLineCollection", "SalesInvoiceLineListCreateView"),
            ("SalesInvoiceLineDetail", "SalesInvoiceLineDetailView"),
            ("SalesInvoiceCollection", "SalesInvoiceListCreateView"),
            ("SalesInvoiceDetail", "SalesInvoiceDetailView"),
        ]
    if rel == "apps/inventory/api/views.py":
        return [
            ("StockTransferRequestLineCollection", "StockTransferRequestLineListCreateView"),
            ("StockTransferRequestLineDetail", "StockTransferRequestLineDetailView"),
            ("StockTransferRequestCollection", "StockTransferRequestListCreateView"),
            ("StockTransferRequestDetail", "StockTransferRequestDetailView"),
            ("StockTransferLineCollection", "StockTransferLineListCreateView"),
            ("StockTransferLineDetail", "StockTransferLineDetailView"),
            ("StockTransferCollection", "StockTransferListCreateView"),
            ("StockTransferDetail", "StockTransferDetailView"),
            ("InventoryGoodsReceiptLineCollection", "InventoryGoodsReceiptLineListCreateView"),
            ("InventoryGoodsReceiptLineDetail", "InventoryGoodsReceiptLineDetailView"),
            ("InventoryGoodsReceiptCollection", "InventoryGoodsReceiptListCreateView"),
            ("InventoryGoodsReceiptDetail", "InventoryGoodsReceiptDetailView"),
            ("InventoryGoodsIssueLineCollection", "InventoryGoodsIssueLineListCreateView"),
            ("InventoryGoodsIssueLineDetail", "InventoryGoodsIssueLineDetailView"),
            ("InventoryGoodsIssueCollection", "InventoryGoodsIssueListCreateView"),
            ("InventoryGoodsIssueDetail", "InventoryGoodsIssueDetailView"),
            ("StockTakeLineCollection", "StockTakeLineListCreateView"),
            ("StockTakeLineDetail", "StockTakeLineDetailView"),
            ("StockTakeCollection", "StockTakeListCreateView"),
            ("StockTakeDetail", "StockTakeDetailView"),
            ("InventoryPostingCollection", "InventoryPostingListCreateView"),
            ("InventoryPostingDetail", "InventoryPostingDetailView"),
            ("ItemWarehouseStockCollection", "ItemWarehouseStockListCreateView"),
            ("ItemWarehouseStockDetail", "ItemWarehouseStockDetailView"),
            ("UnitOfMeasureCollection", "UnitOfMeasureListCreateView"),
            ("UnitOfMeasureDetail", "UnitOfMeasureDetailView"),
            ("ItemGroupCollection", "ItemGroupListCreateView"),
            ("ItemGroupDetail", "ItemGroupDetailView"),
            ("ItemCollection", "ItemListCreateView"),
            ("ItemDetail", "ItemDetailView"),
        ]
    if rel == "apps/production/api/views.py":
        return [
            ("ProductionOrderLineCollection", "ProductionOrderLineListCreateView"),
            ("ProductionOrderLineDetail", "ProductionOrderLineDetailView"),
            ("ProductionOrderCollection", "ProductionOrderListCreateView"),
            ("ProductionOrderDetail", "ProductionOrderDetailView"),
            ("BomLineCollection", "BomLineListCreateView"),
            ("BomLineDetail", "BomLineDetailView"),
            ("BomHeaderCollection", "BomHeaderListCreateView"),
            ("BomHeaderDetail", "BomHeaderDetailView"),
        ]
    if rel == "apps/warehouse/api/views.py":
        return [
            ("WarehouseCollection", "WarehouseListCreateView"),
            ("WarehouseDetail", "WarehouseDetailView"),
        ]
    return []


def merge_beginner_imports(text: str) -> str:
    """Ensure pagination / flag helpers are imported from apps.core.beginner_style."""
    required = (
        "get_list_pagination_for_request",
        "get_boolean_query_flag_is_true",
        "get_optional_int_from_query",
    )
    marker = "from apps.core.beginner_style import ("
    if marker not in text:
        insert = (
            "from apps.core.beginner_style import (\n"
            "    get_boolean_query_flag_is_true,\n"
            "    get_list_pagination_for_request,\n"
            "    get_optional_int_from_query,\n"
            ")\n\n"
        )
        anchor = "from django_bolt.views import APIView\n\n"
        if anchor in text:
            return text.replace(anchor, anchor + insert, 1)
        raise RuntimeError("Could not find insertion anchor for beginner_style imports")

    start = text.find(marker) + len(marker)
    sub = text[start:]
    close_idx = sub.find("\n)")
    if close_idx == -1:
        raise RuntimeError("Unclosed beginner_style import tuple.")
    inner = sub[:close_idx]
    imported_names = {
        ln.strip().rstrip(",").strip()
        for ln in inner.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    }
    if all(n in imported_names for n in required):
        return text
    if marker not in text:
        insert = (
            "from apps.core.beginner_style import (\n"
            "    get_boolean_query_flag_is_true,\n"
            "    get_list_pagination_for_request,\n"
            "    get_optional_int_from_query,\n"
            ")\n\n"
        )
        anchor = "from django_bolt.views import APIView\n\n"
        if anchor in text:
            return text.replace(anchor, anchor + insert, 1)
        raise RuntimeError("Could not find insertion anchor for beginner_style imports")

    start = text.find(marker) + len(marker)
    sub = text[start:]
    close_idx = sub.find("\n)")
    if close_idx == -1:
        raise RuntimeError("Unclosed beginner_style import tuple.")
    inner = sub[:close_idx]
    existing_order: list[str] = []
    for line in inner.splitlines():
        s = line.strip().rstrip(",").strip()
        if not s or s.startswith("#"):
            continue
        existing_order.append(s)
    for n in required:
        if n not in existing_order:
            existing_order.append(n)
    new_inner = "".join(f"    {n},\n" for n in existing_order)
    return text[:start] + "\n" + new_inner + sub[close_idx:]


def process_file(rel: str) -> None:
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    orig = text

    pairs = class_pairs_for_file(rel)
    pairs.sort(key=lambda p: len(p[0]), reverse=True)
    for old, new in pairs:
        text = text.replace(old, new)

    if PAGINATION_OLD in text:
        text = text.replace(PAGINATION_OLD, PAGINATION_NEW)

    text = text.replace(INCLUDE_LIST, INCLUDE_LIST_NEW)
    text = text.replace(INCLUDE_QD, INCLUDE_QD_NEW)

    if DOC_ENTRY_BLOCK in text:
        text = text.replace(DOC_ENTRY_BLOCK, DOC_ENTRY_NEW)

    if rel == "apps/inventory/api/views.py" and INVENTORY_DOC_BLOCK in text:
        text = text.replace(INVENTORY_DOC_BLOCK, INVENTORY_DOC_NEW)

    text = merge_beginner_imports(text)
    text = text.replace("DetailViewView", "DetailView")

    if text != orig:
        path.write_text(text, encoding="utf-8")
        print(f"updated {rel}")
    else:
        print(f"no changes {rel}")


def main() -> None:
    for rel in (
        "apps/purchase/api/views.py",
        "apps/sales/api/views.py",
        "apps/inventory/api/views.py",
        "apps/production/api/views.py",
        "apps/warehouse/api/views.py",
    ):
        process_file(rel)


if __name__ == "__main__":
    main()
