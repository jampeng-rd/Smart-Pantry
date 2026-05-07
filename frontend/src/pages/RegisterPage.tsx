import { FormEvent, useState } from "react";
import { FiEye, FiEyeOff, FiLogIn, FiUserPlus } from "react-icons/fi";

import { useAppDispatch, useAppSelector } from "../app/hooks";
import { clearAuthError, register } from "../features/auth/authSlice";

interface RegisterPageProps {
  onRegistered: () => void;
  onShowLogin: () => void;
}

/** 註冊頁。 */
export function RegisterPage({ onRegistered, onShowLogin }: RegisterPageProps) {
  const dispatch = useAppDispatch();
  const auth = useAppSelector((state) => state.auth);

  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    dispatch(clearAuthError());
    setValidationError(null);

    if (!displayName.trim() || !email.trim() || !password.trim()) {
      setValidationError("請完整填寫欄位");
      return;
    }

    if (password.length < 8) {
      setValidationError("密碼至少需要 8 個字元");
      return;
    }

    if (password !== confirmPassword) {
      setValidationError("兩次輸入的密碼不一致");
      return;
    }

    const resultAction = await dispatch(
      register({
        display_name: displayName.trim(),
        email: email.trim(),
        password,
      }),
    );

    if (register.fulfilled.match(resultAction)) {
      onRegistered();
    }
  };

  return (
    <section className="card auth-card">
      <header className="auth-brand">
        <h1>智慧食材保存與膳食管理系統</h1>
        <p>Smart Pantry & Nutritionist System</p>
      </header>

      <h2 className="auth-form-title">建立帳號</h2>
      <form className="auth-form" onSubmit={handleSubmit}>
        <label htmlFor="register-display-name">顯示名稱</label>
        <input
          id="register-display-name"
          name="displayName"
          type="text"
          autoComplete="name"
          value={displayName}
          onChange={(event) => setDisplayName(event.target.value)}
          placeholder="王小明"
        />

        <label htmlFor="register-email">Email</label>
        <input
          id="register-email"
          name="email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="user@example.com"
        />

        <label htmlFor="register-password">密碼</label>
        <div className="password-field">
          <input
            id="register-password"
            name="password"
            type={showPassword ? "text" : "password"}
            autoComplete="new-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
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

        <label htmlFor="register-confirm-password">確認密碼</label>
        <div className="password-field">
          <input
            id="register-confirm-password"
            name="confirmPassword"
            type={showConfirmPassword ? "text" : "password"}
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            placeholder="再次輸入密碼"
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

        {(validationError || auth.error) && <p className="error-text">{validationError ?? auth.error}</p>}

        <button type="submit" className="btn primary" disabled={auth.loading} aria-label="送出註冊">
          <FiUserPlus aria-hidden="true" />
          {auth.loading ? "註冊中..." : "註冊並登入"}
        </button>
      </form>

      <button type="button" className="btn ghost" onClick={onShowLogin} aria-label="返回登入頁">
        <FiLogIn aria-hidden="true" />
        已有帳號？返回登入
      </button>
    </section>
  );
}
