import { useEffect, useMemo } from "react";
import { FiAlertCircle, FiRefreshCw } from "react-icons/fi";

import { useAppDispatch, useAppSelector } from "../app/hooks";
import { ExpirationEmptyState } from "../components/expiration/ExpirationEmptyState";
import { ExpirationFilters } from "../components/expiration/ExpirationFilters";
import { ExpirationItemList } from "../components/expiration/ExpirationItemList";
import { ExpirationSummaryCards } from "../components/expiration/ExpirationSummaryCards";
import {
  clearExpirationError,
  fetchExpirationSummary,
  setExpirationStatusFilter,
} from "../features/expiration/expirationSlice";
import type { ExpirationItem } from "../features/expiration/expirationTypes";

/** 到期提醒主頁。 */
export function ExpirationPage() {
  const dispatch = useAppDispatch();
  const { summary, stats, loading, error, selectedStatusFilter } = useAppSelector((state) => state.expiration);

  useEffect(() => {
    void dispatch(fetchExpirationSummary());
  }, [dispatch]);

  const items = useMemo(() => {
    const expiredItems = summary?.expired_items ?? [];
    const expiringSoonItems = summary?.expiring_soon_items ?? [];

    if (selectedStatusFilter === "expired") {
      return expiredItems;
    }
    if (selectedStatusFilter === "expiring_soon") {
      return expiringSoonItems;
    }
    if (selectedStatusFilter === "normal") {
      return [] as ExpirationItem[];
    }

    return [...expiredItems, ...expiringSoonItems].sort((a, b) => {
      const aDate = a.expiration_date ?? "9999-12-31";
      const bDate = b.expiration_date ?? "9999-12-31";
      return aDate.localeCompare(bDate);
    });
  }, [summary, selectedStatusFilter]);

  const filterLabel = useMemo(() => {
    if (selectedStatusFilter === "expired") {
      return "已過期";
    }
    if (selectedStatusFilter === "expiring_soon") {
      return "即將到期";
    }
    if (selectedStatusFilter === "normal") {
      return "正常";
    }
    return "全部";
  }, [selectedStatusFilter]);

  const showEmpty = !loading && !error && items.length === 0;

  return (
    <section className="workspace-expiration">
      <ExpirationSummaryCards stats={stats} />

      <ExpirationFilters
        selectedStatusFilter={selectedStatusFilter}
        onFilterChange={(status) => dispatch(setExpirationStatusFilter(status))}
      />

      {loading ? <div className="card expiration-loading">載入到期提醒中...</div> : null}

      {error ? (
        <div className="card pantry-error" role="alert">
          <p>
            <FiAlertCircle aria-hidden="true" /> {error}
          </p>
          <div className="pantry-error-actions">
            <button type="button" className="btn ghost" onClick={() => void dispatch(fetchExpirationSummary())}>
              <FiRefreshCw aria-hidden="true" /> 重試
            </button>
            <button type="button" className="btn ghost" onClick={() => dispatch(clearExpirationError())}>
              關閉
            </button>
          </div>
        </div>
      ) : null}

      {showEmpty ? <ExpirationEmptyState statusLabel={filterLabel} /> : null}

      {!loading && !error && !showEmpty ? <ExpirationItemList items={items} /> : null}
    </section>
  );
}
