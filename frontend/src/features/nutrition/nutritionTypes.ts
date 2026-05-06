/** 營養估算狀態定義。 */
export interface NutritionState {
  items: string[];
  page: number;
  pageSize: number;
  total: number;
  loading: boolean;
  error: string | null;
}
