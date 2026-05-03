/** Shared SAP-style document registry (Sales / Purchase / Production orders). */

export type FieldKind = "text" | "number" | "date" | "datetime-local";

export type HeaderField = {
  key: string;
  label: string;
  kind: FieldKind;
  pk?: boolean;
  readonly?: boolean;
};

export type ListCol = { key: string; label: string };

export type DocumentLinesDef = {
  listPath: (parentPk: string | number) => string;
  detailPath: (parentPk: string | number, lineNum: number) => string;
  postPath: string;
  columns: ListCol[];
  editKeys: string[];
  /** Line POST JSON uses ``Father`` (BOM) instead of ``DocEntry``. */
  lineParentFieldInBody?: "DocEntry" | "Father";
};

export type DocumentRegistryEntry = {
  id: string;
  title: string;
  listPath: string;
  detailPath: (row: Record<string, unknown>) => string;
  pkKeys: string[];
  listColumns: ListCol[];
  headerFields: HeaderField[];
  createKeys: string[];
  patchKeys: string[];
  lines: DocumentLinesDef;
  /**
   * Header field that opens BP search (e.g. ``CardCode``). Set to ``null`` for documents
   * without a business partner picker (e.g. purchase request).
   */
  partnerPickerFieldKey?: string | null;
  /** Field updated from BP master (default ``CardName``). */
  partnerNameFieldKey?: string;
  /** Optional currency field copied from BP (sales). */
  partnerCurrencyFieldKey?: string;
  listButtonTitleBp?: string;
  /** Root layout class on ``.sap-doc-root`` (e.g. ``sap-sales-doc``). */
  docRootClassName?: string;
  /** Window shell class (e.g. ``sap-window-sales``). */
  windowClassName?: string;
  /** Header keys shown in the footer left block (remarks / UDF-style). */
  footerLeftKeys?: string[];
  /** Keys rendered in the totals table (right footer). */
  footerTotalsKeys?: string[];
  /** Show currency hint next to totals when ``DocCur`` is present. */
  showDocCurHint?: boolean;
};
