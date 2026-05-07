/** Token 儲存與過期檢查服務（集中管理 sessionStorage 存取）。 */
export const TOKEN_KEYS = {
  accessToken: "smartpantry_access_token",
  refreshToken: "smartpantry_refresh_token",
} as const;

const ACCESS_TOKEN_REFRESH_BUFFER_SECONDS = 60;

/** 取得 access token。 */
export function getAccessToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEYS.accessToken);
}

/** 取得 refresh token。 */
export function getRefreshToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEYS.refreshToken);
}

/** 同步儲存 access/refresh token。 */
export function saveTokens(accessToken: string, refreshToken: string): void {
  sessionStorage.setItem(TOKEN_KEYS.accessToken, accessToken);
  sessionStorage.setItem(TOKEN_KEYS.refreshToken, refreshToken);
}

/** 清除所有 auth token。 */
export function clearTokens(): void {
  sessionStorage.removeItem(TOKEN_KEYS.accessToken);
  sessionStorage.removeItem(TOKEN_KEYS.refreshToken);
}

/** 判斷目前是否有可用 token。 */
export function hasTokens(): boolean {
  return Boolean(getAccessToken() && getRefreshToken());
}

/** 判斷 access token 是否即將過期。 */
export function isAccessTokenExpiringSoon(bufferSeconds: number = ACCESS_TOKEN_REFRESH_BUFFER_SECONDS): boolean {
  const token = getAccessToken();
  if (!token) {
    return true;
  }

  const payload = parseJwtPayload(token);
  if (!payload || typeof payload.exp !== "number") {
    return true;
  }

  const nowInSeconds = Math.floor(Date.now() / 1000);
  return payload.exp <= nowInSeconds + bufferSeconds;
}

function parseJwtPayload(token: string): Record<string, unknown> | null {
  const segments = token.split(".");
  if (segments.length < 2) {
    return null;
  }

  try {
    const base64 = segments[1].replace(/-/g, "+").replace(/_/g, "/");
    const normalized = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), "=");
    const jsonText = atob(normalized);
    return JSON.parse(jsonText) as Record<string, unknown>;
  } catch {
    return null;
  }
}
