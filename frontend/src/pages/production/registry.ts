/** Production CRUD → ``/api/production`` (``apps/production/api/views.py``). */

import type { DocumentRegistryEntry, HeaderField, ListCol } from "../shared/documentTypes";

const API = "/api/production";

const LINE_WOR: ListCol[] = [
  { key: "LineNum", label: "#" },
  { key: "ItemCode", label: "Item No." },
  { key: "PlannedQty", label: "Planned Qty" },
  { key: "IssuedQty", label: "Issued Qty" },
  { key: "WhsCode", label: "Whs" },
];

const LINE_WOR_EDIT = ["ItemCode", "PlannedQty", "IssuedQty", "WhsCode"];

const LINE_BOM: ListCol[] = [
  { key: "LineNum", label: "#" },
  { key: "ItemCode", label: "Item No." },
  { key: "Quantity", label: "Qty" },
  { key: "WhsCode", label: "Whs" },
];

const LINE_BOM_EDIT = ["ItemCode", "Quantity", "WhsCode"];

const HEADER_OWOR: HeaderField[] = [
  { key: "DocEntry", label: "DocEntry", kind: "number", pk: true, readonly: true },
  { key: "DocNum", label: "DocNum", kind: "number" },
  { key: "ItemCode", label: "Item No.", kind: "text" },
  { key: "Status", label: "Status", kind: "text" },
  { key: "PlannedQty", label: "Planned Qty", kind: "text" },
  { key: "CmpltQty", label: "Completed Qty", kind: "text" },
  { key: "PostDate", label: "Posting Date", kind: "date" },
  { key: "WhsCode", label: "Whse", kind: "text" },
  { key: "Canceled", label: "Canceled", kind: "text", readonly: true },
];

const HEADER_BOM: HeaderField[] = [
  { key: "Code", label: "BOM Code", kind: "text", pk: true },
  { key: "TreeType", label: "Tree Type", kind: "text" },
  { key: "Quantity", label: "Quantity", kind: "text" },
  { key: "Canceled", label: "Canceled", kind: "text", readonly: true },
];

const LIST_OWOR: ListCol[] = [
  { key: "DocEntry", label: "Entry" },
  { key: "DocNum", label: "No." },
  { key: "ItemCode", label: "Item" },
  { key: "Status", label: "St" },
  { key: "PostDate", label: "Date" },
];

const LIST_BOM: ListCol[] = [
  { key: "Code", label: "Code" },
  { key: "TreeType", label: "Type" },
  { key: "Quantity", label: "Qty" },
];

export const PRODUCTION_REGISTRY: DocumentRegistryEntry[] = [
  {
    id: "production-order",
    title: "Production Order — OWOR",
    listPath: `${API}/production-orders`,
    detailPath: (r) => `${API}/production-orders/${Number(r.DocEntry)}`,
    pkKeys: ["DocEntry"],
    listColumns: LIST_OWOR,
    headerFields: HEADER_OWOR,
    partnerPickerFieldKey: null,
    footerLeftKeys: [],
    footerTotalsKeys: [],
    showDocCurHint: false,
    createKeys: ["DocNum", "ItemCode", "Status", "PlannedQty", "CmpltQty", "PostDate", "WhsCode"],
    patchKeys: ["DocNum", "ItemCode", "Status", "PlannedQty", "CmpltQty", "PostDate", "WhsCode", "Canceled"],
    lines: {
      listPath: (de) => `${API}/production-order-lines?doc_entry=${de}&limit=200&offset=0`,
      detailPath: (de, ln) => `${API}/production-order-lines/${de}/${ln}`,
      postPath: `${API}/production-order-lines`,
      columns: LINE_WOR,
      editKeys: LINE_WOR_EDIT,
    },
  },
  {
    id: "bom",
    title: "Bill of Materials — OITT",
    listPath: `${API}/bom-headers`,
    detailPath: (r) => `${API}/bom-headers/${encodeURIComponent(String(r.Code ?? "").trim())}`,
    pkKeys: ["Code"],
    listColumns: LIST_BOM,
    headerFields: HEADER_BOM,
    partnerPickerFieldKey: null,
    footerLeftKeys: [],
    footerTotalsKeys: [],
    showDocCurHint: false,
    createKeys: ["Code", "TreeType", "Quantity"],
    patchKeys: ["TreeType", "Quantity", "Canceled"],
    lines: {
      listPath: (code) => `${API}/bom-lines?father=${encodeURIComponent(String(code))}&limit=200&offset=0`,
      detailPath: (code, ln) => `${API}/bom-lines/${encodeURIComponent(String(code))}/${ln}`,
      postPath: `${API}/bom-lines`,
      columns: LINE_BOM,
      editKeys: LINE_BOM_EDIT,
      lineParentFieldInBody: "Father",
    },
  },
];

export function getProductionModule(id: string | undefined): DocumentRegistryEntry | undefined {
  if (!id) return undefined;
  return PRODUCTION_REGISTRY.find((x) => x.id === id);
}
