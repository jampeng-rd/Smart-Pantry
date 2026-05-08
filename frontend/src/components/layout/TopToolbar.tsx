import type { ReactNode } from "react";
import { FiMoreHorizontal, FiMenu } from "react-icons/fi";

interface TopToolbarProps {
  pageIcon?: ReactNode;
  pageTitleText: string;
  isMobile: boolean;
  onMobileMenuOpen: () => void;
}

/** 工作區頂部工具列。 */
export function TopToolbar({ pageIcon, pageTitleText, isMobile, onMobileMenuOpen }: TopToolbarProps) {
  return (
    <header className="top-toolbar">
      <div className="toolbar-title-row">
        {isMobile ? (
          <button type="button" className="icon-btn" aria-label="開啟側邊導覽選單" onClick={onMobileMenuOpen}>
            <FiMenu aria-hidden="true" />
          </button>
        ) : null}
        <h1 className="toolbar-page-title">
          {pageIcon ? <span className="toolbar-page-title-icon">{pageIcon}</span> : null}
          <span className="toolbar-page-title-text">{pageTitleText}</span>
        </h1>
      </div>

      <div className="toolbar-actions">
        <button type="button" className="icon-btn toolbar-more-btn" aria-label="更多頁面操作">
          <FiMoreHorizontal aria-hidden="true" />
        </button>
      </div>
    </header>
  );
}
