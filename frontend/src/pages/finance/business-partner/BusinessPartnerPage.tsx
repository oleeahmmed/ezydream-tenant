import { useMemo } from "react";
import { InventoryDocumentCrud } from "../../inventory/shared/InventoryDocumentCrud";
import { businessPartnerRegistryEntry } from "./businessPartnerRegistry";

/** Business Partner master (OCRD) — finance module screen. */
export function BusinessPartnerPage({ tabId }: { tabId: string }) {
  const def = useMemo(() => businessPartnerRegistryEntry, []);
  return <InventoryDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
