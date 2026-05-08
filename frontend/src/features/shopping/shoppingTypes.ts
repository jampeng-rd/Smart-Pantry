export type ShoppingSort = "created_at" | "name" | "purchased_at";
export type ShoppingPurchasedFilter = "all" | "unpurchased" | "purchased";

/** 單一購物清單項目。 */
export interface ShoppingItem {
  id: number;
  source_pantry_item_id: number | null;
  name: string;
  quantity: number;
  unit: string;
  is_purchased: boolean;
  purchased_at: string | null;
  created_at: string;
  updated_at: string;
}

/** 購物清單篩選條件。 */
export interface ShoppingFilters {
  q: string;
  isPurchased: ShoppingPurchasedFilter;
}

/** 購物清單列表狀態。 */
export interface ShoppingState {
  items: ShoppingItem[];
  page: number;
  pageSize: number;
  total: number;
  loading: boolean;
  error: string | null;
  filters: ShoppingFilters;
  sort: ShoppingSort;
}

/** 購物清單列表 API 回應資料。 */
export interface ShoppingListData {
  items: ShoppingItem[];
  page: number;
  page_size: number;
  total: number;
}

/** 新增購物項目請求。 */
export interface ShoppingCreatePayload {
  source_pantry_item_id?: number | null;
  name: string;
  quantity: number;
  unit: string;
}

/** 更新購物項目請求。 */
export interface ShoppingUpdatePayload {
  name?: string;
  quantity?: number;
  unit?: string;
  is_purchased?: boolean;
}

/** 購物清單查詢參數。 */
export interface ShoppingListParams {
  page?: number;
  page_size?: number;
  is_purchased?: boolean;
  q?: string;
  sort?: "created_at" | "purchased_at";
}
