import { useMemo } from "react";
import { getProductionModule } from "../registry";
import { SapDocumentCrud } from "../../shared/SapDocumentCrud";

export function BomWorkspacePane({ tabId }: { tabId: string }) {
  const def = useMemo(() => getProductionModule("bom"), []);
  if (!def) return null;
  return <SapDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
