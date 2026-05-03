import { useMemo } from "react";
import { getSalesModule } from "../registry";
import { SalesDocumentCrud } from "../shared/SalesDocumentCrud";

export function InvoiceWorkspacePane({ tabId }: { tabId: string }) {
  const def = useMemo(() => getSalesModule("invoice"), []);
  if (!def) return null;
  return <SalesDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
