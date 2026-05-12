import type { ThemeMode } from "../theme/themeTypes";

export type ExpirationReminderDays = "none" | "1" | "3";

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
