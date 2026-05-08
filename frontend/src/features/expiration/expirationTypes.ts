export type ExpirationStatusFilter = "all" | "expired" | "expiring_soon" | "normal";

/** 到期提醒清單項目。 */
export interface ExpirationItem {
  id: number;
  name: string;
  category: string;
  quantity: number;
  unit: string;
  expiration_date: string | null;
  status: "expired" | "expiring_soon" | "normal";
  storage_location: string | null;
  note: string | null;
}

/** 到期提醒摘要回應。 */
export interface ExpirationSummary {
  expired_count: number;
  expiring_soon_count: number;
  expired_items: ExpirationItem[];
  expiring_soon_items: ExpirationItem[];
}

/** 到期提醒頁面摘要卡片統計。 */
export interface ExpirationSummaryStats {
  expired: number;
  expiringSoon: number;
  normal: number;
  total: number;
}

/** 到期提醒 Redux 狀態。 */
export interface ExpirationState {
  summary: ExpirationSummary | null;
  stats: ExpirationSummaryStats;
  items: ExpirationItem[];
  loading: boolean;
  error: string | null;
  selectedStatusFilter: ExpirationStatusFilter;
}
