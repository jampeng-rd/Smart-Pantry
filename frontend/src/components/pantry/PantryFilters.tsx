import { FiFilter, FiPlus, FiSearch, FiSliders } from "react-icons/fi";

import type { PantryFilters as PantryFiltersType, PantryItemStatus, PantrySort } from "../../features/pantry/pantryTypes";

interface PantryFiltersProps {
  filters: PantryFiltersType;
  sort: PantrySort;
  onFiltersChange: (filters: PantryFiltersType) => void;
  onSortChange: (sort: PantrySort) => void;
  onCreateClick: () => void;
}

/** Pantry 篩選與操作工具列。 */
export function PantryFilters({ filters, sort, onFiltersChange, onSortChange, onCreateClick }: PantryFiltersProps) {
  const onStatusChange = (value: string) => {
    onFiltersChange({ ...filters, status: value as PantryItemStatus | "all" });
  };

  return (
    <section className="card pantry-toolbar">
      <label className="pantry-input-wrap">
        <FiSearch aria-hidden="true" />
        <input
          type="text"
          placeholder="搜尋食材名稱或備註"
          value={filters.q}
          onChange={(event) => onFiltersChange({ ...filters, q: event.target.value })}
        />
      </label>

      <label className="pantry-field-wrap">
        <span>
          <FiFilter aria-hidden="true" /> 分類
        </span>
        <input
          type="text"
          placeholder="例如：蔬菜"
          value={filters.category}
          onChange={(event) => onFiltersChange({ ...filters, category: event.target.value })}
        />
      </label>

      <label className="pantry-field-wrap">
        <span>
          <FiFilter aria-hidden="true" /> 狀態
        </span>
        <select value={filters.status} onChange={(event) => onStatusChange(event.target.value)}>
          <option value="all">全部狀態</option>
          <option value="normal">正常</option>
          <option value="expiring_soon">即將到期</option>
          <option value="expired">已過期</option>
        </select>
      </label>

      <label className="pantry-field-wrap">
        <span>
          <FiSliders aria-hidden="true" /> 排序
        </span>
        <select value={sort} onChange={(event) => onSortChange(event.target.value as PantrySort)}>
          <option value="expiration_date">依過期日</option>
          <option value="created_at">依建立時間</option>
        </select>
      </label>

      <button type="button" className="btn pantry-add-btn" onClick={onCreateClick}>
        <FiPlus aria-hidden="true" /> 新增食材
      </button>
    </section>
  );
}
