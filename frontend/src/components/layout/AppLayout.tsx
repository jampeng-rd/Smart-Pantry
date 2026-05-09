import { ReactNode, useEffect, useMemo, useState } from "react";
import {
  FiActivity,
  FiArchive,
  FiBookOpen,
  FiCamera,
  FiClock,
  FiGrid,
  FiShoppingCart,
} from "react-icons/fi";

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
  // { key: "recipes", label: "食譜建議", path: "/recipes", icon: <FiBookOpen aria-hidden="true" /> },
  // { key: "ocr", label: "OCR 匯入", path: "/ocr", icon: <FiCamera aria-hidden="true" /> },
  // { key: "nutrition", label: "營養估算", path: "/nutrition", icon: <FiActivity aria-hidden="true" /> },
];

/** Dashboard 主版型。 */
export function AppLayout({ pathname, children, onNavigate }: AppLayoutProps) {
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

  const currentTitle = useMemo(() => {
    if (pathname === "/pantry") {
      return { icon: <FiArchive aria-hidden="true" />, text: "食材庫存" };
    }

    const matched = navItems.find((item) => item.path === pathname);
    if (matched) {
      return { icon: matched.icon, text: matched.label };
    }

    return { icon: <FiGrid aria-hidden="true" />, text: "儀表板" };
  }, [pathname]);

  return (
    <main className="dashboard-shell">
      <Sidebar
        navItems={navItems}
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
