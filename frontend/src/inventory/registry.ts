/** Inventory CRUD definitions → ``/api/inventory`` (human-readable paths). */

export type FieldKind = "text" | "number" | "date" | "datetime-local";

export type HeaderField = {
  key: string;
  label: string;
  kind: FieldKind;
  pk?: boolean;
  readonly?: boolean;
};

export type ListCol = { key: string; label: string };

export type LinesDef = {
  listPath: (docEntry: number) => string;
  detailPath: (docEntry: number, lineNum: number) => string;
  postPath: string;
  columns: ListCol[];
  /** Keys shown in line sub-form (excluding DocEntry, LineNum for PATCH body). */
  editKeys: string[];
};

export type InvRegistryEntry = {
  id: string;
  title: string;
  listPath: string;
  detailPath: (row: Record<string, unknown>) => string;
  deletePath?: (row: Record<string, unknown>) => string;
  pkKeys: string[];
  listColumns: ListCol[];
  headerFields: HeaderField[];
  /** Keys sent on POST (subset of headerFields + pk if create needs it). */
  createKeys: string[];
  /** Keys allowed on PATCH (non-null). */
  patchKeys: string[];
  lines?: LinesDef;
};

const API = "/api/inventory";

function enc(s: string): string {
  return encodeURIComponent(s);
}

