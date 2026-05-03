import { useMemo } from "react";
import { getInventoryModule } from "../registry";
import { InventoryDocumentCrud } from "../shared/InventoryDocumentCrud";

export function GreceiptWorkspacePane({ tabId }: { tabId: string }) {
  const def = useMemo(() => getInventoryModule("greceipt"), []);
  if (!def) return null;
  return <InventoryDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
