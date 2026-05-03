import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { postLogin } from "../api/auth";
import { setTokens } from "../lib/auth";
import { SapButton } from "./SapButton";

/** Login window — layout and classes from ``frontend/ui/sap-dash.html`` */
export function SapLoginScreen() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const data = await postLogin(email, password);
      if (data.otp_required) {
        setError(data.detail || "OTP required — check email or disable OTP for this user.");
        return;
      }
      if (!data.access || !data.refresh) {
        setError("Unexpected response from server.");
        return;
      }
      setTokens(data.access, data.refresh);
      nav("/", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div id="login-screen">
      <div className="login-window login-shadow">
        <div className="login-titlebar">
          <div className="login-titlebar-left">
            <div className="login-titlebar-icon">S</div>
            <span className="login-titlebar-text">SAP Business One - Log On</span>
          </div>
          <div className="login-titlebar-btns">
            <button type="button" className="win-btn" title="Minimize">
              ─
            </button>
            <button type="button" className="win-btn" title="Close">
              ✕
            </button>
          </div>
        </div>
        <div className="login-body">
          <div className="login-side-banner">
            <div className="sap-logo-big">SAP</div>
            <div className="login-side-text">
              <b>Business One</b>
              <br />
              version 9.3
            </div>
            <div className="login-side-text" style={{ marginTop: 12, fontSize: 9 }}>
              Powered by SAP HANA
              <br />© 2018 SAP SE
            </div>
          </div>
          <div className="login-form-area">
            <div className="login-form-title">Please enter your login information</div>
            <form onSubmit={onSubmit}>
              {error ? <div className="login-error">{error}</div> : null}
              <div className="form-row">
                <label htmlFor="user-id">User ID:</label>
                <input
                  id="user-id"
                  name="email"
                  type="email"
                  autoComplete="username"
                  autoFocus
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="email@company.com"
                />
              </div>
              <div className="form-row">
                <label htmlFor="password">Password:</label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <div className="checkbox-row" style={{ marginTop: 8 }}>
                <input id="win-account" type="checkbox" />
                <label htmlFor="win-account">Logon with Windows Account</label>
              </div>
              <div className="form-buttons">
                <SapButton
                  type="button"
                  onClick={() => {
                    setEmail("");
                    setPassword("");
                  }}
                >
                  Cancel
                </SapButton>
                <SapButton type="button">Change Password</SapButton>
                <SapButton type="submit" primary disabled={busy}>
                  {busy ? "…" : "OK"}
                </SapButton>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
