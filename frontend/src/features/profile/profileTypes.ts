/** Profile 回應資料。 */
export interface ProfileData {
  display_name: string;
  email: string;
  avatar_url: string | null;
  avatar_fallback: string;
}

/** 更新 Profile 請求。 */
export interface ProfileUpdatePayload {
  display_name: string;
}

/** 修改密碼請求。 */
export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
}
