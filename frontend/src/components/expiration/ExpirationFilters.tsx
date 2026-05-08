import { FiCheckCircle, FiFilter, FiLayers, FiClock, FiXCircle } from "react-icons/fi";

import type { ExpirationStatusFilter } from "../../features/expiration/expirationTypes";

interface ExpirationFiltersProps {
  selectedStatusFilter: ExpirationStatusFilter;
  onFilterChange: (status: ExpirationStatusFilter) => void;
}

/** 到期提醒狀態篩選列。 */
export function ExpirationFilters({ selectedStatusFilter, onFilterChange }: ExpirationFiltersProps) {
  return (
    <section className="card expiration-filters" aria-label="到期提醒篩選">
      <p className="expiration-filters-title">
        <FiFilter aria-hidden="true" /> 狀態篩選
      </p>
      <div className="expiration-filter-buttons" role="tablist" aria-label="到期狀態">
        <button
          type="button"
          className={`btn ghost expiration-filter-btn${selectedStatusFilter === "all" ? " active" : ""}`}
          onClick={() => onFilterChange("all")}
        >
          <FiLayers aria-hidden="true" /> 全部
        </button>
        <button
          type="button"
          className={`btn ghost expiration-filter-btn${selectedStatusFilter === "expired" ? " active" : ""}`}
          onClick={() => onFilterChange("expired")}
        >
          <FiXCircle aria-hidden="true" /> 已過期
        </button>
        <button
          type="button"
          className={`btn ghost expiration-filter-btn${selectedStatusFilter === "expiring_soon" ? " active" : ""}`}
          onClick={() => onFilterChange("expiring_soon")}
        >
          <FiClock aria-hidden="true" /> 即將到期
        </button>
        <button
          type="button"
          className={`btn ghost expiration-filter-btn${selectedStatusFilter === "normal" ? " active" : ""}`}
          onClick={() => onFilterChange("normal")}
        >
          <FiCheckCircle aria-hidden="true" /> 正常
        </button>
      </div>
    </section>
  );
}
