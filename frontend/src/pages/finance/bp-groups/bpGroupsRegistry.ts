import type { InvRegistryEntry } from "../../inventory/registry";
import { BUSINESS_PARTNER_API_ROOT } from "../constants";

/** Workspace / URL segment: ``/finance/bp-groups`` */
export const FINANCE_BP_GROUPS_MODULE_ID = "bp-groups" as const;

export const bpGroupsRegistryEntry: InvRegistryEntry = {
  id: FINANCE_BP_GROUPS_MODULE_ID,
  title: "Business Partner Groups — OCRG",
  listPath: `${BUSINESS_PARTNER_API_ROOT}/groups`,
  detailPath: (r) => `${BUSINESS_PARTNER_API_ROOT}/groups/${r.GroupCode}`,
  pkKeys: ["GroupCode"],
  readonlyEnv: "finance",
  listColumns: [
    { key: "GroupCode", label: "Group Code" },
    { key: "GroupName", label: "Group Name" },
    { key: "GroupType", label: "Type" },
    { key: "Canceled", label: "Canceled" },
  ],
  headerFields: [
    { key: "GroupCode", label: "Group Code", kind: "number", pk: true },
    { key: "GroupName", label: "Group Name", kind: "text" },
    { key: "GroupType", label: "Group Type (B/V)", kind: "text" },
    { key: "Canceled", label: "Canceled", kind: "text" },
  ],
  createKeys: ["GroupCode", "GroupName", "GroupType"],
  patchKeys: ["GroupName", "GroupType", "Canceled"],
};
