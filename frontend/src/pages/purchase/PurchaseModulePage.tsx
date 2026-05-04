import type { ComponentType } from "react";
import { useMemo } from "react";
import { getPurchaseModule } from "./registry";
import { ApInvoiceWorkspacePane } from "./ap-invoice/ApInvoiceWorkspacePane";
import { GoodsReceiptPoWorkspacePane } from "./goods-receipt-po/GoodsReceiptPoWorkspacePane";
import { PurchaseOrderWorkspacePane } from "./purchase-order/PurchaseOrderWorkspacePane";
import { PurchaseRequestWorkspacePane } from "./purchase-request/PurchaseRequestWorkspacePane";
import { VendorReturnWorkspacePane } from "./vendor-return/VendorReturnWorkspacePane";

const PURCHASE_MODULE_PANES: Record<string, ComponentType<{ tabId: string }>> = {
  "purchase-request": PurchaseRequestWorkspacePane,
  "purchase-order": PurchaseOrderWorkspacePane,
  "goods-receipt-po": GoodsReceiptPoWorkspacePane,
  "vendor-return": VendorReturnWorkspacePane,
  "ap-invoice": ApInvoiceWorkspacePane,
};

/** Purchase A/P document workspaces (one folder per module under ``pages/purchase``). */
export function PurchaseWorkspacePane({ moduleId, tabId }: { moduleId: string; tabId: string }) {
  const def = useMemo(() => getPurchaseModule(moduleId), [moduleId]);
  const Pane = PURCHASE_MODULE_PANES[moduleId];
  if (!Pane || !def) {
    return (
      <div className="workspace-home">
        <p>
          Unknown purchase module: <strong>{moduleId}</strong>
        </p>
      </div>
    );
  }
  return <Pane tabId={tabId} />;
}
