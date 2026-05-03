import { useMemo } from "react";
import { getInventoryModule } from "../registry";
import { InventoryDocumentCrud } from "../shared/InventoryDocumentCrud";

export function GissueWorkspacePane({ tabId }: { tabId: string }) {
  const def = useMemo(() => getInventoryModule("gissue"), []);
  if (!def) return null;
  return <InventoryDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
