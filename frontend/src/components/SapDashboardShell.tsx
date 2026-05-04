import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { clearTokens } from "../lib/auth";
import { BRAND_NAME, BRAND_NAME_SHORT, BRAND_SUITE } from "../lib/brand";
import { SapModuleSidebar } from "./SapModuleSidebar";
import { HOME_TAB_ID, useWorkspace, type WorkspaceTab } from "../workspace/WorkspaceContext";
import { InventoryWorkspacePane } from "../pages/inventory/InventoryModulePage";
import { PurchaseWorkspacePane } from "../pages/purchase/PurchaseModulePage";
import { ProductionWorkspacePane } from "../pages/production/ProductionModulePage";
import { SalesWorkspacePane } from "../pages/sales/SalesModulePage";
import { FinanceWorkspacePane } from "../pages/finance/FinanceModulePage";
import { WarehouseWorkspacePane } from "../pages/warehouse/WarehouseModulePage";

type SapDashboardShellProps = {
  userLabel: string;
};

function HomeWorkspacePane() {
  return (
    <div className="workspace-home">
      <h1>Welcome</h1>
      <p>
        Open forms from the module menu on the left. Each document opens in its own tab — use the tab bar to switch or close windows.
      </p>
      <p>Use the toolbar (First, Prev, Next, Last, New, Find, Print) or the File / Edit / View menus for the active tab.</p>
    </div>
  );
}

