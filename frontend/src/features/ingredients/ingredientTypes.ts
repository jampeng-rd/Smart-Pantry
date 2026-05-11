export type IngredientPhotoJobStatus = "pending" | "running" | "success" | "failed" | "cancelled";

/** AI 候選食材資料。 */
export interface IngredientCandidateItem {
  name: string;
  category: string;
  quantity: number;
  unit: string;
  expiration_date: string | null;
  storage_location: string;
  note: string;
}

/** 食材照片辨識結果。 */
export interface IngredientPhotoRecognitionResult {
  candidate_items: IngredientCandidateItem[];
  note: string;
}

/** 建立食材辨識 job 回應。 */
export interface IngredientPhotoJobCreateData {
  job_id: number;
  status: IngredientPhotoJobStatus;
  created_at: string;
}

/** 查詢食材辨識 job 回應。 */
export interface IngredientPhotoJobStatusData {
  job_id: number;
  status: IngredientPhotoJobStatus;
  result: IngredientPhotoRecognitionResult | null;
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

/** 單筆候選食材寫入 pantry 的結果。 */
export interface IngredientConfirmFailureItem {
  index: number;
  name: string;
  reason: string;
}

/** 確認加入庫存後的摘要。 */
export interface IngredientConfirmSummary {
  successCount: number;
  failureItems: IngredientConfirmFailureItem[];
}

/** 食材辨識頁 Redux 狀態。 */
export interface IngredientState {
  uploading: boolean;
  polling: boolean;
  currentJobId: number | null;
  jobStatus: IngredientPhotoJobStatus | null;
  jobError: string | null;
  candidates: IngredientCandidateItem[];
  resultNote: string | null;
  confirmLoading: boolean;
  confirmSummary: IngredientConfirmSummary | null;
}
