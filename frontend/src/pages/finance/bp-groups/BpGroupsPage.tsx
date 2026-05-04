import { useMemo } from "react";
import { InventoryDocumentCrud } from "../../inventory/shared/InventoryDocumentCrud";
import { bpGroupsRegistryEntry } from "./bpGroupsRegistry";

/** BP Groups master (OCRG) — finance module screen. */
export function BpGroupsPage({ tabId }: { tabId: string }) {
  const def = useMemo(() => bpGroupsRegistryEntry, []);
  return <InventoryDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
