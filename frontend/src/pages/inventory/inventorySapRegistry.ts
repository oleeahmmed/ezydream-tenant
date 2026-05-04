/**
 * Inventory documents use the same shell as Sales/Purchase (``SapDocumentCrud``).
 * Header / line fields match ``apps/inventory/api/serializers.py``.
 */

import type { DocumentRegistryEntry } from "../shared/documentTypes";

const API = "/api/inventory";

const HDR_DATE_FILER = [
  { key: "DocEntry", label: "Doc Entry", kind: "number" as const, pk: true, readonly: true },
  { key: "DocNum", label: "Doc No.", kind: "number" as const },
  { key: "DocDate", label: "Posting Date", kind: "date" as const },
  { key: "Filler", label: "Employee / Project", kind: "text" as const },
  { key: "U_UserFld1", label: "User-defined field 1", kind: "text" as const },
  { key: "U_UserFld2", label: "User-defined field 2", kind: "text" as const },
  { key: "Canceled", label: "Canceled", kind: "text" as const, readonly: true },
];

const HDR_GRE_GR_ISSUE = [
  { key: "DocEntry", label: "Doc Entry", kind: "number" as const, pk: true, readonly: true },
  { key: "DocNum", label: "Doc No.", kind: "number" as const },
  { key: "DocDate", label: "Posting Date", kind: "date" as const },
  { key: "U_UserFld1", label: "User-defined field 1", kind: "text" as const },
  { key: "U_UserFld2", label: "User-defined field 2", kind: "text" as const },
  { key: "Canceled", label: "Canceled", kind: "text" as const, readonly: true },
];

const HDR_STKT = [
  { key: "DocEntry", label: "Doc Entry", kind: "number" as const, pk: true, readonly: true },
  { key: "DocNum", label: "Doc No.", kind: "number" as const },
  { key: "CountDate", label: "Count Date", kind: "date" as const },
  { key: "U_UserFld1", label: "User-defined field 1", kind: "text" as const },
  { key: "U_UserFld2", label: "User-defined field 2", kind: "text" as const },
  { key: "Canceled", label: "Canceled", kind: "text" as const, readonly: true },
];

/** Remarks live in right sidebar (``Comments``, ``JrnlMemo``) — see ``rightSidebarFieldKeys``. */
const HDR_SIDEBAR_MEMO = [
  { key: "Comments", label: "Remarks", kind: "text" as const },
  { key: "JrnlMemo", label: "Journal Memo", kind: "text" as const },
];

