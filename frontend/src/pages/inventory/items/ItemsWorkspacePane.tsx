import { useMemo } from "react";
import { getInventoryModule } from "../registry";
import { InventoryDocumentCrud } from "../shared/InventoryDocumentCrud";

export function ItemsWorkspacePane({ tabId }: { tabId: string }) {
  const def = useMemo(() => getInventoryModule("items"), []);
  if (!def) return null;
  return <InventoryDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
