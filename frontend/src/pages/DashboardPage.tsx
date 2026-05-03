import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getAccessToken, clearTokens } from "../lib/auth";
import { getMe } from "../api/auth";
import { SapDashboardShell } from "../components/SapDashboardShell";
import { WorkspaceProvider } from "../workspace/WorkspaceContext";

export default function DashboardPage() {
  const nav = useNavigate();
  const token = getAccessToken();
  const [user, setUser] = useState<string>("…");

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    (async () => {
      try {
        const me = await getMe(token);
        if (!cancelled) setUser(me.email);
      } catch {
        clearTokens();
        nav("/login", { replace: true });
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token, nav]);

  if (!token) return null;
  return (
    <WorkspaceProvider>
      <SapDashboardShell userLabel={user} />
    </WorkspaceProvider>
  );
}
