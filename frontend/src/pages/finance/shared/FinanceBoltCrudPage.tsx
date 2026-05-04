import { useMemo } from "react";
import { InventoryDocumentCrud } from "../../inventory/shared/InventoryDocumentCrud";
import { getFinanceModule } from "../registry";

/** Generic CRUD for ``/api/finance`` registry entries (see ``erpBoltRegistry``). */
export function FinanceBoltCrudPage({ tabId, moduleId }: { tabId: string; moduleId: string }) {
  const def = useMemo(() => getFinanceModule(moduleId), [moduleId]);
  if (!def) return null;
  return <InventoryDocumentCrud key={`${tabId}-${moduleId}`} def={def} workspaceTabId={tabId} />;
}
