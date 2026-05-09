import { useEffect, useMemo } from "react";
import { FiRefreshCw } from "react-icons/fi";

import { useAppDispatch, useAppSelector } from "../app/hooks";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingState } from "../components/common/LoadingState";
import { Pagination } from "../components/common/Pagination";
import { ExpirationEmptyState } from "../components/expiration/ExpirationEmptyState";
import { ExpirationFilters } from "../components/expiration/ExpirationFilters";
import { ExpirationItemList } from "../components/expiration/ExpirationItemList";
import { ExpirationSummaryCards } from "../components/expiration/ExpirationSummaryCards";
import {
  clearExpirationError,
  fetchExpirationSummary,
  setExpirationPage,
  setExpirationPageSize,
  setExpirationStatusFilter,
} from "../features/expiration/expirationSlice";
import type { ExpirationItem } from "../features/expiration/expirationTypes";

/** 到期提醒主頁。 */
export function ExpirationPage() {
  const dispatch = useAppDispatch();
  const { stats, items: unifiedItems, loading, error, selectedStatusFilter, page, pageSize } = useAppSelector((state) => state.expiration);

  useEffect(() => {
    void dispatch(fetchExpirationSummary());
  }, [dispatch]);

  const items = useMemo(() => {
    if (selectedStatusFilter === "expired") {
      return sortExpirationItems(unifiedItems.filter((item) => item.status === "expired"));
    }
    if (selectedStatusFilter === "expiring_soon") {
      return sortExpirationItems(unifiedItems.filter((item) => item.status === "expiring_soon"));
    }
    if (selectedStatusFilter === "normal") {
      return sortExpirationItems(unifiedItems.filter((item) => item.status === "normal"));
    }

    return sortExpirationItems(unifiedItems);
  }, [unifiedItems, selectedStatusFilter]);

  const emptyMessage = useMemo(() => {
    if (selectedStatusFilter === "all") {
      return "目前沒有食材資料";
    }
    if (selectedStatusFilter === "expired") {
      return "目前沒有已過期食材";
    }
    if (selectedStatusFilter === "expiring_soon") {
      return "目前沒有即將到期食材";
    }
    return "目前沒有正常食材";
  }, [selectedStatusFilter]);

  const showEmpty = !loading && !error && items.length === 0;
  const total = items.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const safePage = Math.min(Math.max(page, 1), totalPages);
  const pagedItems = useMemo(() => {
    const startIndex = (safePage - 1) * pageSize;
    return items.slice(startIndex, startIndex + pageSize);
  }, [items, pageSize, safePage]);

  return (
    <section className="workspace-expiration">
      <ExpirationSummaryCards stats={stats} />

      <ExpirationFilters
        selectedStatusFilter={selectedStatusFilter}
        onFilterChange={(status) => dispatch(setExpirationStatusFilter(status))}
      />

      {loading ? <LoadingState className="card expiration-loading" text="載入到期提醒中..." /> : null}

      {error ? (
        <ErrorState
          message={error}
          className="card pantry-error"
          actionsClassName="pantry-error-actions"
          onRetry={() => void dispatch(fetchExpirationSummary())}
          onClose={() => dispatch(clearExpirationError())}
          retryIcon={<FiRefreshCw aria-hidden="true" />}
        />
      ) : null}

      {showEmpty ? <ExpirationEmptyState message={emptyMessage} /> : null}

      {!loading && !error && !showEmpty ? <ExpirationItemList items={pagedItems} /> : null}

      {!loading && !error && !showEmpty ? (
        <Pagination
          page={safePage}
          pageSize={pageSize}
          total={total}
          pageSizeOptions={[10, 20, 50]}
          onPageChange={(nextPage) => dispatch(setExpirationPage(nextPage))}
          onPageSizeChange={(nextPageSize) => dispatch(setExpirationPageSize(nextPageSize))}
        />
      ) : null}
    </section>
  );
}

function sortExpirationItems(items: ExpirationItem[]): ExpirationItem[] {
  return [...items].sort((a, b) => {
    const statusOrder: Record<ExpirationItem["status"], number> = {
      expired: 0,
      expiring_soon: 1,
      normal: 2,
    };

    const statusDiff = statusOrder[a.status] - statusOrder[b.status];
    if (statusDiff !== 0) {
      return statusDiff;
    }

    if (!a.expiration_date && !b.expiration_date) {
      return a.id - b.id;
    }
    if (!a.expiration_date) {
      return 1;
    }
    if (!b.expiration_date) {
      return -1;
    }
    return a.expiration_date.localeCompare(b.expiration_date);
  });
}
