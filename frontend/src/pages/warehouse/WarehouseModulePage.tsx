import { useMemo } from "react";
import { InventoryDocumentCrud } from "../inventory/shared/InventoryDocumentCrud";
import { getWarehouseModule } from "./registry";

/** OWHS master — same CRUD shell as inventory masters (list uses ``active_only`` default on API). */
export function WarehouseWorkspacePane({ moduleId, tabId }: { moduleId: string; tabId: string }) {
  const def = useMemo(() => getWarehouseModule(moduleId), [moduleId]);
  if (!def) {
    return (
      <div className="workspace-home">
        <p>
          Unknown warehouse module: <strong>{moduleId}</strong>
        </p>
      </div>
    );
  }
  return <InventoryDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
