/** 過期提醒狀態定義。 */
export interface ExpirationState {
  items: string[];
  page: number;
  pageSize: number;
  total: number;
  loading: boolean;
  error: string | null;
}
