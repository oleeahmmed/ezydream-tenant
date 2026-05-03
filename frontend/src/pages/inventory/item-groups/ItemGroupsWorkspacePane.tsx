import { useMemo } from "react";
import { getInventoryModule } from "../registry";
import { InventoryDocumentCrud } from "../shared/InventoryDocumentCrud";

export function ItemGroupsWorkspacePane({ tabId }: { tabId: string }) {
  const def = useMemo(() => getInventoryModule("item-groups"), []);
  if (!def) return null;
  return <InventoryDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
