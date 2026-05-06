/** 食材列表狀態定義。 */
export interface PantryState {
  items: string[];
  page: number;
  pageSize: number;
  total: number;
  loading: boolean;
  error: string | null;
}
