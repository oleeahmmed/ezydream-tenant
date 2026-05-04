/** Payments & bank-style documents — still ``/finance/…`` routes, own sidebar group. */
export type BankingSidebarItem = { icon?: string; label: string; path?: string; section?: boolean };

export const BANKING_MENU_GROUP = {
  id: "bnk",
  icon: "🏦",
  title: "Banking",
  items: [
    { icon: "💵", label: "Incoming Payments (ORCT)", path: "/finance/incoming-payments" },
    { icon: "📃", label: "Incoming Payment Lines (RCT1)", path: "/finance/rct1-lines" },
    { icon: "💸", label: "Outgoing Payments (OVPM)", path: "/finance/outgoing-payments" },
    { icon: "📃", label: "Outgoing Payment Lines (VPM1)", path: "/finance/vpm1-lines" },
    { icon: "🔄", label: "Internal Reconciliation (OITL)", path: "/finance/internal-recon" },
    { icon: "📄", label: "Internal Recon. Lines (ITL1)", path: "/finance/itl1-lines" },
    { icon: "🔀", label: "Bank Transfer (OIBT)", path: "/finance/bank-transfer" },
  ] satisfies BankingSidebarItem[],
};
