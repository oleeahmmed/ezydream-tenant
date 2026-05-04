/**
 * Core G/L & posting — only what belongs under Finance.
 * Paths ``/finance/…`` open the finance workspace tab.
 */
export type FinanceSidebarItem = { icon?: string; label: string; path?: string; section?: boolean };

export const FINANCE_MENU_GROUP = {
  id: "fin",
  icon: "💰",
  title: "Finance",
  items: [
    { icon: "📊", label: "Chart of Accounts (OACT)", path: "/finance/chart-of-accounts" },
    { icon: "📓", label: "Journal Entries (OJDT)", path: "/finance/journal-entries" },
    { icon: "📄", label: "Journal Lines (JDT1)", path: "/finance/jdt1-lines" },
    { icon: "🎯", label: "Profit Centers (OPRC)", path: "/finance/profit-centers" },
    { icon: "🧾", label: "Tax Codes (OSTC)", path: "/finance/tax-codes" },
    { icon: "📅", label: "Financial Periods (OFPR)", path: "/finance/financial-periods" },
    { icon: "📊", label: "Budget Setup (OBGT)", path: "/finance/budget-setups" },
    { icon: "📈", label: "Budget Lines (BTG1)", path: "/finance/bgt1-lines" },
  ] satisfies FinanceSidebarItem[],
};
