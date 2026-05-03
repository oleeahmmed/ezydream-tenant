import type { ComponentType } from "react";
import { getSalesModule } from "./registry";
import { DeliveryWorkspacePane } from "./delivery/DeliveryWorkspacePane";
import { InvoiceWorkspacePane } from "./invoice/InvoiceWorkspacePane";
import { QuotationWorkspacePane } from "./quotation/QuotationWorkspacePane";
import { ReturnWorkspacePane } from "./return/ReturnWorkspacePane";
import { SalesOrderWorkspacePane } from "./sales-order/SalesOrderWorkspacePane";

const SALES_MODULE_PANES: Record<string, ComponentType<{ tabId: string }>> = {
  quotation: QuotationWorkspacePane,
  "sales-order": SalesOrderWorkspacePane,
  delivery: DeliveryWorkspacePane,
  return: ReturnWorkspacePane,
  invoice: InvoiceWorkspacePane,
};

/** Opens the correct sales A/R document workspace (one folder per module under ``pages/sales``). */
export function SalesWorkspacePane({ salesModuleId, tabId }: { salesModuleId: string; tabId: string }) {
  const Pane = SALES_MODULE_PANES[salesModuleId];
  const def = getSalesModule(salesModuleId);
  if (!Pane || !def) {
    return (
      <div className="workspace-home">
        <p>
          Unknown sales module: <strong>{salesModuleId}</strong>
        </p>
      </div>
    );
  }
  return <Pane tabId={tabId} />;
}
