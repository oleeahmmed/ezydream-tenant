import { useMemo } from "react";
import { getInventoryModule } from "../registry";
import { InventoryDocumentCrud } from "../shared/InventoryDocumentCrud";

export function StktakeWorkspacePane({ tabId }: { tabId: string }) {
  const def = useMemo(() => getInventoryModule("stktake"), []);
  if (!def) return null;
  return <InventoryDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
