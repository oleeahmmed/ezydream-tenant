import { useMemo } from "react";
import { getSalesModule } from "../registry";
import { SalesDocumentCrud } from "../shared/SalesDocumentCrud";

export function ReturnWorkspacePane({ tabId }: { tabId: string }) {
  const def = useMemo(() => getSalesModule("return"), []);
  if (!def) return null;
  return <SalesDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
