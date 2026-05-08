export type PantryItemStatus = "normal" | "expiring_soon" | "expired";

/** 食材項目資料。 */
export interface PantryItem {
  id: number;
  name: string;
  category: string;
  quantity: number;
  unit: string;
  expiration_date: string | null;
  storage_location: string | null;
  note: string | null;
  created_at: string;
  updated_at: string;
  /**
   * 後端目前已提供 status；若未來欄位缺失，前端可 fallback 顯示「未分類」。
   * 期望最終由後端統一提供狀態定義，避免前端時間判斷不一致。
   */
  status?: PantryItemStatus;
}

/** 食材列表查詢條件。 */
export interface PantryFilters {
  q: string;
  category: string;
  status: PantryItemStatus | "all";
}

export type PantrySort = "expiration_date" | "created_at";

/** 食材列表狀態。 */
export interface PantryState {
  items: PantryItem[];
  page: number;
  pageSize: number;
  total: number;
  loading: boolean;
  error: string | null;
  filters: PantryFilters;
  sort: PantrySort;
}

/** 食材列表 API 回應資料。 */
export interface PantryListData {
  items: PantryItem[];
  page: number;
  page_size: number;
  total: number;
}

/** 新增食材請求。 */
export interface PantryCreatePayload {
  name: string;
  category: string;
  quantity: number;
  unit: string;
  expiration_date: string | null;
  storage_location: string | null;
  note: string | null;
}

/** 更新食材請求。 */
export interface PantryUpdatePayload {
  name?: string;
  category?: string;
  quantity?: number;
  unit?: string;
  expiration_date?: string | null;
  storage_location?: string | null;
  note?: string | null;
}

/** 食材列表查詢參數。 */
export interface PantryListParams {
  category?: string;
  status?: PantryItemStatus;
  sort?: PantrySort;
  q?: string;
  page?: number;
  page_size?: number;
}
