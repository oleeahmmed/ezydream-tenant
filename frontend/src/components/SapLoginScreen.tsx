import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { postLogin } from "../api/auth";
import { setTokens } from "../lib/auth";
import { BRAND_NAME, BRAND_NAME_SHORT, BRAND_SUITE } from "../lib/brand";
import { SapButton } from "./SapButton";

/** Login — modern card layout (styles in ``sap-theme.css``). */
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
            <div className="login-titlebar-icon" aria-hidden>
              {BRAND_NAME_SHORT.slice(0, 1)}
            </div>
            <span className="login-titlebar-text">{BRAND_NAME}</span>
          </div>
          <div className="login-titlebar-btns" aria-hidden>
            <span className="win-btn win-btn--fake" title="Minimize">
              ─
            </span>
            <span className="win-btn win-btn--fake" title="Close">
              ✕
            </span>
          </div>
        </div>
        <div className="login-body">
          <div className="login-side-banner">
            <div className="sap-logo-big">{BRAND_NAME_SHORT}</div>
            <div className="login-side-text">
              <b>{BRAND_NAME}</b>
              <br />
              {BRAND_SUITE}
            </div>
            <p className="login-side-tagline">Secure workspace access</p>
          </div>
          <div className="login-form-area">
            <h1 className="login-form-title">Sign in</h1>
            <p className="login-form-sub">Use your work email and password.</p>
            <form onSubmit={onSubmit} className="login-form">
              {error ? (
                <div className="login-error" role="alert">
                  {error}
                </div>
              ) : null}
              <div className="form-row">
                <label htmlFor="user-id">Email</label>
                <input
                  id="user-id"
                  name="email"
                  type="email"
                  autoComplete="username"
                  autoFocus
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@company.com"
                />
              </div>
              <div className="form-row">
                <label htmlFor="password">Password</label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                />
              </div>
              <div className="form-buttons">
                <SapButton
                  type="button"
                  onClick={() => {
                    setEmail("");
                    setPassword("");
                    setError("");
                  }}
                >
                  Clear
                </SapButton>
                <SapButton type="submit" primary disabled={busy}>
                  {busy ? "Signing in…" : "Sign in"}
                </SapButton>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
