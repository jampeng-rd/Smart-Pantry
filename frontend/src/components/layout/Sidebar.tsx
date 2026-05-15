import type { ReactElement } from "react";
import {
  FiActivity,
  FiArchive,
  FiBookOpen,
  FiCamera,
  FiChevronLeft,
  FiChevronRight,
  FiClock,
  FiGrid,
  FiShoppingCart,
  FiUser,
  FiUsers,
} from "react-icons/fi";

import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { logout } from "../../features/auth/authSlice";
import { toggleTheme } from "../../features/theme/themeSlice";
import { UserMenu } from "./UserMenu";
import darkSoftLogo from "../../../assets/dark_soft_logo.png";
import lightSoftLogo from "../../../assets/light_soft_logo.png";

export interface NavItem {
  key: string;
  label: string;
  path: string;
  icon: ReactElement;
}

interface SidebarProps {
  navItems: NavItem[];
  activePath: string;
  collapsed: boolean;
  isMobile: boolean;
  mobileOpen: boolean;
  userMenuOpen: boolean;
  onNavigate: (path: string) => void;
  onToggleCollapsed: () => void;
  onOpenMobile: () => void;
  onCloseMobile: () => void;
  onToggleUserMenu: () => void;
  onCloseUserMenu: () => void;
}

const iconMap: Record<string, ReactElement> = {
  dashboard: <FiGrid aria-hidden="true" />,
  pantry: <FiArchive aria-hidden="true" />,
  expiration: <FiClock aria-hidden="true" />,
  shopping: <FiShoppingCart aria-hidden="true" />,
  recipes: <FiBookOpen aria-hidden="true" />,
  ingredients: <FiCamera aria-hidden="true" />,
  nutrition: <FiActivity aria-hidden="true" />,
  "admin-members": <FiUsers aria-hidden="true" />,
};

/** Dashboard 側邊導覽。 */
export function Sidebar({
  navItems,
  activePath,
  collapsed,
  isMobile,
  mobileOpen,
  userMenuOpen,
  onNavigate,
  onToggleCollapsed,
  onOpenMobile,
  onCloseMobile,
  onToggleUserMenu,
  onCloseUserMenu,
}: SidebarProps) {
  const dispatch = useAppDispatch();
  const auth = useAppSelector((state) => state.auth);
  const themeMode = useAppSelector((state) => state.theme.mode);
  const subscriptionTier = (auth.user as { subscription_tier?: string } | null)?.subscription_tier;
  const sidebarLogo = themeMode === "dark-soft" ? darkSoftLogo : lightSoftLogo;
  const isCollapsedDesktop = collapsed && !isMobile;

  const handleNavigate = (path: string) => {
    onNavigate(path);
    onCloseUserMenu();
    if (isMobile) {
      onCloseMobile();
    }
  };

  const handleLogout = async () => {
    await dispatch(logout());
    onCloseUserMenu();
    onNavigate("/");
  };

  const isDrawerOpen = isMobile ? mobileOpen : true;

  return (
    <>
      {isMobile ? (
        <button
          type="button"
          className={`sidebar-overlay${mobileOpen ? " open" : ""}`}
          aria-label="關閉側邊導覽選單"
          onClick={onCloseMobile}
        />
      ) : null}

      <aside className={`sidebar ${collapsed ? "collapsed" : "expanded"} ${isDrawerOpen ? "open" : ""}`}>
        <div className="sidebar-logo">
          {isCollapsedDesktop ? (
            <div className="collapsed-logo-switcher">
              <img src={sidebarLogo} className="logo-icon" alt="智慧食材系統 Logo" />
              <button type="button" className="icon-btn collapsed-expand-btn" aria-label="展開側邊欄" onClick={onToggleCollapsed}>
                <FiChevronRight aria-hidden="true" />
              </button>
            </div>
          ) : (
            <div className="logo-text-wrap">
              <p className="logo-zh">智慧食材系統</p>
              <p className="logo-en">Smart Pantry</p>
            </div>
          )}

          {!isCollapsedDesktop ? (
            <button
              type="button"
              className="icon-btn"
              aria-label={collapsed ? "展開側邊欄" : "收合側邊欄"}
              onClick={isMobile ? (mobileOpen ? onCloseMobile : onOpenMobile) : onToggleCollapsed}
            >
              {collapsed ? <FiChevronRight aria-hidden="true" /> : <FiChevronLeft aria-hidden="true" />}
            </button>
          ) : null}
        </div>

        <nav className="sidebar-nav" aria-label="主要導覽">
          {navItems.map((item) => {
            const isActive = activePath === item.path;
            return (
              <button
                key={item.key}
                type="button"
                className={`nav-item${isActive ? " active" : ""}`}
                aria-label={`前往 ${item.label}`}
                onClick={() => handleNavigate(item.path)}
              >
                <span className="nav-icon">{iconMap[item.key] ?? item.icon}</span>
                <span className={`nav-label${collapsed && !isMobile ? " hidden" : ""}`}>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <section className="sidebar-user-wrap" aria-label="使用者區塊">
          {userMenuOpen ? (
            <UserMenu
              collapsed={isCollapsedDesktop}
              themeMode={themeMode}
              loading={auth.loading}
              onProfile={() => handleNavigate("/profile")}
              onSettings={() => handleNavigate("/settings")}
              onHelp={() => handleNavigate("/help")}
              onToggleTheme={() => dispatch(toggleTheme())}
              onLogout={() => void handleLogout()}
            />
          ) : null}

          <button type="button" className="sidebar-user" onClick={onToggleUserMenu} aria-label="開啟使用者選單">
            <span className="nav-icon">
              <FiUser aria-hidden="true" />
            </span>
            <span className={`user-meta${collapsed && !isMobile ? " hidden" : ""}`}>
              <strong>{auth.user?.display_name ?? "使用者"}</strong>
              {subscriptionTier === "PRO" ? <small className="pro-badge">PRO</small> : null}
            </span>
          </button>
        </section>
      </aside>
    </>
  );
}
