import { useMemo } from "react";
import { getPurchaseModule } from "../registry";
import { SapDocumentCrud } from "../../shared/SapDocumentCrud";

export function GoodsReceiptPoWorkspacePane({ tabId }: { tabId: string }) {
  const def = useMemo(() => getPurchaseModule("goods-receipt-po"), []);
  if (!def) return null;
  return <SapDocumentCrud key={tabId} def={def} workspaceTabId={tabId} />;
}
