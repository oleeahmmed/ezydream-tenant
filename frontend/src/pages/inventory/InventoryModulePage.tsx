import type { ComponentType } from "react";
import { useMemo } from "react";
import { getInventoryModule } from "./registry";
import { getInventorySapModule, INVENTORY_SAP_MODULE_IDS } from "./inventorySapRegistry";
import { SapDocumentCrud } from "../shared/SapDocumentCrud";
import { InvpostWorkspacePane } from "./invpost/InvpostWorkspacePane";
import { ItemGroupsWorkspacePane } from "./item-groups/ItemGroupsWorkspacePane";
import { ItemWhsWorkspacePane } from "./item-whs/ItemWhsWorkspacePane";
import { ItemsWorkspacePane } from "./items/ItemsWorkspacePane";
import { UomWorkspacePane } from "./uom/UomWorkspacePane";

const INVENTORY_MODULE_PANES: Record<string, ComponentType<{ tabId: string }>> = {
  "item-groups": ItemGroupsWorkspacePane,
  items: ItemsWorkspacePane,
  "item-whs": ItemWhsWorkspacePane,
  uom: UomWorkspacePane,
  invpost: InvpostWorkspacePane,
};

/** Masters use ``InventoryDocumentCrud``; stock documents use ``SapDocumentCrud`` (same shell as Sales/Purchase). */
export function InventoryWorkspacePane({ moduleId, tabId }: { moduleId: string; tabId: string }) {
  const sapDef = useMemo(() => (INVENTORY_SAP_MODULE_IDS.has(moduleId) ? getInventorySapModule(moduleId) : undefined), [moduleId]);
  if (sapDef) {
    return <SapDocumentCrud key={tabId} def={sapDef} workspaceTabId={tabId} />;
  }

  const def = useMemo(() => getInventoryModule(moduleId), [moduleId]);
  const Pane = INVENTORY_MODULE_PANES[moduleId];
  if (!Pane || !def) {
    return (
      <div className="workspace-home">
        <p>
          Unknown inventory module: <strong>{moduleId}</strong>
        </p>
      </div>
    );
  }
  return <Pane tabId={tabId} />;
}
