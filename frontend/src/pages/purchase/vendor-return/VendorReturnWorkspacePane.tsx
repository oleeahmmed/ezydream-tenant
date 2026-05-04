import { useMemo } from "react";
import { getPurchaseModule } from "../registry";
import { SapDocumentCrud } from "../../shared/SapDocumentCrud";

export function VendorReturnWorkspacePane({ tabId }: { tabId: string }) {
  const def = useMemo(() => getPurchaseModule("vendor-return"), []);
  if (!def) return null;
  return <SapDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
