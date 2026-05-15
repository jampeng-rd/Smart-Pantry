import type {
  ApiResponse,
  AuthTokenData,
  ForgotPasswordPayload,
  MeData,
  RegisterPayload,
  ResetPasswordPayload,
} from "../features/auth/authTypes";
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
import type {
  IngredientPhotoJobCreateData,
  IngredientPhotoJobStatusData,
} from "../features/ingredients/ingredientTypes";
import type {
  RecipeRecommendationJobCreateData,
  RecipeRecommendationJobCreatePayload,
  RecipeRecommendationJobStatusData,
} from "../features/recipes/recipeTypes";
import type { AdminMemberListData } from "../features/admin/adminTypes";
import type { ChangePasswordPayload, ProfileData, ProfileUpdatePayload } from "../features/profile/profileTypes";
import type {
  ExpirationReminderDeliveryListResponse,
  SettingsData,
  SettingsUpdatePayload,
} from "../features/settings/settingsTypes";
import { clearTokens, getAccessToken, getRefreshToken, isAccessTokenExpiringSoon, saveTokens } from "./tokenService";

/** API 基底網址。 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const NETWORK_ERROR_MESSAGE = "網路異常，請稍後再試。";
const SYSTEM_FAILURE_MESSAGE = "目前系統偵測異常，系統維修中。";

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
  forgotPassword: (payload: ForgotPasswordPayload) => post<unknown>("/auth/forgot-password", payload),
  resetPassword: (payload: ResetPasswordPayload) => post<unknown>("/auth/reset-password", payload),
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

/** Recipes AI Job API 封裝。 */
export const recipesApi = {
  /** 建立食譜推薦任務。 */
  createRecommendationJob: (payload: RecipeRecommendationJobCreatePayload) =>
    requestWithAuth<RecipeRecommendationJobCreateData>("/recipes/recommendation-jobs", { method: "POST", body: JSON.stringify(payload) }),
  /** 查詢食譜推薦任務狀態。 */
  getRecommendationJobStatus: (jobId: number) =>
    requestWithAuth<RecipeRecommendationJobStatusData>(`/recipes/recommendation-jobs/${jobId}`, { method: "GET" }),
};

/** Ingredients Photo Job API 封裝。 */
export const ingredientsApi = {
  /** 建立食材照片辨識任務。 */
  createIngredientPhotoJob: (file: File) => {
    const formData = new FormData();
    formData.append("image", file);
    return requestWithAuthFormData<IngredientPhotoJobCreateData>("/ingredients/photo/jobs", formData);
  },
  /** 查詢食材照片辨識任務狀態。 */
  getIngredientPhotoJob: (jobId: number) => requestWithAuth<IngredientPhotoJobStatusData>(`/ingredients/photo/jobs/${jobId}`, { method: "GET" }),
};

/** Profile API 封裝。 */
export const profileApi = {
  get: () => requestWithAuth<ProfileData>("/profile", { method: "GET" }),
  update: (payload: ProfileUpdatePayload) => requestWithAuth<ProfileData>("/profile", { method: "PATCH", body: JSON.stringify(payload) }),
  changePassword: (payload: ChangePasswordPayload) =>
    requestWithAuth<{ password_changed: boolean }>("/profile/change-password", { method: "POST", body: JSON.stringify(payload) }),
};

/** Settings API 封裝。 */
export const settingsApi = {
  get: () => requestWithAuth<SettingsData>("/settings", { method: "GET" }),
  update: (payload: SettingsUpdatePayload) => requestWithAuth<SettingsData>("/settings", { method: "PATCH", body: JSON.stringify(payload) }),
  /** 查詢到期 Email 提醒寄送紀錄（分頁）。 */
  getExpirationReminderDeliveries: (params: { page: number; pageSize: number }) => {
    const query = new URLSearchParams({
      page: String(params.page),
      page_size: String(params.pageSize),
    });
    return requestWithAuth<ExpirationReminderDeliveryListResponse>(`/settings/expiration-reminder-deliveries?${query.toString()}`, { method: "GET" });
  },
};

/** Admin 會員管理 API 封裝。 */
export const adminApi = {
  /** 查詢會員列表（僅 admin）。 */
  listMembers: (params: { page: number; pageSize: number; q?: string }) => {
    const query = new URLSearchParams({
      page: String(params.page),
      page_size: String(params.pageSize),
    });
    const keyword = params.q?.trim();
    if (keyword) {
      query.set("q", keyword);
    }
    return requestWithAuth<AdminMemberListData>(`/admin/members?${query.toString()}`, { method: "GET" });
  },
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

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
        ...(init.headers ?? {}),
      },
    });
  } catch (error) {
    throw toNetworkSafeError(error);
  }

  if (response.status === 401 && !retried) {
    await refreshTokensOrThrow();
    return requestWithAuth<T>(path, init, true);
  }

  const body = (await response.json()) as ApiResponse<T> & { detail?: string };
  if (!response.ok || body.status !== "success" || body.data === null) {
    throw new Error(toSafeApiErrorMessage(response.status, body.message ?? body.detail ?? ""));
  }

  return body.data;
}

async function requestWithAuthFormData<T>(path: string, formData: FormData, retried = false): Promise<T> {
  if (isAccessTokenExpiringSoon()) {
    await refreshTokensOrThrow();
  }

  const accessToken = getAccessToken();
  if (!accessToken) {
    throw new Error("尚未登入");
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      body: formData,
    });
  } catch (error) {
    throw toNetworkSafeError(error);
  }

  if (response.status === 401 && !retried) {
    await refreshTokensOrThrow();
    return requestWithAuthFormData<T>(path, formData, true);
  }

  const body = (await response.json()) as ApiResponse<T> & { detail?: string };
  if (!response.ok || body.status !== "success" || body.data === null) {
    throw new Error(toSafeApiErrorMessage(response.status, body.message ?? body.detail ?? ""));
  }

  return body.data;
}

async function post<T>(path: string, payload: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch (error) {
    throw toNetworkSafeError(error);
  }

  const body = (await response.json()) as ApiResponse<T>;
  if (!response.ok || body.status !== "success" || body.data === null) {
    throw new Error(toSafeApiErrorMessage(response.status, body.message ?? ""));
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

/** 將前端/瀏覽器網路錯誤轉為固定對外訊息。 */
function toNetworkSafeError(error: unknown): Error {
  if (!(error instanceof Error)) {
    return new Error(NETWORK_ERROR_MESSAGE);
  }
  const text = error.message.toLowerCase();
  if (
    text.includes("networkerror")
    || text.includes("failed to fetch")
    || text.includes("load failed")
    || text.includes("network request failed")
    || text.includes("fetch")
    || text.includes("axios")
  ) {
    return new Error(NETWORK_ERROR_MESSAGE);
  }
  return error;
}

/** 將 API 錯誤轉為安全、可顯示給使用者的訊息。 */
function toSafeApiErrorMessage(status: number, fallbackMessage: string): string {
  if (status >= 500) {
    return SYSTEM_FAILURE_MESSAGE;
  }
  if (status === 401) {
    return "登入狀態已失效，請重新登入。";
  }
  if (status === 403) {
    return "目前無法執行此操作，請稍後再試。";
  }
  if (status === 404) {
    return "資料不存在或已被移除。";
  }
  if (status === 422) {
    return "送出資料格式不正確，請檢查後再試。";
  }
  if (status === 400) {
    return fallbackMessage || "目前無法處理此請求，請稍後再試。";
  }
  if (status >= 400) {
    return "目前無法處理此請求，請稍後再試。";
  }
  return fallbackMessage || "API 請求失敗";
}
