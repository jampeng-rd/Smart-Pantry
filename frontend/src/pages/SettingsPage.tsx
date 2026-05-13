import { FormEvent, useEffect, useState } from "react";
import { FiAlertCircle, FiGlobe, FiMoon, FiRefreshCw, FiSave, FiSun } from "react-icons/fi";

import { useAppDispatch, useAppSelector } from "../app/hooks";
import type { ExpirationReminderDays, ExpirationReminderDelivery, SettingsData } from "../features/settings/settingsTypes";
import { setTheme } from "../features/theme/themeSlice";
import { settingsApi } from "../services/apiClient";
import { formatLocalDateTime } from "../utils/dateTime";

const REMINDER_OPTIONS: Array<{ value: ExpirationReminderDays; label: string }> = [
  { value: "none", label: "不提醒" },
  { value: "1", label: "前 1 天（預設）" },
  { value: "3", label: "前 3 天" },
];
const DELIVERY_PAGE_SIZE = 10;

/** 轉換寄送時段文字。 */
function mapSendWindowLabel(sendWindow: ExpirationReminderDelivery["send_window"]): string {
  if (sendWindow === "morning_08") {
    return "上午 8:00";
  }
  return "下午 5:00";
}

/** 轉換提醒天數文字。 */
function mapReminderDaysLabel(reminderDays: ExpirationReminderDays): string {
  if (reminderDays === "1") {
    return "前 1 天";
  }
  if (reminderDays === "3") {
    return "前 3 天";
  }
  return "不提醒";
}

/** 轉換寄送狀態文字。 */
function mapDeliveryStatusLabel(status: ExpirationReminderDelivery["status"]): string {
  if (status === "success") {
    return "成功";
  }
  if (status === "failed") {
    return "失敗";
  }
  return "處理中";
}

