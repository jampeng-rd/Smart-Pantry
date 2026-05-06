/** 食譜建議狀態定義。 */
export interface RecipeState {
  items: string[];
  page: number;
  pageSize: number;
  total: number;
  loading: boolean;
  error: string | null;
}
