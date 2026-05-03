import { useMemo } from "react";
import { getSalesModule } from "../registry";
import { SalesDocumentCrud } from "../shared/SalesDocumentCrud";

export function SalesOrderWorkspacePane({ tabId }: { tabId: string }) {
  const def = useMemo(() => getSalesModule("sales-order"), []);
  if (!def) return null;
  return <SalesDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
