/** Purchase A/P CRUD → ``/api/purchase`` (``apps/purchase/api/views.py``). */

import type { DocumentRegistryEntry, HeaderField, ListCol } from "../shared/documentTypes";

const API = "/api/purchase";

const LINE_PO: ListCol[] = [
  { key: "LineNum", label: "#" },
  { key: "ItemCode", label: "Item No." },
  { key: "Quantity", label: "Qty" },
  { key: "Price", label: "Price" },
  { key: "WhsCode", label: "Whs" },
  { key: "BaseEntry", label: "Base" },
  { key: "BaseLine", label: "BL" },
];

const LINE_PO_EDIT = ["ItemCode", "Quantity", "Price", "WhsCode", "BaseType", "BaseEntry", "BaseLine"];

const LINE_PRQ: ListCol[] = [
  { key: "LineNum", label: "#" },
  { key: "ItemCode", label: "Item No." },
  { key: "Dscription", label: "Description" },
  { key: "Quantity", label: "Qty" },
  { key: "WhsCode", label: "Whs" },
  { key: "LineStatus", label: "Ln St" },
];

const LINE_PRQ_EDIT = ["ItemCode", "Dscription", "Quantity", "WhsCode", "LineStatus"];

const LINE_AP: ListCol[] = [
  { key: "LineNum", label: "#" },
  { key: "ItemCode", label: "Item No." },
  { key: "Quantity", label: "Qty" },
  { key: "Price", label: "Price" },
  { key: "LineTotal", label: "Line Total" },
  { key: "BaseEntry", label: "Base" },
];

const LINE_AP_EDIT = ["ItemCode", "Quantity", "Price", "LineTotal", "BaseType", "BaseEntry"];

const HEADER_PO: HeaderField[] = [
  { key: "DocEntry", label: "DocEntry", kind: "number", pk: true, readonly: true },
  { key: "DocNum", label: "DocNum", kind: "number" },
  { key: "CardCode", label: "Vendor", kind: "text" },
  { key: "CardName", label: "Name", kind: "text" },
  { key: "DocStatus", label: "Status", kind: "text" },
  { key: "DocDate", label: "Posting Date", kind: "date" },
  { key: "DocTotal", label: "Doc Total", kind: "text" },
  { key: "Canceled", label: "Canceled", kind: "text", readonly: true },
];

const HEADER_GRPO: HeaderField[] = [
  { key: "DocEntry", label: "DocEntry", kind: "number", pk: true, readonly: true },
  { key: "DocNum", label: "DocNum", kind: "number" },
  { key: "CardCode", label: "Vendor", kind: "text" },
  { key: "CardName", label: "Name", kind: "text" },
  { key: "DocDate", label: "Posting Date", kind: "date" },
  { key: "DocStatus", label: "Status", kind: "text" },
  { key: "Canceled", label: "Canceled", kind: "text", readonly: true },
];

const HEADER_VR: HeaderField[] = [
  { key: "DocEntry", label: "DocEntry", kind: "number", pk: true, readonly: true },
  { key: "DocNum", label: "DocNum", kind: "number" },
  { key: "CardCode", label: "Vendor", kind: "text" },
  { key: "CardName", label: "Name", kind: "text" },
  { key: "DocDate", label: "Posting Date", kind: "date" },
  { key: "Canceled", label: "Canceled", kind: "text", readonly: true },
];

const HEADER_AP: HeaderField[] = [
  { key: "DocEntry", label: "DocEntry", kind: "number", pk: true, readonly: true },
  { key: "DocNum", label: "DocNum", kind: "number" },
  { key: "CardCode", label: "Vendor", kind: "text" },
  { key: "CardName", label: "Name", kind: "text" },
  { key: "DocDate", label: "Posting Date", kind: "date" },
  { key: "DocTotal", label: "Doc Total", kind: "text" },
  { key: "VatSum", label: "Tax", kind: "text" },
  { key: "Canceled", label: "Canceled", kind: "text", readonly: true },
];

