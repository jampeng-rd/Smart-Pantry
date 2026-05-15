import { FormEvent, useState } from "react";
import { FiArrowLeft, FiCheckCircle, FiEye, FiEyeOff, FiKey } from "react-icons/fi";

import { authApi } from "../services/apiClient";

interface ResetPasswordPageProps {
  tokenFromUrl: string;
  onBackToLogin: () => void;
}

/** 重設密碼頁面。 */
export function ResetPasswordPage({ tokenFromUrl, onBackToLogin }: ResetPasswordPageProps) {
  const [token, setToken] = useState(tokenFromUrl);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setMessage(null);

    if (!token.trim() || !newPassword.trim() || !confirmPassword.trim()) {
      setError("請完整填寫欄位");
      return;
    }
    if (newPassword.length < 8) {
      setError("新密碼至少需要 8 個字元");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("兩次輸入的密碼不一致");
      return;
    }

    setLoading(true);
    try {
      await authApi.resetPassword({ token: token.trim(), new_password: newPassword });
      setMessage("密碼重設成功，請返回登入頁重新登入。");
    } catch (caughtError) {
      const safeMessage = caughtError instanceof Error ? caughtError.message : "目前無法處理此請求，請稍後再試。";
      setError(safeMessage);
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

      <h2 className="auth-form-title">重設密碼</h2>
      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        <label htmlFor="reset-password-token">重設 token</label>
        <input
          id="reset-password-token"
          name="token"
          type="text"
          value={token}
          onChange={(event) => setToken(event.target.value)}
          placeholder="請貼上信件中的重設 token"
        />

        <label htmlFor="reset-password-new-password">新密碼</label>
        <div className="password-field">
          <input
            id="reset-password-new-password"
            name="newPassword"
            type={showPassword ? "text" : "password"}
            autoComplete="new-password"
            value={newPassword}
            onChange={(event) => setNewPassword(event.target.value)}
            placeholder="至少 8 字元"
          />
          <button
            type="button"
            className="btn ghost password-toggle"
            onClick={() => setShowPassword((value) => !value)}
            aria-label={showPassword ? "隱藏密碼" : "顯示密碼"}
          >
            {showPassword ? <FiEyeOff aria-hidden="true" /> : <FiEye aria-hidden="true" />}
          </button>
        </div>

        <label htmlFor="reset-password-confirm-password">確認新密碼</label>
        <div className="password-field">
          <input
            id="reset-password-confirm-password"
            name="confirmPassword"
            type={showConfirmPassword ? "text" : "password"}
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            placeholder="再次輸入新密碼"
          />
          <button
            type="button"
            className="btn ghost password-toggle"
            onClick={() => setShowConfirmPassword((value) => !value)}
            aria-label={showConfirmPassword ? "隱藏密碼" : "顯示密碼"}
          >
            {showConfirmPassword ? <FiEyeOff aria-hidden="true" /> : <FiEye aria-hidden="true" />}
          </button>
        </div>

        {message && <p className="muted-text">{message}</p>}
        {error && <p className="error-text">{error}</p>}

        <button type="submit" className="btn primary" disabled={loading} aria-label="送出重設密碼">
          <FiKey aria-hidden="true" />
          {loading ? "重設中..." : "重設密碼"}
        </button>
      </form>

      <button type="button" className="btn ghost" onClick={onBackToLogin} aria-label="返回登入頁">
        <FiArrowLeft aria-hidden="true" />
        返回登入
      </button>
      <p className="muted-text">
        <FiCheckCircle aria-hidden="true" /> 重設成功後，系統會要求你重新登入。
      </p>
    </section>
  );
}
