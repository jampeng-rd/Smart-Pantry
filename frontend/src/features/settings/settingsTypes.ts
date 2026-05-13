import type { ThemeMode } from "../theme/themeTypes";

export type ExpirationReminderDays = "none" | "1" | "3";
export type ExpirationReminderSendWindow = "morning_08" | "evening_17";
export type ExpirationReminderDeliveryStatus = "pending" | "success" | "failed";

/** Settings 回應資料。 */
export interface SettingsData {
  theme: ThemeMode;
  timezone: string | null;
  language: string;
  expiration_email_reminder_days: ExpirationReminderDays;
}

/** 更新 Settings 請求。 */
export interface SettingsUpdatePayload {
  theme?: ThemeMode;
  timezone?: string | null;
  expiration_email_reminder_days?: ExpirationReminderDays;
  language?: string;
}

/** 單筆到期提醒寄送紀錄。 */
export interface ExpirationReminderDelivery {
  id: number;
  scheduled_date: string;
  send_window: ExpirationReminderSendWindow;
  reminder_days: ExpirationReminderDays;
  item_ids: number[];
  item_count: number;
  email_to: string;
  status: ExpirationReminderDeliveryStatus;
  sent_at: string | null;
  error_message: string | null;
  created_at: string;
}

/** 到期提醒寄送紀錄列表回應。 */
export interface ExpirationReminderDeliveryListResponse {
  items: ExpirationReminderDelivery[];
  page: number;
  page_size: number;
  total: number;
}
