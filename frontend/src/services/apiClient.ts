import type { ApiResponse, AuthTokenData, MeData, RegisterPayload } from "../features/auth/authTypes";
import { clearTokens, getAccessToken, getRefreshToken, isAccessTokenExpiringSoon, saveTokens } from "./tokenService";

/** API 基底網址。 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

interface LoginPayload {
  email: string;
  password: string;
}

interface RefreshPayload {
  refresh_token: string;
}

interface LogoutPayload {
  refresh_token: string;
}

/** Auth API 封裝。 */
export const authApi = {
  register: (payload: RegisterPayload) => post<unknown>("/auth/register", payload),
  login: (payload: LoginPayload) => post<AuthTokenData>("/auth/login", payload),
  refresh: (payload: RefreshPayload) => post<AuthTokenData>("/auth/refresh", payload),
  logout: (payload: LogoutPayload) => post<unknown>("/auth/logout", payload),
  me: () => requestWithAuth<MeData>("/auth/me", { method: "GET" }),
};

/** 送出需授權的請求，含 pre-refresh 與 401 單次重試。 */
export async function requestWithAuth<T>(path: string, init: RequestInit, retried = false): Promise<T> {
  if (isAccessTokenExpiringSoon()) {
    await refreshTokensOrThrow();
  }

  const accessToken = getAccessToken();
  if (!accessToken) {
    throw new Error("尚未登入");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
      ...(init.headers ?? {}),
    },
  });

  if (response.status === 401 && !retried) {
    await refreshTokensOrThrow();
    return requestWithAuth<T>(path, init, true);
  }

  const body = (await response.json()) as ApiResponse<T>;
  if (!response.ok || body.status !== "success" || body.data === null) {
    throw new Error(body.message ?? "API 請求失敗");
  }

  return body.data;
}

async function post<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const body = (await response.json()) as ApiResponse<T>;
  if (!response.ok || body.status !== "success" || body.data === null) {
    throw new Error(body.message ?? "API 請求失敗");
  }

  return body.data;
}

/** 嘗試刷新 token，失敗時清除本地登入狀態。 */
export async function refreshTokensOrThrow(): Promise<void> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    clearTokens();
    throw new Error("缺少 refresh token");
  }

  try {
    const tokenData = await authApi.refresh({ refresh_token: refreshToken });
    saveTokens(tokenData.access_token, tokenData.refresh_token);
  } catch (error) {
    clearTokens();
    throw error;
  }
}
