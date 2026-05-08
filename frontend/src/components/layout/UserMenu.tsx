import { FiHelpCircle, FiLogOut, FiMoon, FiSettings, FiSun, FiUser } from "react-icons/fi";

import type { ThemeMode } from "../../features/theme/themeTypes";

interface UserMenuProps {
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
  themeMode,
  loading,
  onProfile,
  onSettings,
  onHelp,
  onToggleTheme,
  onLogout,
}: UserMenuProps) {
  return (
    <div className="user-menu" role="menu" aria-label="使用者選單">
      <button type="button" className="user-menu-item" role="menuitem" onClick={onProfile}>
        <FiUser aria-hidden="true" /> Profile（個人資料）
      </button>
      <button type="button" className="user-menu-item" role="menuitem" onClick={onSettings}>
        <FiSettings aria-hidden="true" /> Settings（設定）
      </button>
      <button type="button" className="user-menu-item" role="menuitem" onClick={onHelp}>
        <FiHelpCircle aria-hidden="true" /> Help（說明）
      </button>
      <button type="button" className="user-menu-item" role="menuitem" onClick={onToggleTheme} aria-label="切換亮色與暗色主題">
        {themeMode === "light-soft" ? <FiMoon aria-hidden="true" /> : <FiSun aria-hidden="true" />} Theme Toggle（主題切換）
      </button>
      <button type="button" className="user-menu-item danger" role="menuitem" onClick={onLogout}>
        <FiLogOut aria-hidden="true" /> {loading ? "Log out..." : "Log out（登出）"}
      </button>
    </div>
  );
}
