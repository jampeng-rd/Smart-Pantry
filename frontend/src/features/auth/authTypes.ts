/** 使用者基本資料。 */
export interface UserProfile {
  id: number;
  email: string;
  display_name: string;
}

/** Auth 狀態定義。 */
export interface AuthState {
  user: UserProfile | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  initialized: boolean;
  error: string | null;
}

/** 登入請求參數。 */
export interface LoginPayload {
  email: string;
  password: string;
}

/** 註冊請求參數。 */
export interface RegisterPayload {
  email: string;
  password: string;
  display_name: string;
}

/** 忘記密碼請求參數。 */
export interface ForgotPasswordPayload {
  email: string;
}

/** 重設密碼請求參數。 */
export interface ResetPasswordPayload {
  token: string;
  new_password: string;
}

/** 後端統一回應結構。 */
export interface ApiResponse<T> {
  status: "success" | "error";
  data: T | null;
  message: string | null;
}

/** Token 回應資料。 */
export interface AuthTokenData {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

/** /auth/me 回應資料。 */
export interface MeData {
  user: UserProfile;
}
