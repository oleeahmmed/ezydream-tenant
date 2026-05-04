import type { ComponentType } from "react";
import { useMemo } from "react";
import { getProductionModule } from "./registry";
import { BomWorkspacePane } from "./bom/BomWorkspacePane";
import { ProductionOrderWorkspacePane } from "./production-order/ProductionOrderWorkspacePane";

const PRODUCTION_MODULE_PANES: Record<string, ComponentType<{ tabId: string }>> = {
  "production-order": ProductionOrderWorkspacePane,
  bom: BomWorkspacePane,
};

/** Production workspaces (BOM + production order) under ``pages/production``. */
export function ProductionWorkspacePane({ moduleId, tabId }: { moduleId: string; tabId: string }) {
  const def = useMemo(() => getProductionModule(moduleId), [moduleId]);
  const Pane = PRODUCTION_MODULE_PANES[moduleId];
  if (!Pane || !def) {
    return (
      <div className="workspace-home">
        <p>
          Unknown production module: <strong>{moduleId}</strong>
        </p>
      </div>
    );
  }
  return <Pane tabId={tabId} />;
}
