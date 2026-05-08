import { FiFilter, FiPlus, FiSearch, FiSliders } from "react-icons/fi";

import type { ShoppingFilters as ShoppingFiltersType, ShoppingPurchasedFilter, ShoppingSort } from "../../features/shopping/shoppingTypes";

interface ShoppingFiltersProps {
  filters: ShoppingFiltersType;
  sort: ShoppingSort;
  onFiltersChange: (filters: ShoppingFiltersType) => void;
  onSortChange: (sort: ShoppingSort) => void;
  onCreateClick: () => void;
}

/** Shopping 篩選與操作工具列。 */
export function ShoppingFilters({ filters, sort, onFiltersChange, onSortChange, onCreateClick }: ShoppingFiltersProps) {
  const onPurchasedStatusChange = (value: string) => {
    onFiltersChange({ ...filters, isPurchased: value as ShoppingPurchasedFilter });
  };

  return (
    <section className="card shopping-toolbar">
      <label className="shopping-input-wrap">
        <FiSearch aria-hidden="true" />
        <input
          type="text"
          placeholder="搜尋購物項目"
          value={filters.q}
          onChange={(event) => onFiltersChange({ ...filters, q: event.target.value })}
        />
      </label>

      <label className="shopping-field-wrap">
        <span>
          <FiFilter aria-hidden="true" /> 狀態
        </span>
        <select value={filters.isPurchased} onChange={(event) => onPurchasedStatusChange(event.target.value)}>
          <option value="all">全部</option>
          <option value="unpurchased">未購買</option>
          <option value="purchased">已購買</option>
        </select>
      </label>

      <label className="shopping-field-wrap">
        <span>
          <FiSliders aria-hidden="true" /> 排序
        </span>
        <select value={sort} onChange={(event) => onSortChange(event.target.value as ShoppingSort)}>
          <option value="created_at">建立時間</option>
          <option value="name">名稱</option>
          <option value="purchased_at">已購買時間</option>
        </select>
      </label>

      <button type="button" className="btn shopping-add-btn" onClick={onCreateClick}>
        <FiPlus aria-hidden="true" /> 新增項目
      </button>
    </section>
  );
}
