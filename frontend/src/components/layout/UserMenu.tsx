import { FiHelpCircle, FiLogOut, FiMoon, FiSettings, FiSun, FiUser } from "react-icons/fi";

import type { ThemeMode } from "../../features/theme/themeTypes";

interface UserMenuProps {
  collapsed: boolean;
  themeMode: ThemeMode;
  loading: boolean;
  onProfile: () => void;
  onSettings: () => void;
  onHelp: () => void;
  onToggleTheme: () => void;
  onLogout: () => void;
}

/** 使用者區塊向上展開選單。 */
export function UserMenu({
  collapsed,
  themeMode,
  loading,
  onProfile,
  onSettings,
  onHelp,
  onToggleTheme,
  onLogout,
}: UserMenuProps) {
  const themeLabel = themeMode === "light-soft" ? "切換至暗色主題" : "切換至亮色主題";
  const logoutLabel = loading ? "登出中" : "登出";

  return (
    <div className={`user-menu${collapsed ? " icon-only" : ""}`} role="menu" aria-label="使用者選單">
      <button type="button" className="user-menu-item" role="menuitem" aria-label="個人資料" title="個人資料" onClick={onProfile}>
        <FiUser aria-hidden="true" />
        {collapsed ? null : "個人資料"}
      </button>
      <button type="button" className="user-menu-item" role="menuitem" aria-label="設定" title="設定" onClick={onSettings}>
        <FiSettings aria-hidden="true" />
        {collapsed ? null : "系統設定"}
      </button>
      <button type="button" className="user-menu-item" role="menuitem" aria-label="說明" title="說明" onClick={onHelp}>
        <FiHelpCircle aria-hidden="true" />
        {collapsed ? null : "使用說明"}
      </button>
      {/* Phase 10-1 UX：主題切換功能已移到 Settings 第一個區塊，UserMenu 先暫時隱藏。 */}
      {/* <button
        type="button"
        className="user-menu-item"
        role="menuitem"
        onClick={onToggleTheme}
        aria-label={themeLabel}
        title={themeLabel}
      >
        {themeMode === "light-soft" ? <FiMoon aria-hidden="true" /> : <FiSun aria-hidden="true" />}
        {collapsed ? null : "主題切換"}
      </button> */}
      <button type="button" className="user-menu-item danger" role="menuitem" aria-label={logoutLabel} title={logoutLabel} onClick={onLogout}>
        <FiLogOut aria-hidden="true" />
        {collapsed ? null : (loading ? "登出中..." : "登出")}
      </button>
    </div>
  );
}