const HEADER_PRQ: HeaderField[] = [
  { key: "DocEntry", label: "DocEntry", kind: "number", pk: true, readonly: true },
  { key: "DocNum", label: "DocNum", kind: "number" },
  { key: "DocStatus", label: "Status", kind: "text" },
  { key: "Requester", label: "Requester", kind: "text" },
  { key: "DocDate", label: "Posting Date", kind: "date" },
  { key: "DocDueDate", label: "Due Date", kind: "date" },
  { key: "Canceled", label: "Canceled", kind: "text", readonly: true },
];

const LIST_VENDOR: ListCol[] = [
  { key: "DocEntry", label: "Entry" },
  { key: "DocNum", label: "No." },
  { key: "CardCode", label: "Vendor" },
  { key: "CardName", label: "Name" },
  { key: "DocDate", label: "Date" },
  { key: "DocTotal", label: "Total" },
];

const LIST_GRPO: ListCol[] = [
  { key: "DocEntry", label: "Entry" },
  { key: "DocNum", label: "No." },
  { key: "CardCode", label: "Vendor" },
  { key: "CardName", label: "Name" },
  { key: "DocDate", label: "Date" },
  { key: "DocStatus", label: "St" },
];

const LIST_PRQ: ListCol[] = [
  { key: "DocEntry", label: "Entry" },
  { key: "DocNum", label: "No." },
  { key: "Requester", label: "Requester" },
  { key: "DocDate", label: "Date" },
  { key: "DocStatus", label: "St" },
];

const LIST_AP: ListCol[] = [
  { key: "DocEntry", label: "Entry" },
  { key: "DocNum", label: "No." },
  { key: "CardCode", label: "Vendor" },
  { key: "DocDate", label: "Date" },
  { key: "DocTotal", label: "Total" },
  { key: "VatSum", label: "Tax" },
];

