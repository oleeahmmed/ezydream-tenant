import type { ComponentType } from "react";
import { useMemo } from "react";
import { getInventoryModule } from "./registry";
import { GreceiptWorkspacePane } from "./greceipt/GreceiptWorkspacePane";
import { GissueWorkspacePane } from "./gissue/GissueWorkspacePane";
import { InvpostWorkspacePane } from "./invpost/InvpostWorkspacePane";
import { ItemGroupsWorkspacePane } from "./item-groups/ItemGroupsWorkspacePane";
import { ItemWhsWorkspacePane } from "./item-whs/ItemWhsWorkspacePane";
import { ItemsWorkspacePane } from "./items/ItemsWorkspacePane";
import { StrReqWorkspacePane } from "./str-req/StrReqWorkspacePane";
import { StktakeWorkspacePane } from "./stktake/StktakeWorkspacePane";
import { StrWorkspacePane } from "./str/StrWorkspacePane";
import { UomWorkspacePane } from "./uom/UomWorkspacePane";

const INVENTORY_MODULE_PANES: Record<string, ComponentType<{ tabId: string }>> = {
  "item-groups": ItemGroupsWorkspacePane,
  items: ItemsWorkspacePane,
  "item-whs": ItemWhsWorkspacePane,
  uom: UomWorkspacePane,
  "str-req": StrReqWorkspacePane,
  str: StrWorkspacePane,
  greceipt: GreceiptWorkspacePane,
  gissue: GissueWorkspacePane,
  stktake: StktakeWorkspacePane,
  invpost: InvpostWorkspacePane,
};

/** One pane per inventory module under ``pages/inventory/<module>/`` (mirrors sales layout). */
export function InventoryWorkspacePane({ moduleId, tabId }: { moduleId: string; tabId: string }) {
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
