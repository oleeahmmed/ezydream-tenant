/**
 * Quotation document list / search helpers (prefix query for ``GET /api/sales/quotations``).
 * UI wiring lives in ``../shared/SalesDocumentCrud``.
 */
export function quotationListQuery(searchPrefix?: string): string {
  const q = new URLSearchParams({ limit: "100", offset: "0" });
  if (searchPrefix != null && searchPrefix !== "") q.set("q", searchPrefix);
  return `?${q}`;
}