/** Main window after login — chrome from ``frontend/ui/sap-dash.html`` (multi-tab workspace). */
export function SapDashboardShell({ userLabel }: SapDashboardShellProps) {
  const nav = useNavigate();
  const {
    tabs,
    activeTabId,
    switchTab,
    closeTab,
    runFind,
    runNew,
    runFirst,
    runPrev,
    runNext,
    runLast,
    runPrint,
    udfSidebarVisible,
    toggleUdfSidebar,
  } = useWorkspace();
  const [clock, setClock] = useState(() => new Date().toLocaleString());

  useEffect(() => {
    const t = setInterval(() => setClock(new Date().toLocaleString()), 1000);
    return () => clearInterval(t);
  }, []);

  function logout() {
    clearTokens();
    nav("/login", { replace: true });
  }

  function onCloseTab(e: React.MouseEvent, id: string) {
    e.stopPropagation();
    closeTab(id);
  }

  return (
    <div id="main-screen">
      <div className="sap-brand-bar">
        <div className="sap-brand-left">
          <div className="sap-mini-logo">{BRAND_NAME_SHORT}</div>
          <span className="sap-brand-title">{BRAND_NAME}</span>
          <span className="brand-info">| {BRAND_SUITE}</span>
        </div>
        <div className="sap-brand-right">
          <span className="brand-info">{clock}</span>
          <div className="brand-user-chip">
            <span>👤</span>
            <span>{userLabel}</span>
          </div>
          <button type="button" className="brand-info" style={{ cursor: "pointer", border: "none", background: "none", padding: 0, color: "#90b8d8" }} onClick={logout} title="Log Off">
            🔴 Log Off
          </button>
        </div>
      </div>

      <div className="menu-bar">
        <div className="menu-item">
          File
          <div className="dropdown">
            <div className="dropdown-item" onClick={() => runNew()} onKeyDown={(e) => e.key === "Enter" && runNew()} role="menuitem" tabIndex={0}>
              New
            </div>
            <div className="dropdown-item" onClick={() => runFind()} onKeyDown={(e) => e.key === "Enter" && runFind()} role="menuitem" tabIndex={0}>
              Open…
            </div>
            <div className="dropdown-item" onClick={() => runPrint()} onKeyDown={(e) => e.key === "Enter" && runPrint()} role="menuitem" tabIndex={0}>
              Print
            </div>
            <div className="dropdown-sep" />
            <div className="dropdown-item" onClick={logout} onKeyDown={(e) => e.key === "Enter" && logout()} role="menuitem" tabIndex={0}>
              Log Off
            </div>
          </div>
        </div>
        <div className="menu-item">
          Edit
          <div className="dropdown">
            <div className="dropdown-item" onClick={() => runFind()} onKeyDown={(e) => e.key === "Enter" && runFind()} role="menuitem" tabIndex={0}>
              Find
            </div>
          </div>
        </div>
        <div className="menu-item">
          View
          <div className="dropdown">
            <div className="dropdown-item" onClick={() => runFind()} onKeyDown={(e) => e.key === "Enter" && runFind()} role="menuitem" tabIndex={0}>
              Refresh
            </div>
            <div
              className="dropdown-item"
              onClick={() => toggleUdfSidebar()}
              onKeyDown={(e) => e.key === "Enter" && toggleUdfSidebar()}
              role="menuitem"
              tabIndex={0}
            >
              {udfSidebarVisible ? "✓ " : ""}
              User-Defined Fields
            </div>
          </div>
        </div>
        <div className="menu-item">
          Help
          <div className="dropdown">
            <div className="dropdown-item">About {BRAND_NAME}</div>
          </div>
        </div>
      </div>

      <div className="toolbar">
        <button type="button" className="tb-btn" title="First Record" onClick={() => runFirst()}>
          <div className="tb-icon">⏮</div>
          <div className="tb-label">First</div>
        </button>
        <button type="button" className="tb-btn" title="Previous Record" onClick={() => runPrev()}>
          <div className="tb-icon">◀</div>
          <div className="tb-label">Prev</div>
        </button>
        <button type="button" className="tb-btn" title="Next Record" onClick={() => runNext()}>
          <div className="tb-icon">▶</div>
          <div className="tb-label">Next</div>
        </button>
        <button type="button" className="tb-btn" title="Last Record" onClick={() => runLast()}>
          <div className="tb-icon">⏭</div>
          <div className="tb-label">Last</div>
        </button>
        <div className="tb-sep" />
        <button type="button" className="tb-btn" title="New" onClick={() => runNew()}>
          <div className="tb-icon">📄</div>
          <div className="tb-label">New</div>
        </button>
        <button type="button" className="tb-btn" title="Find" onClick={() => runFind()}>
          <div className="tb-icon">🔍</div>
          <div className="tb-label">Find</div>
        </button>
        <div className="tb-sep" />
        <button type="button" className="tb-btn" title="Print" onClick={() => runPrint()}>
          <div className="tb-icon">🖨</div>
          <div className="tb-label">Print</div>
        </button>
      </div>

      <div className="main-body">
        <SapModuleSidebar />
        <div className="content-area">
          <div className="content-tabs" role="tablist">
            {tabs.map((tab: WorkspaceTab) => (
              <div
                key={tab.id}
                className={`content-tab${activeTabId === tab.id ? " active" : ""}`}
                onClick={() => switchTab(tab.id)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    switchTab(tab.id);
                  }
                }}
                role="tab"
                aria-selected={activeTabId === tab.id}
                tabIndex={activeTabId === tab.id ? 0 : -1}
              >
                <span className="tab-label">{tab.label}</span>
                {tab.id !== HOME_TAB_ID ? (
                  <span
                    className="tab-close"
                    title="Close"
                    onClick={(e) => onCloseTab(e, tab.id)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        e.stopPropagation();
                        closeTab(tab.id);
                      }
                    }}
                    role="button"
                    tabIndex={0}
                  >
                    ✕
                  </span>
                ) : null}
              </div>
            ))}
          </div>
          {tabs.map((tab: WorkspaceTab) => (
            <div
              key={tab.id}
              className="content-pane"
              role="tabpanel"
              hidden={activeTabId !== tab.id}
              style={{ display: activeTabId === tab.id ? "flex" : "none", flexDirection: "column" }}
            >
              {tab.kind === "home" ? <HomeWorkspacePane /> : null}
              {tab.kind === "inventory" && tab.moduleId ? <InventoryWorkspacePane moduleId={tab.moduleId} tabId={tab.id} /> : null}
              {tab.kind === "sales" && tab.salesModuleId ? <SalesWorkspacePane salesModuleId={tab.salesModuleId} tabId={tab.id} /> : null}
              {tab.kind === "purchase" && tab.purchaseModuleId ? <PurchaseWorkspacePane moduleId={tab.purchaseModuleId} tabId={tab.id} /> : null}
              {tab.kind === "production" && tab.productionModuleId ? <ProductionWorkspacePane moduleId={tab.productionModuleId} tabId={tab.id} /> : null}
              {tab.kind === "finance" && tab.financeModuleId ? <FinanceWorkspacePane moduleId={tab.financeModuleId} tabId={tab.id} /> : null}
              {tab.kind === "warehouse" && tab.warehouseModuleId ? (
                <WarehouseWorkspacePane moduleId={tab.warehouseModuleId} tabId={tab.id} />
              ) : null}
            </div>
          ))}
        </div>
      </div>

      <div className="status-bar">
        <div className="status-seg">
          <div className="status-led led-green" />
          <span>Connected</span>
        </div>
        <div className="status-seg">
          User: <strong>{userLabel}</strong>
        </div>
        <div className="status-seg">
          <span>{tabs.find((t: WorkspaceTab) => t.id === activeTabId)?.label ?? ""}</span>
        </div>
        <div className="status-seg">
          <div className="status-led led-yellow" />
          <span>{clock}</span>
        </div>
      </div>
    </div>
  );
}
