import { useMemo } from "react";
import { getSalesModule } from "../registry";
import { SalesDocumentCrud } from "../shared/SalesDocumentCrud";

/** Sales Quotation (OQUT) — document workspace; list/find/add/edit/delete live in ``SalesDocumentCrud``. */
export function QuotationWorkspacePane({ tabId }: { tabId: string }) {
  const def = useMemo(() => getSalesModule("quotation"), []);
  if (!def) return null;
  return <SalesDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
