export type LoginResponse = {
  otp_required?: boolean;
  detail?: string;
  access?: string;
  refresh?: string;
  token_type?: string;
  expires_in?: number;
};

export type MeResponse = {
  id: number;
  email: string;
  otp_enabled: boolean;
};

function detailMessage(data: unknown): string {
  if (data && typeof data === "object" && "detail" in data) {
    const d = (data as { detail: unknown }).detail;
    if (typeof d === "string") return d;
    if (Array.isArray(d)) return d.map((x) => String(x)).join("; ");
  }
  return "Request failed";
}

export async function postLogin(email: string, password: string): Promise<LoginResponse> {
  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: email.trim().toLowerCase(), password }),
  });
  const data: unknown = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(detailMessage(data));
  return data as LoginResponse;
}

export async function getMe(token: string): Promise<MeResponse> {
  const res = await fetch("/api/auth/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data: unknown = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(detailMessage(data));
  return data as MeResponse;
}
