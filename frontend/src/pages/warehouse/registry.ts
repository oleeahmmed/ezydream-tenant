/** Warehouse master CRUD → ``/api/warehouse`` (``apps/warehouse/api/views.py``). */

import type { InvRegistryEntry } from "../inventory/registry";

function enc(s: string): string {
  return encodeURIComponent(s);
}

const API = "/api/warehouse";

export const WAREHOUSE_REGISTRY: InvRegistryEntry[] = [
  {
    id: "warehouses",
    title: "Warehouses — OWHS",
    listPath: `${API}/warehouses`,
    detailPath: (r) => `${API}/warehouses/${enc(String(r.WhsCode ?? "").trim())}`,
    pkKeys: ["WhsCode"],
    listColumns: [
      { key: "WhsCode", label: "Code" },
      { key: "WhsName", label: "Name" },
      { key: "Location", label: "Location" },
      { key: "Inactive", label: "Inactive" },
    ],
    headerFields: [
      { key: "WhsCode", label: "Warehouse Code", kind: "text", pk: true },
      { key: "WhsName", label: "Warehouse Name", kind: "text" },
      { key: "Location", label: "Location", kind: "text" },
      { key: "Inactive", label: "Inactive (Y/N)", kind: "text" },
    ],
    createKeys: ["WhsCode", "WhsName", "Location", "Inactive"],
    patchKeys: ["WhsName", "Location", "Inactive"],
  },
];

export function getWarehouseModule(id: string | undefined): InvRegistryEntry | undefined {
  if (!id) return undefined;
  return WAREHOUSE_REGISTRY.find((m) => m.id === id);
}
