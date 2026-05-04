/** BP master — same finance routes, separate menu from G/L. */
export type BpSidebarItem = { icon?: string; label: string; path?: string; section?: boolean };

export const BUSINESS_PARTNER_MENU_GROUP = {
  id: "bp",
  icon: "👥",
  title: "Business partners",
  items: [
    { icon: "👤", label: "Business Partner (OCRD)", path: "/finance/business-partner" },
    { icon: "📂", label: "BP Groups (OCRG)", path: "/finance/bp-groups" },
  ] satisfies BpSidebarItem[],
};
