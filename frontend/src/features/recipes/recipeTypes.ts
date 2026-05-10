import type { PantryItem } from "../pantry/pantryTypes";

export type RecipeRecommendationMode = "selected_items" | "auto_from_pantry";
export type RecipeJobStatus = "pending" | "running" | "success" | "failed" | "cancelled";

/** 食譜建議結果格式。 */
export interface RecipeRecommendationResult {
  recipe_name: string;
  ingredients_used: string[];
  missing_ingredients: string[];
  steps: string[];
  cooking_time_minutes: number;
  note: string;
}

/** 建立食譜推薦 job 請求。 */
export interface RecipeRecommendationJobCreatePayload {
  recommendation_mode: RecipeRecommendationMode;
  selected_pantry_item_ids?: number[];
  prioritize_expiring_soon: boolean;
  cooking_time_minutes: number;
  cooking_tools: string[];
  diet_preference: string | null;
  allergies: string[];
}

/** 建立食譜推薦 job 回應。 */
export interface RecipeRecommendationJobCreateData {
  job_id: number;
  status: RecipeJobStatus;
  created_at: string;
}

/** 食譜推薦 job 查詢回應。 */
export interface RecipeRecommendationJobStatusData {
  job_id: number;
  status: RecipeJobStatus;
  result: RecipeRecommendationResult | null;
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

/** Recipes 頁面狀態。 */
export interface RecipeState {
  pantryItems: PantryItem[];
  pantryLoading: boolean;
  pantryError: string | null;
  creatingJob: boolean;
  polling: boolean;
  currentJobId: number | null;
  jobStatus: RecipeJobStatus | null;
  jobError: string | null;
  result: RecipeRecommendationResult | null;
}
