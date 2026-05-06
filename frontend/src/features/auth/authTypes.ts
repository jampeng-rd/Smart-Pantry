/** Auth 基礎狀態定義。 */
export interface AuthState {
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}
