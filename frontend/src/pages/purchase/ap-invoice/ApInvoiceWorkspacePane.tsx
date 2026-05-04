import { useMemo } from "react";
import { getPurchaseModule } from "../registry";
import { SapDocumentCrud } from "../../shared/SapDocumentCrud";

export function ApInvoiceWorkspacePane({ tabId }: { tabId: string }) {
  const def = useMemo(() => getPurchaseModule("ap-invoice"), []);
  if (!def) return null;
  return <SapDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
