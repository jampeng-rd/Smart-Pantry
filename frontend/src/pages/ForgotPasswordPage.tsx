import { FormEvent, useState } from "react";
import { FiArrowLeft, FiMail, FiSend } from "react-icons/fi";

import { authApi } from "../services/apiClient";

interface ForgotPasswordPageProps {
  onBackToLogin: () => void;
  onShowResetPassword: () => void;
}

const SUCCESS_MESSAGE = "若此 Email 已註冊，我們已寄出重設密碼通知信。";

/**
 * 驗證 Email 格式（前端基本檢查，避免顯示成伺服器錯誤）。
 */
export function isValidEmailFormat(email: string): boolean {
  const normalized = email.trim();
  if (!normalized) {
    return false;
  }
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalized);
}

/** 忘記密碼頁面。 */
export function ForgotPasswordPage({ onBackToLogin, onShowResetPassword }: ForgotPasswordPageProps) {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setMessage(null);

    if (!email.trim()) {
      setError("請輸入 Email");
      return;
    }

    if (!isValidEmailFormat(email)) {
      setError("請輸入正確的 Email 格式");
      return;
    }

    setLoading(true);
    try {
      await authApi.forgotPassword({ email: email.trim() });
      setMessage(SUCCESS_MESSAGE);
    } catch {
      setError("目前無法處理此請求，請稍後再試。");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card auth-card">
      <header className="auth-brand">
        <h1>智慧食材保存與膳食管理系統</h1>
        <p>Smart Pantry & Nutritionist System</p>
      </header>

      <h2 className="auth-form-title">忘記密碼</h2>
      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        <label htmlFor="forgot-password-email">Email</label>
        <input
          id="forgot-password-email"
          name="email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="user@example.com"
        />

        {message && <p className="muted-text">{message}</p>}
        {error && <p className="error-text">{error}</p>}

        <button type="submit" className="btn primary" disabled={loading} aria-label="送出忘記密碼請求">
          <FiSend aria-hidden="true" />
          {loading ? "送出中..." : "送出重設請求"}
        </button>
      </form>

      <button type="button" className="btn ghost" onClick={onBackToLogin} aria-label="返回登入頁">
        <FiArrowLeft aria-hidden="true" />
        返回登入
      </button>
      <button type="button" className="btn ghost" onClick={onShowResetPassword} aria-label="前往重設密碼頁">
        已取得臨時密碼，前往重設密碼
      </button>
      <p className="muted-text">
        <FiMail aria-hidden="true" /> 請至信箱取得臨時密碼，再前往 重設密碼 完成操作。
      </p>
    </section>
  );
}
