import { FormEvent, useEffect, useState } from "react";
import { FiGlobe, FiMoon, FiSave, FiSettings, FiSun } from "react-icons/fi";

import { useAppDispatch, useAppSelector } from "../app/hooks";
import type { ExpirationReminderDays, SettingsData } from "../features/settings/settingsTypes";
import { setTheme } from "../features/theme/themeSlice";
import { settingsApi } from "../services/apiClient";

const REMINDER_OPTIONS: Array<{ value: ExpirationReminderDays; label: string }> = [
  { value: "none", label: "不提醒" },
  { value: "1", label: "前 1 天（預設）" },
  { value: "3", label: "前 3 天" },
];

/** Settings 設定頁面。 */
export function SettingsPage() {
  const dispatch = useAppDispatch();
  const currentTheme = useAppSelector((state) => state.theme.mode);

  const [settings, setSettings] = useState<SettingsData | null>(null);
  const [theme, setThemeValue] = useState(currentTheme);
  const [timezone, setTimezone] = useState("Asia/Taipei");
  const [reminderDays, setReminderDays] = useState<ExpirationReminderDays>("1");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await settingsApi.get();
        setSettings(data);
        setThemeValue(data.theme);
        setTimezone(data.timezone ?? Intl.DateTimeFormat().resolvedOptions().timeZone ?? "Asia/Taipei");
        setReminderDays(data.expiration_email_reminder_days);
        dispatch(setTheme(data.theme));
      } catch (apiError) {
        setError(apiError instanceof Error ? apiError.message : "載入設定失敗");
      } finally {
        setLoading(false);
      }
    };

    void run();
  }, [dispatch]);

  const handleSave = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSaving(true);
    setMessage(null);
    setError(null);
    try {
      const updated = await settingsApi.update({
        theme,
        timezone,
        expiration_email_reminder_days: reminderDays,
      });
      setSettings(updated);
      setThemeValue(updated.theme);
      setTimezone(updated.timezone ?? "Asia/Taipei");
      setReminderDays(updated.expiration_email_reminder_days);
      dispatch(setTheme(updated.theme));
      setMessage("設定已儲存");
    } catch (apiError) {
      setError(apiError instanceof Error ? apiError.message : "儲存設定失敗");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <section className="card workspace-card">載入設定中...</section>;
  }

  return (
    <section className="card workspace-card settings-page">
      <h2 className="workspace-title">
        <FiSettings aria-hidden="true" /> 系統設定
      </h2>

      <form onSubmit={handleSave} className="settings-form" noValidate>
        <h3 className="workspace-subtitle">1. 外觀設定</h3>
        <div className="theme-toggle-group" role="radiogroup" aria-label="主題切換">
          <button
            type="button"
            className={`btn ${theme === "light-soft" ? "primary" : "ghost"}`}
            aria-label="切換柔和亮色主題"
            onClick={() => {
              setThemeValue("light-soft");
              dispatch(setTheme("light-soft"));
            }}
          >
            <FiSun aria-hidden="true" /> 柔和亮色
          </button>
          <button
            type="button"
            className={`btn ${theme === "dark-soft" ? "primary" : "ghost"}`}
            aria-label="切換柔和暗色主題"
            onClick={() => {
              setThemeValue("dark-soft");
              dispatch(setTheme("dark-soft"));
            }}
          >
            <FiMoon aria-hidden="true" /> 柔和暗色
          </button>
        </div>

        <h3 className="workspace-subtitle">2. 到期 Email 提醒</h3>
        <label htmlFor="settings-reminder">提醒時間</label>
        <select
          id="settings-reminder"
          value={reminderDays}
          onChange={(event) => setReminderDays(event.target.value as ExpirationReminderDays)}
        >
          {REMINDER_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <p className="muted-text">本階段僅儲存提醒偏好，不會寄送 Email。</p>

        <h3 className="workspace-subtitle">3. 時區</h3>
        <label htmlFor="settings-timezone">時區</label>
        <select id="settings-timezone" value={timezone} onChange={(event) => setTimezone(event.target.value)}>
          <option value="Asia/Taipei">Asia/Taipei</option>
        </select>

        <h3 className="workspace-subtitle">4. 語言</h3>
        <label htmlFor="settings-language">語言</label>
        <input id="settings-language" value={settings?.language ?? "zh-TW"} disabled aria-disabled="true" />

        <h3 className="workspace-subtitle">5. 登出所有裝置</h3>
        <button type="button" className="btn ghost" disabled aria-label="登出所有裝置（未來功能）">
          未來功能
        </button>

        <h3 className="workspace-subtitle">6. 最近登入時間</h3>
        <div className="future-block" aria-disabled="true">
          <FiGlobe aria-hidden="true" /> 未來功能
        </div>

        <button type="submit" className="btn" disabled={saving} aria-label="儲存設定">
          <FiSave aria-hidden="true" /> {saving ? "儲存中..." : "儲存設定"}
        </button>
      </form>

      {message ? <p className="success-text">{message}</p> : null}
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}
