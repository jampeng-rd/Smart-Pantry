import { FiChevronLeft, FiChevronRight } from "react-icons/fi";

interface PaginationProps {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (pageSize: number) => void;
  pageSizeOptions?: number[];
}

/** 共用分頁控制列。 */
export function Pagination({
  page,
  pageSize,
  total,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = [10, 20, 50],
}: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const safePage = Math.min(Math.max(page, 1), totalPages);
  const from = total === 0 ? 0 : (safePage - 1) * pageSize + 1;
  const to = Math.min(total, safePage * pageSize);

  return (
    <div className="common-pagination">
      <p className="muted-text">
        顯示第 {from} - {to} 筆，共 {total} 筆
      </p>

      <div className="common-pagination-controls">
        <label>
          每頁
          <select value={pageSize} onChange={(event) => onPageSizeChange(Number(event.target.value))}>
            {pageSizeOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          筆
        </label>

        <button type="button" className="icon-btn" aria-label="上一頁" onClick={() => onPageChange(safePage - 1)} disabled={safePage <= 1}>
          <FiChevronLeft aria-hidden="true" />
        </button>
        <span>
          第 {safePage} / {totalPages} 頁
        </span>
        <button
          type="button"
          className="icon-btn"
          aria-label="下一頁"
          onClick={() => onPageChange(safePage + 1)}
          disabled={safePage >= totalPages}
        >
          <FiChevronRight aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}
