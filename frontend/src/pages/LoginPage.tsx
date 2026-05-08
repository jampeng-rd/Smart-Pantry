import { FormEvent, useState } from "react";
import { FiEye, FiEyeOff, FiLogIn, FiUserPlus } from "react-icons/fi";

import { useAppDispatch, useAppSelector } from "../app/hooks";
import { clearAuthError, login } from "../features/auth/authSlice";

interface LoginPageProps {
  onLoggedIn: () => void;
  onShowRegister: () => void;
}

/** 登入頁。 */
export function LoginPage({ onLoggedIn, onShowRegister }: LoginPageProps) {
  const dispatch = useAppDispatch();
  const auth = useAppSelector((state) => state.auth);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    dispatch(clearAuthError());
    setValidationError(null);

    if (!email.trim() || !password.trim()) {
      setValidationError("請輸入 Email 與密碼");
      return;
    }

    const resultAction = await dispatch(login({ email: email.trim(), password }));
    if (login.fulfilled.match(resultAction)) {
      onLoggedIn();
    }
  };

  return (
    <section className="card auth-card">
      <header className="auth-brand">
        <h1>智慧食材保存與膳食管理系統</h1>
        <p>Smart Pantry & Nutritionist System</p>
      </header>

      <h2 className="auth-form-title">登入</h2>
      <form className="auth-form" onSubmit={handleSubmit}>
        <label htmlFor="login-email">Email</label>
        <input
          id="login-email"
          name="email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="user@example.com"
        />

        <label htmlFor="login-password">密碼</label>
        <div className="password-field">
          <input
            id="login-password"
            name="password"
            type={showPassword ? "text" : "password"}
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="請輸入密碼"
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

        {(validationError || auth.error) && <p className="error-text">{validationError ?? auth.error}</p>}

        <button type="submit" className="btn primary" disabled={auth.loading} aria-label="送出登入">
          <FiLogIn aria-hidden="true" />
          {auth.loading ? "登入中..." : "登入"}
        </button>
      </form>

      <button type="button" className="btn ghost" onClick={onShowRegister} aria-label="切換到註冊頁">
        沒有帳號？前往註冊
        <FiUserPlus aria-hidden="true" />
      </button>
    </section>
  );
}
