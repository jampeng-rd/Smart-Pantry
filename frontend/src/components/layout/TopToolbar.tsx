import { FiMenu, FiMoreHorizontal, FiSearch } from "react-icons/fi";

interface TopToolbarProps {
  pageTitle: string;
  isMobile: boolean;
  onMobileMenuOpen: () => void;
}

/** 工作區頂部工具列。 */
export function TopToolbar({ pageTitle, isMobile, onMobileMenuOpen }: TopToolbarProps) {
  return (
    <header className="top-toolbar">
      <div className="toolbar-title-row">
        {isMobile ? (
          <button type="button" className="icon-btn" aria-label="開啟側邊導覽選單" onClick={onMobileMenuOpen}>
            <FiMenu aria-hidden="true" />
          </button>
        ) : null}
        <h1>{pageTitle}</h1>
      </div>

      <div className="toolbar-actions">
        <label className="toolbar-search" aria-label="搜尋（佔位功能）">
          <FiSearch aria-hidden="true" />
          <input type="text" placeholder="搜尋（Phase 06-2 佔位）" />
        </label>

        <button type="button" className="icon-btn toolbar-more-btn" aria-label="更多頁面操作">
          <FiMoreHorizontal aria-hidden="true" />
        </button>
      </div>
    </header>
  );
}