export const PURCHASE_REGISTRY: DocumentRegistryEntry[] = [
  {
    id: "purchase-request",
    title: "Purchase Request — OPRQ",
    listPath: `${API}/purchase-requests`,
    detailPath: (r) => `${API}/purchase-requests/${Number(r.DocEntry)}`,
    pkKeys: ["DocEntry"],
    listColumns: LIST_PRQ,
    headerFields: HEADER_PRQ,
    partnerPickerFieldKey: null,
    footerLeftKeys: [],
    footerTotalsKeys: [],
    showDocCurHint: false,
    createKeys: ["DocNum", "DocStatus", "Requester", "DocDate", "DocDueDate"],
    patchKeys: ["DocNum", "DocStatus", "Requester", "DocDate", "DocDueDate", "Canceled"],
    lines: {
      listPath: (de) => `${API}/purchase-request-lines?doc_entry=${de}&limit=200&offset=0`,
      detailPath: (de, ln) => `${API}/purchase-request-lines/${de}/${ln}`,
      postPath: `${API}/purchase-request-lines`,
      columns: LINE_PRQ,
      editKeys: LINE_PRQ_EDIT,
    },
  },
  {
    id: "purchase-order",
    title: "Purchase Order — OPOR",
    listPath: `${API}/purchase-orders`,
    detailPath: (r) => `${API}/purchase-orders/${Number(r.DocEntry)}`,
    pkKeys: ["DocEntry"],
    listColumns: LIST_VENDOR,
    headerFields: HEADER_PO,
    listButtonTitleBp: "Vendor list",
    footerLeftKeys: [],
    footerTotalsKeys: ["DocTotal"],
    showDocCurHint: false,
    createKeys: ["DocNum", "CardCode", "CardName", "DocStatus", "DocDate", "DocTotal"],
    patchKeys: ["DocNum", "CardCode", "CardName", "DocStatus", "DocDate", "DocTotal", "Canceled"],
    lines: {
      listPath: (de) => `${API}/purchase-order-lines?doc_entry=${de}&limit=200&offset=0`,
      detailPath: (de, ln) => `${API}/purchase-order-lines/${de}/${ln}`,
      postPath: `${API}/purchase-order-lines`,
      columns: LINE_PO,
      editKeys: LINE_PO_EDIT,
    },
  },
  {
    id: "goods-receipt-po",
    title: "Goods Receipt PO — OPDN",
    listPath: `${API}/goods-receipts`,
    detailPath: (r) => `${API}/goods-receipts/${Number(r.DocEntry)}`,
    pkKeys: ["DocEntry"],
    listColumns: LIST_GRPO,
    headerFields: HEADER_GRPO,
    listButtonTitleBp: "Vendor list",
    footerLeftKeys: [],
    footerTotalsKeys: [],
    showDocCurHint: false,
    createKeys: ["DocNum", "CardCode", "CardName", "DocDate", "DocStatus"],
    patchKeys: ["DocNum", "CardCode", "CardName", "DocDate", "DocStatus", "Canceled"],
    lines: {
      listPath: (de) => `${API}/goods-receipt-lines?doc_entry=${de}&limit=200&offset=0`,
      detailPath: (de, ln) => `${API}/goods-receipt-lines/${de}/${ln}`,
      postPath: `${API}/goods-receipt-lines`,
      columns: LINE_PO,
      editKeys: LINE_PO_EDIT,
    },
  },
  {
    id: "vendor-return",
    title: "Goods Return — ORPC",
    listPath: `${API}/vendor-returns`,
    detailPath: (r) => `${API}/vendor-returns/${Number(r.DocEntry)}`,
    pkKeys: ["DocEntry"],
    listColumns: LIST_GRPO.filter((c) => c.key !== "DocStatus"),
    headerFields: HEADER_VR,
    listButtonTitleBp: "Vendor list",
    footerLeftKeys: [],
    footerTotalsKeys: [],
    showDocCurHint: false,
    createKeys: ["DocNum", "CardCode", "CardName", "DocDate"],
    patchKeys: ["DocNum", "CardCode", "CardName", "DocDate", "DocStatus", "Canceled"],
    lines: {
      listPath: (de) => `${API}/vendor-return-lines?doc_entry=${de}&limit=200&offset=0`,
      detailPath: (de, ln) => `${API}/vendor-return-lines/${de}/${ln}`,
      postPath: `${API}/vendor-return-lines`,
      columns: LINE_PO,
      editKeys: LINE_PO_EDIT,
    },
  },
  {
    id: "ap-invoice",
    title: "A/P Invoice — OPCH",
    listPath: `${API}/ap-invoices`,
    detailPath: (r) => `${API}/ap-invoices/${Number(r.DocEntry)}`,
    pkKeys: ["DocEntry"],
    listColumns: LIST_AP,
    headerFields: HEADER_AP,
    listButtonTitleBp: "Vendor list",
    footerLeftKeys: [],
    footerTotalsKeys: ["DocTotal", "VatSum"],
    showDocCurHint: false,
    createKeys: ["DocNum", "CardCode", "CardName", "DocDate", "DocTotal", "VatSum"],
    patchKeys: ["DocNum", "CardCode", "CardName", "DocDate", "DocTotal", "VatSum", "Canceled"],
    lines: {
      listPath: (de) => `${API}/ap-invoice-lines?doc_entry=${de}&limit=200&offset=0`,
      detailPath: (de, ln) => `${API}/ap-invoice-lines/${de}/${ln}`,
      postPath: `${API}/ap-invoice-lines`,
      columns: LINE_AP,
      editKeys: LINE_AP_EDIT,
    },
  },
];

export function getPurchaseModule(id: string | undefined): DocumentRegistryEntry | undefined {
  if (!id) return undefined;
  return PURCHASE_REGISTRY.find((x) => x.id === id);
}
