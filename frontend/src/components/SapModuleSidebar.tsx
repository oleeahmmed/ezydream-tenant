import { useMemo, useState } from "react";
import { useWorkspace } from "../workspace/WorkspaceContext";

type Item = { icon: string; label: string; path?: string };
type Group = { id: string; icon: string; title: string; items: Item[] };

const MENU: Group[] = [
  {
    id: "fin",
    icon: "💰",
    title: "Financials",
    items: [
      { icon: "📊", label: "Chart of Accounts" },
      { icon: "📓", label: "Journal Entry" },
    ],
  },
  {
    id: "sales",
    icon: "🛒",
    title: "Sales – A/R",
    items: [
      { icon: "📄", label: "Sales Quotation (OQUT)", path: "/sales/quotation" },
      { icon: "📦", label: "Sales Order (ORDR)", path: "/sales/sales-order" },
      { icon: "🚚", label: "Delivery (ODLN)", path: "/sales/delivery" },
      { icon: "↩️", label: "Return (ORDN)", path: "/sales/return" },
      { icon: "🧾", label: "A/R Invoice (OINV)", path: "/sales/invoice" },
    ],
  },
  {
    id: "inv",
    icon: "📦",
    title: "Inventory",
    items: [
      { icon: "📂", label: "Item Groups (OITB)", path: "/inventory/item-groups" },
      { icon: "🔖", label: "Item Master (OITM)", path: "/inventory/items" },
      { icon: "🏭", label: "Item + Warehouse (OITW)", path: "/inventory/item-whs" },
      { icon: "📏", label: "Units of Measure (OUOM)", path: "/inventory/uom" },
      { icon: "📋", label: "Stock Tfr Request (OWTQ)", path: "/inventory/str-req" },
      { icon: "🔄", label: "Stock Transfer (OWTR)", path: "/inventory/str" },
      { icon: "📥", label: "Goods Receipt (OIGN)", path: "/inventory/greceipt" },
      { icon: "📤", label: "Goods Issue (OIGE)", path: "/inventory/gissue" },
      { icon: "🔢", label: "Stock Take (OINC)", path: "/inventory/stktake" },
      { icon: "📊", label: "Inventory Posting (OINM)", path: "/inventory/invpost" },
    ],
  },
];

/** Left module tree — opens workspace tabs for each module. */
export function SapModuleSidebar() {
  const { openInventoryModule, openSalesModule, activeNavPath } = useWorkspace();
  const [openId, setOpenId] = useState<string | null>("inv");
  const [q, setQ] = useState("");

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    if (!needle) return MENU;
    return MENU.map((g) => ({
      ...g,
      items: g.items.filter((it) => it.label.toLowerCase().includes(needle)),
    })).filter((g) => g.items.length > 0);
  }, [q]);

  return (
    <div className="left-panel">
      <div className="module-search">
        <span className="module-search-icon" aria-hidden>
          <svg viewBox="0 0 16 16" width="14" height="14" focusable="false">
            <circle cx="6.5" cy="6.5" r="4" fill="none" stroke="currentColor" strokeWidth="1.4" />
            <path d="M9.2 9.2 L13.5 13.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
          </svg>
        </span>
        <input
          className="module-search-input"
          placeholder="Search menu..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
          aria-label="Search menu"
        />
      </div>
      <div className="left-menu">
        {filtered.map((g) => {
          const open = openId === g.id;
          return (
            <div key={g.id} className="module-group">
              <div
                className={`module-group-header${open ? " active" : ""}`}
                onClick={() => setOpenId(open ? null : g.id)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    setOpenId(open ? null : g.id);
                  }
                }}
                role="button"
                tabIndex={0}
              >
                <span className={`tree-arrow${open ? " open" : ""}`}>▶</span>
                <span className="module-group-icon">{g.icon}</span>
                <span>{g.title}</span>
              </div>
              <div className={`module-children${open ? " open" : ""}`}>
                {g.items.map((it) => (
                  <div
                    key={it.label}
                    className={`module-child${it.path && activeNavPath === it.path ? " selected" : ""}`}
                    onClick={() => {
                      if (!it.path) return;
                      const inv = it.path.match(/^\/inventory\/([^/]+)\/?$/)?.[1];
                      if (inv) {
                        openInventoryModule(inv, it.label, it.path);
                        return;
                      }
                      const sal = it.path.match(/^\/sales\/([^/]+)\/?$/)?.[1];
                      if (sal) openSalesModule(sal, it.label, it.path);
                    }}
                    onKeyDown={(e) => {
                      if ((e.key === "Enter" || e.key === " ") && it.path) {
                        e.preventDefault();
                        const inv = it.path.match(/^\/inventory\/([^/]+)\/?$/)?.[1];
                        if (inv) {
                          openInventoryModule(inv, it.label, it.path);
                          return;
                        }
                        const sal = it.path.match(/^\/sales\/([^/]+)\/?$/)?.[1];
                        if (sal) openSalesModule(sal, it.label, it.path);
                      }
                    }}
                    role={it.path ? "button" : undefined}
                    tabIndex={it.path ? 0 : undefined}
                    style={it.path ? { cursor: "pointer" } : undefined}
                  >
                    <span className="module-child-icon">{it.icon}</span>
                    {it.label}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
