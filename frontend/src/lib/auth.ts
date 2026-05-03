const ACCESS = "erp_access";
const REFRESH = "erp_refresh";

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS);
}

export function setTokens(access: string, refresh: string): void {
  localStorage.setItem(ACCESS, access);
  localStorage.setItem(REFRESH, refresh);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS);
  localStorage.removeItem(REFRESH);
}
