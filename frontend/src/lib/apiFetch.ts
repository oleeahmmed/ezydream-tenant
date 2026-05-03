import { getAccessToken, clearTokens } from "./auth";

function formatDetailEntry(entry: unknown): string {
  if (typeof entry === "string") return entry;
  if (entry && typeof entry === "object" && "msg" in entry) {
    const m = (entry as { msg?: unknown }).msg;
    if (typeof m === "string") return m;
  }
  try {
    return JSON.stringify(entry);
  } catch {
    return String(entry);
  }
}

function detailMsg(data: unknown): string {
  if (data && typeof data === "object" && "detail" in data) {
    const d = (data as { detail: unknown }).detail;
    if (typeof d === "string") return d;
    if (Array.isArray(d)) return d.map(formatDetailEntry).join("; ");
    if (d && typeof d === "object") return formatDetailEntry(d);
  }
  return "Request failed";
}

export async function apiFetch<T>(path: string, init?: RequestInit & { json?: unknown }): Promise<T> {
  const token = getAccessToken();
  const headers: HeadersInit = { ...(init?.headers as Record<string, string>) };
  if (!(init?.body instanceof FormData) && init?.json !== undefined) {
    (headers as Record<string, string>)["Content-Type"] = "application/json";
  }
  if (token) (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  const body = init?.json !== undefined ? JSON.stringify(init.json) : init?.body;
  const res = await fetch(path, { ...init, headers, body: body ?? init?.body });
  const data: unknown = await res.json().catch(() => ({}));
  if (res.status === 401) {
    clearTokens();
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }
  if (!res.ok) throw new Error(detailMsg(data) || res.statusText);
  return data as T;
}