export const INVENTORY_REGISTRY: InvRegistryEntry[] = [
  {
    id: "item-groups",
    title: "Item Groups — OITB",
    listPath: `${API}/item-groups`,
    detailPath: (r) => `${API}/item-groups/${r.ItmsGrpCod}`,
    pkKeys: ["ItmsGrpCod"],
    listColumns: [
      { key: "ItmsGrpCod", label: "Group Code" },
      { key: "ItmsGrpNam", label: "Group Name" },
      { key: "Canceled", label: "Canceled" },
    ],
    headerFields: [
      { key: "ItmsGrpCod", label: "Group Code", kind: "number", pk: true },
      { key: "ItmsGrpNam", label: "Group Name", kind: "text" },
      { key: "Canceled", label: "Canceled", kind: "text" },
    ],
    createKeys: ["ItmsGrpCod", "ItmsGrpNam"],
    patchKeys: ["ItmsGrpNam", "Canceled"],
  },
  {
    id: "items",
    title: "Item Master Data — OITM",
    listPath: `${API}/items`,
    detailPath: (r) => `${API}/items/${enc(String(r.ItemCode))}`,
    pkKeys: ["ItemCode"],
    listColumns: [
      { key: "ItemCode", label: "Item No." },
      { key: "ItemName", label: "Item Name" },
      { key: "ItmsGrpCod", label: "Group" },
      { key: "OnHand", label: "In Stock" },
      { key: "InvntItem", label: "Inv." },
    ],
    headerFields: [
      { key: "ItemCode", label: "Item No.", kind: "text", pk: true },
      { key: "ItemName", label: "Item Name", kind: "text" },
      { key: "ItmsGrpCod", label: "Items Group", kind: "number" },
      { key: "InvntItem", label: "Inventory Item", kind: "text" },
      { key: "OnHand", label: "In Stock", kind: "text" },
      { key: "IsCommited", label: "Committed", kind: "text" },
      { key: "OnOrder", label: "Ordered", kind: "text" },
      { key: "ByWh", label: "Manage WH", kind: "text" },
      { key: "DfltWH", label: "Dflt WH", kind: "text" },
      { key: "FrgnName", label: "Foreign Name", kind: "text" },
      { key: "CodeBars", label: "Barcode", kind: "text" },
      { key: "SalItem", label: "Sales Item", kind: "text" },
      { key: "PrchseItem", label: "Purchase Item", kind: "text" },
      { key: "SalUnitMsr", label: "Sales UoM", kind: "text" },
      { key: "BuyUnitMsr", label: "Purchase UoM", kind: "text" },
      { key: "ValidFor", label: "Valid", kind: "text" },
    ],
    createKeys: ["ItemCode", "ItemName", "ItmsGrpCod", "InvntItem", "OnHand", "IsCommited", "OnOrder", "ByWh", "DfltWH", "FrgnName", "CodeBars", "SalItem", "PrchseItem", "SalUnitMsr", "BuyUnitMsr"],
    patchKeys: ["ItemName", "ItmsGrpCod", "InvntItem", "OnHand", "IsCommited", "OnOrder", "ByWh", "DfltWH", "FrgnName", "CodeBars", "SalItem", "PrchseItem", "SalUnitMsr", "BuyUnitMsr", "ValidFor"],
  },
  {
    id: "item-whs",
    title: "Item Warehouse Stock — OITW",
    listPath: `${API}/item-warehouse-stock`,
    detailPath: (r) => `${API}/item-warehouse-stock/${enc(String(r.ItemCode))}/${enc(String(r.WhsCode))}`,
    pkKeys: ["ItemCode", "WhsCode"],
    listColumns: [
      { key: "ItemCode", label: "Item" },
      { key: "WhsCode", label: "Warehouse" },
      { key: "OnHand", label: "In Stock" },
      { key: "AvgPrice", label: "Avg Price" },
    ],
    headerFields: [
      { key: "ItemCode", label: "Item No.", kind: "text", pk: true },
      { key: "WhsCode", label: "Warehouse", kind: "text", pk: true },
      { key: "OnHand", label: "In Stock", kind: "text" },
      { key: "IsCommited", label: "Committed", kind: "text" },
      { key: "AvgPrice", label: "Avg Price", kind: "text" },
      { key: "OrderQty", label: "Ordered", kind: "text" },
      { key: "MinStock", label: "Min", kind: "text" },
      { key: "MaxStock", label: "Max", kind: "text" },
      { key: "Locked", label: "Locked", kind: "text" },
      { key: "Canceled", label: "Canceled", kind: "text" },
    ],
    createKeys: ["ItemCode", "WhsCode", "OnHand", "IsCommited", "AvgPrice", "OrderQty", "MinStock", "MaxStock", "Locked"],
    patchKeys: ["OnHand", "IsCommited", "AvgPrice", "OrderQty", "MinStock", "MaxStock", "Locked", "Canceled"],
  },
  {
    id: "uom",
    title: "Units of Measure — OUOM",
    listPath: `${API}/units-of-measure`,
    detailPath: (r) => `${API}/units-of-measure/${r.UomEntry}`,
    pkKeys: ["UomEntry"],
    listColumns: [
      { key: "UomEntry", label: "Entry" },
      { key: "UomCode", label: "Code" },
      { key: "UomName", label: "Name" },
      { key: "Locked", label: "Locked" },
    ],
    headerFields: [
      { key: "UomEntry", label: "UoM Entry", kind: "number", pk: true, readonly: true },
      { key: "UomCode", label: "UoM Code", kind: "text" },
      { key: "UomName", label: "UoM Name", kind: "text" },
      { key: "Locked", label: "Locked", kind: "text" },
      { key: "DataSource", label: "Data Source", kind: "text" },
    ],
    createKeys: ["UomCode", "UomName", "Locked", "DataSource"],
    patchKeys: ["UomCode", "UomName", "Locked", "DataSource"],
  },
  {
    id: "str-req",
    title: "Stock Transfer Request — OWTQ / WTQ1",
    listPath: `${API}/stock-transfer-requests`,
    detailPath: (r) => `${API}/stock-transfer-requests/${r.DocEntry}`,
    pkKeys: ["DocEntry"],
    listColumns: [
      { key: "DocEntry", label: "DocEntry" },
      { key: "DocNum", label: "No." },
      { key: "DocDate", label: "Date" },
      { key: "Filler", label: "Filler" },
      { key: "Canceled", label: "Can." },
    ],
    headerFields: [
      { key: "DocEntry", label: "DocEntry", kind: "number", pk: true, readonly: true },
      { key: "DocNum", label: "Document No.", kind: "number" },
      { key: "DocDate", label: "Posting Date", kind: "date" },
      { key: "Filler", label: "Filler", kind: "text" },
      { key: "Comments", label: "Comments", kind: "text" },
      { key: "JrnlMemo", label: "Jrnl Memo", kind: "text" },
      { key: "Canceled", label: "Canceled", kind: "text" },
    ],
    createKeys: ["DocNum", "DocDate", "Filler", "Comments", "JrnlMemo"],
    patchKeys: ["DocNum", "DocDate", "Filler", "Comments", "JrnlMemo", "Canceled"],
    lines: {
      listPath: (de) => `${API}/stock-transfer-request-lines?doc_entry=${de}`,
      detailPath: (de, ln) => `${API}/stock-transfer-request-lines/${de}/${ln}`,
      postPath: `${API}/stock-transfer-request-lines`,
      columns: [
        { key: "LineNum", label: "#" },
        { key: "ItemCode", label: "Item" },
        { key: "Quantity", label: "Qty" },
        { key: "FromWhsCod", label: "From WH" },
        { key: "WhsCode", label: "To WH" },
        { key: "Price", label: "Price" },
      ],
      editKeys: ["ItemCode", "Quantity", "OpenQty", "Price", "FromWhsCod", "WhsCode", "LineStatus", "TargetType", "TrgetEntry", "BaseRef", "BaseType", "BaseEntry", "BaseLine", "Canceled"],
    },
  },
  {
    id: "str",
    title: "Stock Transfer — OWTR / WTR1",
    listPath: `${API}/stock-transfers`,
    detailPath: (r) => `${API}/stock-transfers/${r.DocEntry}`,
    pkKeys: ["DocEntry"],
    listColumns: [
      { key: "DocEntry", label: "DocEntry" },
      { key: "DocNum", label: "No." },
      { key: "DocDate", label: "Date" },
      { key: "Filler", label: "Filler" },
      { key: "Canceled", label: "Can." },
    ],
    headerFields: [
      { key: "DocEntry", label: "DocEntry", kind: "number", pk: true, readonly: true },
      { key: "DocNum", label: "Document No.", kind: "number" },
      { key: "DocDate", label: "Posting Date", kind: "date" },
      { key: "Filler", label: "Filler", kind: "text" },
      { key: "Comments", label: "Comments", kind: "text" },
      { key: "JrnlMemo", label: "Jrnl Memo", kind: "text" },
      { key: "Canceled", label: "Canceled", kind: "text" },
    ],
    createKeys: ["DocNum", "DocDate", "Filler", "Comments", "JrnlMemo"],
    patchKeys: ["DocNum", "DocDate", "Filler", "Comments", "JrnlMemo", "Canceled"],
    lines: {
      listPath: (de) => `${API}/stock-transfer-lines?doc_entry=${de}`,
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
    title: "Goods Receipt — OIGN / IGN1",
    listPath: `${API}/goods-receipts`,
    detailPath: (r) => `${API}/goods-receipts/${r.DocEntry}`,
    pkKeys: ["DocEntry"],
    listColumns: [
      { key: "DocEntry", label: "DocEntry" },
      { key: "DocNum", label: "No." },
      { key: "DocDate", label: "Date" },
      { key: "Canceled", label: "Can." },
    ],
    headerFields: [
      { key: "DocEntry", label: "DocEntry", kind: "number", pk: true, readonly: true },
      { key: "DocNum", label: "Document No.", kind: "number" },
      { key: "DocDate", label: "Posting Date", kind: "date" },
      { key: "Comments", label: "Comments", kind: "text" },
      { key: "JrnlMemo", label: "Jrnl Memo", kind: "text" },
      { key: "Canceled", label: "Canceled", kind: "text" },
    ],
    createKeys: ["DocNum", "DocDate", "Comments", "JrnlMemo"],
    patchKeys: ["DocNum", "DocDate", "Comments", "JrnlMemo", "Canceled"],
    lines: {
      listPath: (de) => `${API}/goods-receipt-lines?doc_entry=${de}`,
      detailPath: (de, ln) => `${API}/goods-receipt-lines/${de}/${ln}`,
      postPath: `${API}/goods-receipt-lines`,
      columns: [
        { key: "LineNum", label: "#" },
        { key: "ItemCode", label: "Item" },
        { key: "Quantity", label: "Qty" },
        { key: "WhsCode", label: "Warehouse" },
        { key: "Price", label: "Price" },
      ],
      editKeys: ["ItemCode", "Quantity", "WhsCode", "Price", "BaseType", "BaseEntry", "BaseLine", "Canceled"],
    },
  },
  {
    id: "gissue",
    title: "Goods Issue — OIGE / IGE1",
    listPath: `${API}/goods-issues`,
    detailPath: (r) => `${API}/goods-issues/${r.DocEntry}`,
    pkKeys: ["DocEntry"],
    listColumns: [
      { key: "DocEntry", label: "DocEntry" },
      { key: "DocNum", label: "No." },
      { key: "DocDate", label: "Date" },
      { key: "Canceled", label: "Can." },
    ],
    headerFields: [
      { key: "DocEntry", label: "DocEntry", kind: "number", pk: true, readonly: true },
      { key: "DocNum", label: "Document No.", kind: "number" },
      { key: "DocDate", label: "Posting Date", kind: "date" },
      { key: "Comments", label: "Comments", kind: "text" },
      { key: "JrnlMemo", label: "Jrnl Memo", kind: "text" },
      { key: "Canceled", label: "Canceled", kind: "text" },
    ],
    createKeys: ["DocNum", "DocDate", "Comments", "JrnlMemo"],
    patchKeys: ["DocNum", "DocDate", "Comments", "JrnlMemo", "Canceled"],
    lines: {
      listPath: (de) => `${API}/goods-issue-lines?doc_entry=${de}`,
      detailPath: (de, ln) => `${API}/goods-issue-lines/${de}/${ln}`,
      postPath: `${API}/goods-issue-lines`,
      columns: [
        { key: "LineNum", label: "#" },
        { key: "ItemCode", label: "Item" },
        { key: "Quantity", label: "Qty" },
        { key: "WhsCode", label: "Warehouse" },
        { key: "Account", label: "Account" },
        { key: "Price", label: "Price" },
      ],
      editKeys: ["ItemCode", "Quantity", "WhsCode", "Account", "Price", "BaseType", "BaseEntry", "BaseLine", "Canceled"],
    },
  },
  {
    id: "stktake",
    title: "Stock Take — OINC / INC1",
    listPath: `${API}/stock-takes`,
    detailPath: (r) => `${API}/stock-takes/${r.DocEntry}`,
    pkKeys: ["DocEntry"],
    listColumns: [
      { key: "DocEntry", label: "DocEntry" },
      { key: "DocNum", label: "No." },
      { key: "CountDate", label: "Count Date" },
      { key: "Canceled", label: "Can." },
    ],
    headerFields: [
      { key: "DocEntry", label: "DocEntry", kind: "number", pk: true, readonly: true },
      { key: "DocNum", label: "Document No.", kind: "number" },
      { key: "CountDate", label: "Count Date", kind: "date" },
      { key: "Canceled", label: "Canceled", kind: "text" },
    ],
    createKeys: ["DocNum", "CountDate"],
    patchKeys: ["DocNum", "CountDate", "Canceled"],
    lines: {
      listPath: (de) => `${API}/stock-take-lines?doc_entry=${de}`,
      detailPath: (de, ln) => `${API}/stock-take-lines/${de}/${ln}`,
      postPath: `${API}/stock-take-lines`,
      columns: [
        { key: "LineNum", label: "#" },
        { key: "ItemCode", label: "Item" },
        { key: "WhsCode", label: "Warehouse" },
        { key: "InQty", label: "In Qty" },
        { key: "OutQty", label: "Out Qty" },
        { key: "Difference", label: "Diff" },
      ],
      editKeys: ["ItemCode", "WhsCode", "InQty", "OutQty", "Difference", "Price", "Canceled"],
    },
  },
  {
    id: "invpost",
    title: "Inventory Posting — OINM",
    listPath: `${API}/inventory-postings`,
    detailPath: (r) => `${API}/inventory-postings/${r.TransNum}`,
    pkKeys: ["TransNum"],
    listColumns: [
      { key: "TransNum", label: "Trans#" },
      { key: "TransType", label: "Type" },
      { key: "ItemCode", label: "Item" },
      { key: "Warehouse", label: "WH" },
      { key: "InQty", label: "In" },
      { key: "OutQty", label: "Out" },
    ],
    headerFields: [
      { key: "TransNum", label: "Trans Num", kind: "number", pk: true, readonly: true },
      { key: "TransType", label: "Trans Type", kind: "number" },
      { key: "ItemCode", label: "Item", kind: "text" },
      { key: "Warehouse", label: "Warehouse", kind: "text" },
      { key: "InQty", label: "In Qty", kind: "text" },
      { key: "OutQty", label: "Out Qty", kind: "text" },
      { key: "Price", label: "Price", kind: "text" },
      { key: "BASE_REF", label: "Base Ref", kind: "text" },
      { key: "DocTime", label: "Doc Time", kind: "datetime-local" },
      { key: "Canceled", label: "Canceled", kind: "text" },
    ],
    createKeys: ["TransType", "ItemCode", "Warehouse", "InQty", "OutQty", "Price", "BASE_REF"],
    patchKeys: ["TransType", "ItemCode", "Warehouse", "InQty", "OutQty", "Price", "BASE_REF", "DocTime", "Canceled"],
  },
];

export function getInventoryModule(id: string | undefined): InvRegistryEntry | undefined {
  return INVENTORY_REGISTRY.find((m) => m.id === id);
}
