import { useMemo } from "react";
import { getPurchaseModule } from "../registry";
import { SapDocumentCrud } from "../../shared/SapDocumentCrud";

export function PurchaseRequestWorkspacePane({ tabId }: { tabId: string }) {
  const def = useMemo(() => getPurchaseModule("purchase-request"), []);
  if (!def) return null;
  return <SapDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