/** Settings 設定頁面。 */
export function SettingsPage() {
  const dispatch = useAppDispatch();
  const currentTheme = useAppSelector((state) => state.theme.mode);

  const [settings, setSettings] = useState<SettingsData | null>(null);
  const [theme, setThemeValue] = useState<"light-soft" | "dark-soft">(currentTheme === "light-soft" ? "light-soft" : "dark-soft");
  const [timezone, setTimezone] = useState("Asia/Taipei");
  const [reminderDays, setReminderDays] = useState<ExpirationReminderDays>("1");
  const [loading, setLoading] = useState(true);
  const [deliveryLoading, setDeliveryLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [deliveryError, setDeliveryError] = useState<string | null>(null);
  const [deliveries, setDeliveries] = useState<ExpirationReminderDelivery[]>([]);
  const [deliveryPage, setDeliveryPage] = useState(1);
  const [deliveryTotal, setDeliveryTotal] = useState(0);

  /** 載入寄送紀錄分頁資料。 */
  const loadDeliveries = async (page: number) => {
    setDeliveryLoading(true);
    setDeliveryError(null);
    try {
      const response = await settingsApi.getExpirationReminderDeliveries({ page, pageSize: DELIVERY_PAGE_SIZE });
      setDeliveries(response.items);
      setDeliveryPage(response.page);
      setDeliveryTotal(response.total);
    } catch (apiError) {
      setDeliveryError(apiError instanceof Error ? apiError.message : "載入寄送紀錄失敗");
    } finally {
      setDeliveryLoading(false);
    }
  };

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
        setThemeValue("dark-soft");
        dispatch(setTheme("dark-soft"));
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [dispatch]);

  useEffect(() => {
    void loadDeliveries(deliveryPage);
  }, [deliveryPage]);

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
      {/* <h2 className="workspace-title">
        <FiSettings aria-hidden="true" /> 系統設定
      </h2> */}

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
        <p className="muted-text">MVP 目前使用 fake email client，寄送紀錄僅供功能驗證。</p>

        <div className="settings-delivery-block">
          <div className="settings-delivery-head">
            <h4>最近寄送紀錄</h4>
            <button
              type="button"
              className="btn ghost"
              aria-label="重試載入寄送紀錄"
              onClick={() => {
                void loadDeliveries(deliveryPage);
              }}
              disabled={deliveryLoading}
            >
              <FiRefreshCw aria-hidden="true" /> 重新整理
            </button>
          </div>

          {deliveryLoading ? <p className="muted-text">載入寄送紀錄中...</p> : null}
          {deliveryError ? (
            <div className="settings-delivery-error">
              <p>
                <FiAlertCircle aria-hidden="true" /> {deliveryError}
              </p>
              <button
                type="button"
                className="btn ghost"
                aria-label="重試載入最近寄送紀錄"
                onClick={() => {
                  void loadDeliveries(deliveryPage);
                }}
              >
                重試
              </button>
            </div>
          ) : null}
          {!deliveryLoading && !deliveryError && deliveries.length === 0 ? <p className="muted-text">尚無寄送紀錄</p> : null}
          {!deliveryLoading && !deliveryError && deliveries.length > 0 ? (
            <>
              <div className="settings-delivery-table-wrap">
                <table className="settings-delivery-table">
                  <thead>
                    <tr>
                      <th>排程日期</th>
                      <th>寄送時段</th>
                      <th>提醒天數</th>
                      <th>食材數量</th>
                      <th>收件 Email</th>
                      <th>狀態</th>
                      <th>寄送時間</th>
                      <th>錯誤訊息</th>
                    </tr>
                  </thead>
                  <tbody>
                    {deliveries.map((item) => (
                      <tr key={item.id}>
                        <td>{item.scheduled_date}</td>
                        <td>{mapSendWindowLabel(item.send_window)}</td>
                        <td>{mapReminderDaysLabel(item.reminder_days)}</td>
                        <td>{item.item_count}</td>
                        <td>{item.email_to}</td>
                        <td>{mapDeliveryStatusLabel(item.status)}</td>
                        <td>{formatLocalDateTime(item.sent_at)}</td>
                        <td>{item.status === "failed" ? item.error_message ?? "-" : "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="settings-delivery-cards">
                {deliveries.map((item) => (
                  <article key={item.id} className="settings-delivery-card">
                    <p>
                      <span>排程日期</span>
                      <strong>{item.scheduled_date}</strong>
                    </p>
                    <p>
                      <span>寄送時段</span>
                      <strong>{mapSendWindowLabel(item.send_window)}</strong>
                    </p>
                    <p>
                      <span>提醒天數</span>
                      <strong>{mapReminderDaysLabel(item.reminder_days)}</strong>
                    </p>
                    <p>
                      <span>食材數量</span>
                      <strong>{item.item_count}</strong>
                    </p>
                    <p>
                      <span>收件 Email</span>
                      <strong>{item.email_to}</strong>
                    </p>
                    <p>
                      <span>狀態</span>
                      <strong>{mapDeliveryStatusLabel(item.status)}</strong>
                    </p>
                    <p>
                      <span>寄送時間</span>
                      <strong>{formatLocalDateTime(item.sent_at)}</strong>
                    </p>
                    {item.status === "failed" ? (
                      <p>
                        <span>錯誤訊息</span>
                        <strong>{item.error_message ?? "-"}</strong>
                      </p>
                    ) : null}
                  </article>
                ))}
              </div>

              <div className="settings-delivery-pagination">
                <p className="muted-text">
                  第 {deliveryPage} 頁，共 {Math.max(1, Math.ceil(deliveryTotal / DELIVERY_PAGE_SIZE))} 頁
                </p>
                <div className="settings-delivery-pagination-actions">
                  <button
                    type="button"
                    className="icon-btn"
                    aria-label="寄送紀錄上一頁"
                    onClick={() => setDeliveryPage((prev) => Math.max(1, prev - 1))}
                    disabled={deliveryPage <= 1 || deliveryLoading}
                  >
                    上一頁
                  </button>
                  <button
                    type="button"
                    className="icon-btn"
                    aria-label="寄送紀錄下一頁"
                    onClick={() => setDeliveryPage((prev) => prev + 1)}
                    disabled={deliveryPage >= Math.max(1, Math.ceil(deliveryTotal / DELIVERY_PAGE_SIZE)) || deliveryLoading}
                  >
                    下一頁
                  </button>
                </div>
              </div>
            </>
          ) : null}
        </div>

        <h3 className="workspace-subtitle">3. 時區</h3>
        <label htmlFor="settings-timezone">時區</label>
        <select id="settings-timezone" value={timezone} onChange={(event) => setTimezone(event.target.value)}>
          <option value="Asia/Taipei">Asia/Taipei</option>
        </select>

        <h3 className="workspace-subtitle">4. 語言</h3>
        <label htmlFor="settings-language">語言</label>
        <input id="settings-language" value="繁體中文" disabled aria-disabled="true" />

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
