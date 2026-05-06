/** 購物清單狀態定義。 */
export interface ShoppingState {
  items: string[];
  page: number;
  pageSize: number;
  total: number;
  loading: boolean;
  error: string | null;
}
