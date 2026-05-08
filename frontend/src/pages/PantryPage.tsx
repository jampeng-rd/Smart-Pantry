import { useEffect, useMemo, useState } from "react";
import { FiAlertCircle } from "react-icons/fi";

import { PantryEmptyState } from "../components/pantry/PantryEmptyState";
import { PantryFilters } from "../components/pantry/PantryFilters";
import { PantryFormDrawer } from "../components/pantry/PantryFormDrawer";
import { PantryPagination } from "../components/pantry/PantryPagination";
import { PantryTable } from "../components/pantry/PantryTable";
import { useAppDispatch, useAppSelector } from "../app/hooks";
import {
  clearPantryError,
  createPantryItem,
  deletePantryItem,
  fetchPantryItems,
  setFilters,
  setPage,
  setPageSize,
  setSort,
  updatePantryItem,
} from "../features/pantry/pantrySlice";
import type { PantryCreatePayload, PantryItem } from "../features/pantry/pantryTypes";

/** Pantry 食材庫存管理頁。 */
export function PantryPage() {
  const dispatch = useAppDispatch();
  const { items, loading, error, page, pageSize, total, filters, sort } = useAppSelector((state) => state.pantry);

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<PantryItem | null>(null);

  useEffect(() => {
    void dispatch(fetchPantryItems());
  }, [dispatch, page, pageSize, filters, sort]);

  const isEmpty = useMemo(() => !loading && !error && items.length === 0, [loading, error, items.length]);

  const onCreateClick = () => {
    setEditingItem(null);
    setDrawerOpen(true);
  };

  const onEditClick = (item: PantryItem) => {
    setEditingItem(item);
    setDrawerOpen(true);
  };

  const onDeleteClick = async (item: PantryItem) => {
    const confirmed = window.confirm(`確定要刪除「${item.name}」嗎？`);
    if (!confirmed) {
      return;
    }

    await dispatch(deletePantryItem(item.id)).unwrap();

    if (items.length === 1 && page > 1) {
      dispatch(setPage(page - 1));
      return;
    }
    await dispatch(fetchPantryItems()).unwrap();
  };

  const onDrawerSubmit = async (payload: PantryCreatePayload) => {
    if (editingItem) {
      await dispatch(updatePantryItem({ itemId: editingItem.id, payload })).unwrap();
    } else {
      await dispatch(createPantryItem(payload)).unwrap();
    }
    setDrawerOpen(false);
    setEditingItem(null);
    await dispatch(fetchPantryItems()).unwrap();
  };

  return (
    <section className="workspace-pantry">
      <PantryFilters
        filters={filters}
        sort={sort}
        onFiltersChange={(nextFilters) => dispatch(setFilters(nextFilters))}
        onSortChange={(nextSort) => dispatch(setSort(nextSort))}
        onCreateClick={onCreateClick}
      />

      {loading ? <div className="card pantry-loading">載入中...</div> : null}

      {error ? (
        <div className="card pantry-error" role="alert">
          <p>
            <FiAlertCircle aria-hidden="true" /> {error}
          </p>
          <div className="pantry-error-actions">
            <button type="button" className="btn ghost" onClick={() => void dispatch(fetchPantryItems())}>
              重試
            </button>
            <button type="button" className="btn ghost" onClick={() => dispatch(clearPantryError())}>
              關閉
            </button>
          </div>
        </div>
      ) : null}

      {isEmpty ? <PantryEmptyState /> : null}

      {!isEmpty && !error ? <PantryTable items={items} onEdit={onEditClick} onDelete={(item) => void onDeleteClick(item)} /> : null}

      {!isEmpty && !error ? (
        <PantryPagination
          page={page}
          pageSize={pageSize}
          total={total}
          onPageChange={(nextPage) => dispatch(setPage(nextPage))}
          onPageSizeChange={(nextPageSize) => dispatch(setPageSize(nextPageSize))}
        />
      ) : null}

      <PantryFormDrawer
        open={drawerOpen}
        loading={loading}
        initialItem={editingItem}
        onClose={() => setDrawerOpen(false)}
        onSubmit={onDrawerSubmit}
      />
    </section>
  );
}
