import type { ApiResponse, AuthTokenData, MeData, RegisterPayload } from "../features/auth/authTypes";
import type { ExpirationSummary } from "../features/expiration/expirationTypes";
import type {
  PantryCreatePayload,
  PantryItem,
  PantryListData,
  PantryListParams,
  PantryUpdatePayload,
} from "../features/pantry/pantryTypes";
import type {
  ShoppingCreatePayload,
  ShoppingItem,
  ShoppingListData,
  ShoppingListParams,
  ShoppingUpdatePayload,
} from "../features/shopping/shoppingTypes";
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

/** Pantry API 封裝。 */
export const pantryApi = {
  list: (params: PantryListParams) => {
    const query = new URLSearchParams();

    if (params.category) {
      query.set("category", params.category);
    }
    if (params.status) {
      query.set("status", params.status);
    }
    if (params.sort) {
      query.set("sort", params.sort);
    }
    if (params.q) {
      query.set("q", params.q);
    }
    if (params.page) {
      query.set("page", String(params.page));
    }
    if (params.page_size) {
      query.set("page_size", String(params.page_size));
    }

    const search = query.toString();
    const path = search ? `/pantry/items?${search}` : "/pantry/items";
    return requestWithAuth<PantryListData>(path, { method: "GET" });
  },
  create: (payload: PantryCreatePayload) => requestWithAuth<PantryItem>("/pantry/items", { method: "POST", body: JSON.stringify(payload) }),
  update: (itemId: number, payload: PantryUpdatePayload) =>
    requestWithAuth<PantryItem>(`/pantry/items/${itemId}`, { method: "PATCH", body: JSON.stringify(payload) }),
  remove: (itemId: number) => requestWithAuth<{ deleted: boolean }>(`/pantry/items/${itemId}`, { method: "DELETE" }),
};

/** Expiration API 封裝。 */
export const expirationApi = {
  /** 取得到期提醒摘要。 */
  getSummary: () => requestWithAuth<ExpirationSummary>("/expiration/summary", { method: "GET" }),
};

/** Shopping API 封裝。 */
export const shoppingApi = {
  list: (params: ShoppingListParams) => {
    const query = new URLSearchParams();

    if (typeof params.is_purchased === "boolean") {
      query.set("is_purchased", String(params.is_purchased));
    }
    if (params.sort) {
      query.set("sort", params.sort);
    }
    if (params.q) {
      query.set("q", params.q);
    }
    if (params.page) {
      query.set("page", String(params.page));
    }
    if (params.page_size) {
      query.set("page_size", String(params.page_size));
    }

    const search = query.toString();
    const path = search ? `/shopping/items?${search}` : "/shopping/items";
    return requestWithAuth<ShoppingListData>(path, { method: "GET" });
  },
  create: (payload: ShoppingCreatePayload) => requestWithAuth<ShoppingItem>("/shopping/items", { method: "POST", body: JSON.stringify(payload) }),
  update: (itemId: number, payload: ShoppingUpdatePayload) =>
    requestWithAuth<ShoppingItem>(`/shopping/items/${itemId}`, { method: "PATCH", body: JSON.stringify(payload) }),
  remove: (itemId: number) => requestWithAuth<{ deleted: boolean }>(`/shopping/items/${itemId}`, { method: "DELETE" }),
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
