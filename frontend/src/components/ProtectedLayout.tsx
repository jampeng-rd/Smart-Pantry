import { ReactNode } from "react";
import { FiGrid, FiLogOut, FiMoon, FiSettings, FiSun, FiUser } from "react-icons/fi";

import { useAppDispatch, useAppSelector } from "../app/hooks";
import { logout } from "../features/auth/authSlice";
import { toggleTheme } from "../features/theme/themeSlice";

interface ProtectedLayoutProps {
  children: ReactNode;
  onLoggedOut: () => void;
}

/** 登入後共用版型（簡化左側區塊）。 */
export function ProtectedLayout({ children, onLoggedOut }: ProtectedLayoutProps) {
  const dispatch = useAppDispatch();
  const theme = useAppSelector((state) => state.theme.mode);
  const auth = useAppSelector((state) => state.auth);

  const handleLogout = async () => {
    await dispatch(logout());
    onLoggedOut();
  };

  return (
    <main className="app-shell app-layout">
      <aside className="card side-panel">
        <div className="side-top">
          <h1>智慧食材保存與膳食管理系統</h1>
          <p>Smart Pantry & Nutritionist</p>
        </div>

        <nav className="side-nav" aria-label="主要導覽">
          <p>
            <FiGrid aria-hidden="true" /> Dashboard Placeholder
          </p>
        </nav>

        <section className="side-user" aria-label="使用者設定區">
          <p>
            <FiUser aria-hidden="true" /> {auth.user?.display_name ?? "使用者"}
          </p>
          <p className="muted-text">{auth.user?.email ?? ""}</p>
          <div className="side-user-actions">
            <button type="button" className="btn" onClick={() => dispatch(toggleTheme())} aria-label="切換主題">
              {theme === "light-soft" ? <FiMoon aria-hidden="true" /> : <FiSun aria-hidden="true" />}
              <FiSettings aria-hidden="true" />
              主題
            </button>
            <button type="button" className="btn danger" onClick={handleLogout} aria-label="登出">
              <FiLogOut aria-hidden="true" />
              {auth.loading ? "登出中..." : "登出"}
            </button>
          </div>
        </section>
      </aside>

      <section className="layout-content">{children}</section>
    </main>
  );
}