export const INVENTORY_SAP_REGISTRY: DocumentRegistryEntry[] = [
  {
    id: "str-req",
    title: "Stock Transfer Request — OWTQ",
    listPath: `${API}/stock-transfer-requests`,
    detailPath: (r) => `${API}/stock-transfer-requests/${Number(r.DocEntry)}`,
    pkKeys: ["DocEntry"],
    listColumns: [
      { key: "DocEntry", label: "Entry" },
      { key: "DocNum", label: "No." },
      { key: "DocDate", label: "Date" },
      { key: "Filler", label: "Filler" },
      { key: "Canceled", label: "Can." },
    ],
    headerFields: [...HDR_DATE_FILER, ...HDR_SIDEBAR_MEMO],
    createKeys: ["DocNum", "DocDate", "Filler", "Comments", "JrnlMemo", "U_UserFld1", "U_UserFld2"],
    patchKeys: ["DocNum", "DocDate", "Filler", "Comments", "JrnlMemo", "U_UserFld1", "U_UserFld2", "Canceled"],
    partnerPickerFieldKey: null,
    footerLeftKeys: [],
    footerTotalsKeys: [],
    docRootClassName: "sap-inventory-doc",
    windowClassName: "sap-window-inventory",
    hideContentsToolbar: true,
    rightSidebarFieldKeys: ["U_UserFld1", "U_UserFld2", "Comments", "JrnlMemo"],
    lines: {
      listPath: (de) => `${API}/stock-transfer-request-lines?doc_entry=${de}&limit=200&offset=0`,
      detailPath: (de, ln) => `${API}/stock-transfer-request-lines/${de}/${ln}`,
      postPath: `${API}/stock-transfer-request-lines`,
      columns: [
        { key: "LineNum", label: "#" },
        { key: "ItemCode", label: "Item" },
        { key: "Quantity", label: "Qty" },
        { key: "OpenQty", label: "Open" },
        { key: "FromWhsCod", label: "From WH" },
        { key: "WhsCode", label: "To WH" },
        { key: "Price", label: "Price" },
        { key: "LineStatus", label: "Ln St" },
      ],
      editKeys: [
        "ItemCode",
        "Quantity",
        "OpenQty",
        "Price",
        "FromWhsCod",
        "WhsCode",
        "LineStatus",
        "TargetType",
        "TrgetEntry",
        "BaseRef",
        "BaseType",
        "BaseEntry",
        "BaseLine",
        "Canceled",
      ],
    },
  },
  {
    id: "str",
    title: "Stock Transfer — OWTR",
    listPath: `${API}/stock-transfers`,
    detailPath: (r) => `${API}/stock-transfers/${Number(r.DocEntry)}`,
    pkKeys: ["DocEntry"],
    listColumns: [
      { key: "DocEntry", label: "Entry" },
      { key: "DocNum", label: "No." },
      { key: "DocDate", label: "Date" },
      { key: "Filler", label: "Filler" },
      { key: "Canceled", label: "Can." },
    ],
    headerFields: [...HDR_DATE_FILER, ...HDR_SIDEBAR_MEMO],
    createKeys: ["DocNum", "DocDate", "Filler", "Comments", "JrnlMemo", "U_UserFld1", "U_UserFld2"],
    patchKeys: ["DocNum", "DocDate", "Filler", "Comments", "JrnlMemo", "U_UserFld1", "U_UserFld2", "Canceled"],
    partnerPickerFieldKey: null,
    footerLeftKeys: [],
    footerTotalsKeys: [],
    docRootClassName: "sap-inventory-doc",
    windowClassName: "sap-window-inventory",
    hideContentsToolbar: true,
    rightSidebarFieldKeys: ["U_UserFld1", "U_UserFld2", "Comments", "JrnlMemo"],
    lines: {
      listPath: (de) => `${API}/stock-transfer-lines?doc_entry=${de}&limit=200&offset=0`,
      detailPath: (de, ln) => `${API}/stock-transfer-lines/${de}/${ln}`,
      postPath: `${API}/stock-transfer-lines`,
      columns: [
        { key: "LineNum", label: "#" },
        { key: "ItemCode", label: "Item" },
        { key: "Quantity", label: "Qty" },
        { key: "FromWhsCod", label: "From WH" },
        { key: "WhsCode", label: "To WH" },
        { key: "Price", label: "Price" },
      ],
      editKeys: ["ItemCode", "Quantity", "FromWhsCod", "WhsCode", "Price", "Canceled"],
    },
  },
  {
    id: "greceipt",
    title: "Goods Receipt — OIGN",
    listPath: `${API}/goods-receipts`,
    detailPath: (r) => `${API}/goods-receipts/${Number(r.DocEntry)}`,
    pkKeys: ["DocEntry"],
    listColumns: [
      { key: "DocEntry", label: "Entry" },
      { key: "DocNum", label: "No." },
      { key: "DocDate", label: "Date" },
      { key: "Canceled", label: "Can." },
    ],
    headerFields: [...HDR_GRE_GR_ISSUE, ...HDR_SIDEBAR_MEMO],
    createKeys: ["DocNum", "DocDate", "Comments", "JrnlMemo", "U_UserFld1", "U_UserFld2"],
    patchKeys: ["DocNum", "DocDate", "Comments", "JrnlMemo", "U_UserFld1", "U_UserFld2", "Canceled"],
    partnerPickerFieldKey: null,
    footerLeftKeys: [],
    footerTotalsKeys: [],
    docRootClassName: "sap-inventory-doc",
    windowClassName: "sap-window-inventory",
    hideContentsToolbar: true,
    rightSidebarFieldKeys: ["U_UserFld1", "U_UserFld2", "Comments", "JrnlMemo"],
    lines: {
      listPath: (de) => `${API}/goods-receipt-lines?doc_entry=${de}&limit=200&offset=0`,
      detailPath: (de, ln) => `${API}/goods-receipt-lines/${de}/${ln}`,
      postPath: `${API}/goods-receipt-lines`,
      columns: [
        { key: "LineNum", label: "#" },
        { key: "ItemCode", label: "Item" },
        { key: "Quantity", label: "Qty" },
        { key: "WhsCode", label: "Whs" },
        { key: "Price", label: "Price" },
      ],
      editKeys: ["ItemCode", "Quantity", "WhsCode", "Price", "BaseType", "BaseEntry", "BaseLine", "Canceled"],
    },
  },
  {
    id: "gissue",
    title: "Goods Issue — OIGE",
    listPath: `${API}/goods-issues`,
    detailPath: (r) => `${API}/goods-issues/${Number(r.DocEntry)}`,
    pkKeys: ["DocEntry"],
    listColumns: [
      { key: "DocEntry", label: "Entry" },
      { key: "DocNum", label: "No." },
      { key: "DocDate", label: "Date" },
      { key: "Canceled", label: "Can." },
    ],
    headerFields: [...HDR_GRE_GR_ISSUE, ...HDR_SIDEBAR_MEMO],
    createKeys: ["DocNum", "DocDate", "Comments", "JrnlMemo", "U_UserFld1", "U_UserFld2"],
    patchKeys: ["DocNum", "DocDate", "Comments", "JrnlMemo", "U_UserFld1", "U_UserFld2", "Canceled"],
    partnerPickerFieldKey: null,
    footerLeftKeys: [],
    footerTotalsKeys: [],
    docRootClassName: "sap-inventory-doc",
    windowClassName: "sap-window-inventory",
    hideContentsToolbar: true,
    rightSidebarFieldKeys: ["U_UserFld1", "U_UserFld2", "Comments", "JrnlMemo"],
    lines: {
      listPath: (de) => `${API}/goods-issue-lines?doc_entry=${de}&limit=200&offset=0`,
      detailPath: (de, ln) => `${API}/goods-issue-lines/${de}/${ln}`,
      postPath: `${API}/goods-issue-lines`,
      columns: [
        { key: "LineNum", label: "#" },
        { key: "ItemCode", label: "Item" },
        { key: "Quantity", label: "Qty" },
        { key: "WhsCode", label: "Whs" },
        { key: "Account", label: "GL / Offset" },
        { key: "Price", label: "Price" },
      ],
      editKeys: ["ItemCode", "Quantity", "WhsCode", "Account", "Price", "BaseType", "BaseEntry", "BaseLine", "Canceled"],
    },
  },
  {
    id: "stktake",
    title: "Stock Take — OINC",
    listPath: `${API}/stock-takes`,
    detailPath: (r) => `${API}/stock-takes/${Number(r.DocEntry)}`,
    pkKeys: ["DocEntry"],
    listColumns: [
      { key: "DocEntry", label: "Entry" },
      { key: "DocNum", label: "No." },
      { key: "CountDate", label: "Date" },
      { key: "Canceled", label: "Can." },
    ],
    headerFields: HDR_STKT,
    rightSidebarFieldKeys: ["U_UserFld1", "U_UserFld2"],
    createKeys: ["DocNum", "CountDate", "U_UserFld1", "U_UserFld2"],
    patchKeys: ["DocNum", "CountDate", "U_UserFld1", "U_UserFld2", "Canceled"],
    partnerPickerFieldKey: null,
    footerLeftKeys: [],
    footerTotalsKeys: [],
    docRootClassName: "sap-inventory-doc",
    windowClassName: "sap-window-inventory",
    hideContentsToolbar: true,
    lines: {
      listPath: (de) => `${API}/stock-take-lines?doc_entry=${de}&limit=200&offset=0`,
      detailPath: (de, ln) => `${API}/stock-take-lines/${de}/${ln}`,
      postPath: `${API}/stock-take-lines`,
      columns: [
        { key: "LineNum", label: "#" },
        { key: "ItemCode", label: "Item" },
        { key: "WhsCode", label: "Whs" },
        { key: "InQty", label: "In" },
        { key: "OutQty", label: "Out" },
        { key: "Difference", label: "Diff" },
        { key: "Price", label: "Price" },
      ],
      editKeys: ["ItemCode", "WhsCode", "InQty", "OutQty", "Difference", "Price", "Canceled"],
    },
  },
];

export function getInventorySapModule(id: string | undefined): DocumentRegistryEntry | undefined {
  if (!id) return undefined;
  return INVENTORY_SAP_REGISTRY.find((x) => x.id === id);
}

/** Module ids rendered with ``SapDocumentCrud`` (header + line grid like Sales). */
export const INVENTORY_SAP_MODULE_IDS = new Set(INVENTORY_SAP_REGISTRY.map((x) => x.id));
