import { useMemo } from "react";
import { BpGroupsPage } from "./bp-groups/BpGroupsPage";
import { BusinessPartnerPage } from "./business-partner/BusinessPartnerPage";
import { FINANCE_BP_GROUPS_MODULE_ID } from "./bp-groups/bpGroupsRegistry";
import { FINANCE_BUSINESS_PARTNER_MODULE_ID } from "./business-partner/businessPartnerRegistry";
import { getFinanceModule } from "./registry";
import { FinanceBoltCrudPage } from "./shared/FinanceBoltCrudPage";
import { FINANCE_STUB_MODULES } from "./stubs/financeStubModules";
import { FinanceStubPage } from "./stubs/FinanceStubPage";

/** Finance workspace — Bolt CRUD, BP screens, or SAP-table stubs (DB table without Bolt UI yet). */
export function FinanceWorkspacePane({ moduleId, tabId }: { moduleId: string; tabId: string }) {
  const def = useMemo(() => getFinanceModule(moduleId), [moduleId]);

  if (moduleId in FINANCE_STUB_MODULES) {
    return <FinanceStubPage moduleId={moduleId} />;
  }
  if (moduleId === FINANCE_BUSINESS_PARTNER_MODULE_ID) {
    return <BusinessPartnerPage tabId={tabId} />;
  }
  if (moduleId === FINANCE_BP_GROUPS_MODULE_ID) {
    return <BpGroupsPage tabId={tabId} />;
  }
  if (!def) {
    return (
      <div className="workspace-home">
        <p>
          Unknown finance module: <strong>{moduleId}</strong>
        </p>
      </div>
    );
  }
  return <FinanceBoltCrudPage tabId={tabId} moduleId={moduleId} />;
}
