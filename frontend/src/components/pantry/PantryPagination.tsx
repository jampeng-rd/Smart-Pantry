import { FiChevronLeft, FiChevronRight } from "react-icons/fi";

interface PantryPaginationProps {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (pageSize: number) => void;
}

/** 食材分頁控制列。 */
export function PantryPagination({ page, pageSize, total, onPageChange, onPageSizeChange }: PantryPaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const from = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const to = Math.min(total, page * pageSize);

  return (
    <div className="pantry-pagination">
      <p className="muted-text">
        顯示第 {from} - {to} 筆，共 {total} 筆
      </p>

      <div className="pantry-pagination-controls">
        <label>
          每頁
          <select value={pageSize} onChange={(event) => onPageSizeChange(Number(event.target.value))}>
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </select>
          筆
        </label>

        <button type="button" className="icon-btn" aria-label="上一頁" onClick={() => onPageChange(page - 1)} disabled={page <= 1}>
          <FiChevronLeft aria-hidden="true" />
        </button>
        <span>
          第 {page} / {totalPages} 頁
        </span>
        <button
          type="button"
          className="icon-btn"
          aria-label="下一頁"
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
        >
          <FiChevronRight aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}
