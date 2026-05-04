/** SAP table stubs: DB model exists (see ``apps/finance/models.py``); Bolt CRUD not wired yet. */
export const FINANCE_STUB_MODULES: Record<string, { sap: string; title: string; hint?: string }> = {
  "asset-classes": { sap: "OACD", title: "Asset Classes", hint: "Table OACD — use Django admin or add Bolt routes." },
  administration: { sap: "OADM", title: "Administration Setup", hint: "Table OADM — company / financial defaults." },
  "asset-groups": { sap: "OAGS", title: "Asset Groups", hint: "Table OAGS." },
  "credit-cards": { sap: "OCTD", title: "Credit Card Management", hint: "Table OCTD." },
  "vat-groups": { sap: "OVTG", title: "VAT Groups", hint: "Table OVTG (distinct from tax codes OSTC)." },
  "ar-credit-memo": { sap: "ORIN / RIN1", title: "A/R Credit Memos", hint: "Not implemented in this codebase yet." },
  "asset-values": { sap: "OFAV", title: "Asset Values", hint: "Table OFAV." },
  "asset-revaluation": { sap: "OAFR", title: "Asset Revaluation", hint: "Table OAFR." },
  "asset-class-areas": { sap: "AAC1", title: "Asset Classes — Depreciation Areas", hint: "Table AAC1." },
  "depreciation-run": { sap: "ODRN", title: "Depreciation Run", hint: "Table ODRN." },
  "internal-recon": { sap: "OITL", title: "Internal Reconciliation (Header)", hint: "Table OITL." },
  "itl1-lines": { sap: "ITL1", title: "Internal Reconciliation Lines", hint: "Table ITL1 — child of OITL." },
  "bank-transfer": { sap: "OIBT", title: "Bank Transfer", hint: "Table OIBT." },
};
