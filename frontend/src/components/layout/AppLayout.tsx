import { ReactNode, useEffect, useMemo, useState } from "react";
import {
  FiActivity,
  FiArchive,
  FiBookOpen,
  FiCamera,
  FiClock,
  FiGrid,
  FiHelpCircle,
  FiShoppingCart,
  FiSettings,
  FiUser,
  FiUsers,
  FiCreditCard,
  FiRepeat,
} from "react-icons/fi";

import { useAppSelector } from "../../app/hooks";
import { Sidebar, type NavItem } from "./Sidebar";
import { TopToolbar } from "./TopToolbar";

interface AppLayoutProps {
  pathname: string;
  children: ReactNode;
  onNavigate: (path: string) => void;
}

const MOBILE_BREAKPOINT = 1024;

const navItems: NavItem[] = [
  // { key: "dashboard", label: "儀表板", path: "/dashboard", icon: <FiGrid aria-hidden="true" /> },
  { key: "pantry", label: "食材庫存", path: "/pantry", icon: <FiArchive aria-hidden="true" /> },
  { key: "expiration", label: "到期提醒", path: "/expiration", icon: <FiClock aria-hidden="true" /> },
  { key: "shopping", label: "購物清單", path: "/shopping", icon: <FiShoppingCart aria-hidden="true" /> },
  { key: "ingredients", label: "食材辨識", path: "/ingredients", icon: <FiCamera aria-hidden="true" /> },
  { key: "recipes", label: "食譜建議", path: "/recipes", icon: <FiBookOpen aria-hidden="true" /> },
  // { key: "nutrition", label: "營養估算", path: "/nutrition", icon: <FiActivity aria-hidden="true" /> },
];

/** Dashboard 主版型。 */
export function AppLayout({ pathname, children, onNavigate }: AppLayoutProps) {
  const user = useAppSelector((state) => state.auth.user);
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= MOBILE_BREAKPOINT);

  useEffect(() => {
    const onResize = () => setIsMobile(window.innerWidth <= MOBILE_BREAKPOINT);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  useEffect(() => {
    if (!isMobile) {
      setMobileOpen(false);
    }
  }, [isMobile]);

  useEffect(() => {
    setUserMenuOpen(false);
  }, [pathname]);

  useEffect(() => {
    document.body.style.overflow = isMobile && mobileOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [isMobile, mobileOpen]);

  const visibleNavItems = useMemo(() => {
    const items = [...navItems];
    if (user?.is_admin) {
      items.push({ key: "admin-members", label: "會員管理", path: "/admin/members", icon: <FiUsers aria-hidden="true" /> });
    }
    return items;
  }, [user?.is_admin]);

  const currentTitle = useMemo(() => {
    if (pathname === "/profile") {
      return { icon: <FiUser aria-hidden="true" />, text: "個人資料" };
    }
    if (pathname === "/settings") {
      return { icon: <FiSettings aria-hidden="true" />, text: "系統設定" };
    }
    if (pathname === "/help") {
      return { icon: <FiHelpCircle aria-hidden="true" />, text: "使用說明" };
    }
    if (pathname === "/billing/upgrade") {
      return { icon: <FiCreditCard aria-hidden="true" />, text: "升級 PRO" };
    }
    if (pathname === "/billing/newebpay-one-time") {
      return { icon: <FiCreditCard aria-hidden="true" />, text: "藍新單次付款" };
    }
    if (pathname === "/billing/newebpay-subscription") {
      return { icon: <FiRepeat aria-hidden="true" />, text: "藍新訂閱付款" };
    }
    if (pathname === "/pantry") {
      return { icon: <FiArchive aria-hidden="true" />, text: "食材庫存" };
    }

    const matched = visibleNavItems.find((item) => item.path === pathname);
    if (matched) {
      return { icon: matched.icon, text: matched.label };
    }

    return { icon: <FiGrid aria-hidden="true" />, text: "儀表板" };
  }, [pathname, visibleNavItems]);

  return (
    <main className="dashboard-shell">
      <Sidebar
        navItems={visibleNavItems}
        activePath={pathname}
        collapsed={collapsed}
        isMobile={isMobile}
        mobileOpen={mobileOpen}
        userMenuOpen={userMenuOpen}
        onNavigate={onNavigate}
        onToggleCollapsed={() => setCollapsed((prev) => !prev)}
        onOpenMobile={() => setMobileOpen(true)}
        onCloseMobile={() => setMobileOpen(false)}
        onToggleUserMenu={() => setUserMenuOpen((prev) => !prev)}
        onCloseUserMenu={() => setUserMenuOpen(false)}
      />

      <section className="main-layout">
        <TopToolbar
          pageIcon={currentTitle.icon}
          pageTitleText={currentTitle.text}
          isMobile={isMobile}
          onMobileMenuOpen={() => setMobileOpen(true)}
        />
        <div className="workspace">{children}</div>
      </section>
    </main>
  );
}
