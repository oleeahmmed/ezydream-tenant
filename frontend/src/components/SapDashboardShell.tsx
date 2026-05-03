import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { clearTokens } from "../lib/auth";
import { SapModuleSidebar } from "./SapModuleSidebar";

type SapDashboardShellProps = {
  userLabel: string;
  children?: ReactNode;
};

/** Main window after login — chrome from ``frontend/ui/sap-dash.html``. */
export function SapDashboardShell({ userLabel, children }: SapDashboardShellProps) {
  const nav = useNavigate();
  const [clock, setClock] = useState(() => new Date().toLocaleString());

  useEffect(() => {
    const t = setInterval(() => setClock(new Date().toLocaleString()), 1000);
    return () => clearInterval(t);
  }, []);

  function logout() {
    clearTokens();
    nav("/login", { replace: true });
  }

  return (
    <div id="main-screen">
      <div className="sap-brand-bar">
        <div className="sap-brand-left">
          <div className="sap-mini-logo">SAP</div>
          <span className="sap-brand-title">SAP Business One</span>
          <span className="brand-info">| EzyDream ERP</span>
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
            <div className="dropdown-item">New</div>
            <div className="dropdown-item">Open</div>
            <div className="dropdown-sep" />
            <div className="dropdown-item" onClick={logout} onKeyDown={(e) => e.key === "Enter" && logout()} role="menuitem" tabIndex={0}>
              Log Off
            </div>
          </div>
        </div>
        <div className="menu-item">
          Edit
          <div className="dropdown">
            <div className="dropdown-item">Find</div>
          </div>
        </div>
        <div className="menu-item">
          View
          <div className="dropdown">
            <div className="dropdown-item">Refresh</div>
          </div>
        </div>
        <div className="menu-item">
          Help
          <div className="dropdown">
            <div className="dropdown-item">About SAP Business One</div>
          </div>
        </div>
      </div>

      <div className="toolbar">
        <button type="button" className="tb-btn" title="First Record">
          <div className="tb-icon">⏮</div>
          <div className="tb-label">First</div>
        </button>
        <button type="button" className="tb-btn" title="Previous Record">
          <div className="tb-icon">◀</div>
          <div className="tb-label">Prev</div>
        </button>
        <button type="button" className="tb-btn" title="Next Record">
          <div className="tb-icon">▶</div>
          <div className="tb-label">Next</div>
        </button>
        <button type="button" className="tb-btn" title="Last Record">
          <div className="tb-icon">⏭</div>
          <div className="tb-label">Last</div>
        </button>
        <div className="tb-sep" />
        <button type="button" className="tb-btn" title="Find">
          <div className="tb-icon">🔍</div>
          <div className="tb-label">Find</div>
        </button>
      </div>

      <div className="main-body">
        <SapModuleSidebar />
        <div className="content-area">{children ?? <div className="content-area-empty" aria-label="Empty workspace" />}</div>
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
          <div className="status-led led-yellow" />
          <span>{clock}</span>
        </div>
      </div>
    </div>
  );
}
