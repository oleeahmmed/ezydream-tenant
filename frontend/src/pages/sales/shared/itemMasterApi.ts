import { apiFetch } from "../../../lib/apiFetch";
import type { Row } from "./formset";

const ITEM_DETAIL = "/api/inventory/items";

/** GET single item master (OITM) by ``ItemCode`` — used to fill line description, warehouse, UoM. */
export async function fetchItemByCode(itemCode: string): Promise<Row> {
  const code = itemCode.trim();
  if (!code) throw new Error("Empty item code");
  const path = `${ITEM_DETAIL}/${encodeURIComponent(code)}`;
  return apiFetch<Row>(path);
}
