import { useMemo } from "react";
import { getInventoryModule } from "../registry";
import { InventoryDocumentCrud } from "../shared/InventoryDocumentCrud";

export function ItemWhsWorkspacePane({ tabId }: { tabId: string }) {
  const def = useMemo(() => getInventoryModule("item-whs"), []);
  if (!def) return null;
  return <InventoryDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
