import type { InvRegistryEntry } from "../inventory/registry";
import { businessPartnerRegistryEntry } from "./business-partner/businessPartnerRegistry";
import { bpGroupsRegistryEntry } from "./bp-groups/bpGroupsRegistry";
import { FINANCE_BOLT_REGISTRY } from "./erpBoltRegistry";

/** Finance workspace registry: Bolt ``/api/finance``, BP API, then bolt-backed masters. */
export const FINANCE_REGISTRY: InvRegistryEntry[] = [
  businessPartnerRegistryEntry,
  bpGroupsRegistryEntry,
  ...FINANCE_BOLT_REGISTRY,
];

export function getFinanceModule(id: string): InvRegistryEntry | undefined {
  return FINANCE_REGISTRY.find((e) => e.id === id);
}
