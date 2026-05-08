import { useEffect, useMemo, useState } from "react";
import { FiAlertCircle } from "react-icons/fi";

import { useAppDispatch, useAppSelector } from "../app/hooks";
import { Pagination } from "../components/common/Pagination";
import { ShoppingEmptyState } from "../components/shopping/ShoppingEmptyState";
import { ShoppingFilters } from "../components/shopping/ShoppingFilters";
import { ShoppingFormDrawer } from "../components/shopping/ShoppingFormDrawer";
import { ShoppingTable } from "../components/shopping/ShoppingTable";
import { ShoppingToPantryDrawer } from "../components/shopping/ShoppingToPantryDrawer";
import type { PantryCreatePayload } from "../features/pantry/pantryTypes";
import {
  clearShoppingError,
  createShoppingItem,
  deleteShoppingItem,
  fetchShoppingItems,
  setShoppingFilters,
  setShoppingPage,
  setShoppingPageSize,
  setShoppingSort,
  updateShoppingItem,
} from "../features/shopping/shoppingSlice";
import type { ShoppingCreatePayload, ShoppingItem } from "../features/shopping/shoppingTypes";
import { pantryApi } from "../services/apiClient";

/** Shopping 購物清單管理頁。 */
export function ShoppingPage() {
  const dispatch = useAppDispatch();
  const { items, loading, error, page, pageSize, total, filters, sort } = useAppSelector((state) => state.shopping);

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<ShoppingItem | null>(null);
  const [toPantryDrawerOpen, setToPantryDrawerOpen] = useState(false);
  const [toPantryItem, setToPantryItem] = useState<ShoppingItem | null>(null);
  const [toPantryLoading, setToPantryLoading] = useState(false);
  const [integrationMessage, setIntegrationMessage] = useState<string | null>(null);
  const [integrationError, setIntegrationError] = useState<string | null>(null);

  useEffect(() => {
    void dispatch(fetchShoppingItems());
  }, [dispatch, page, pageSize, filters, sort]);

  const isEmpty = useMemo(() => !loading && !error && items.length === 0, [loading, error, items.length]);

  const onCreateClick = () => {
    setEditingItem(null);
    setDrawerOpen(true);
  };

  const onEditClick = (item: ShoppingItem) => {
    setEditingItem(item);
    setDrawerOpen(true);
  };

  const onTogglePurchased = async (item: ShoppingItem) => {
    await dispatch(updateShoppingItem({ itemId: item.id, payload: { is_purchased: !item.is_purchased } })).unwrap();
    await dispatch(fetchShoppingItems()).unwrap();
  };

  const onDeleteClick = async (item: ShoppingItem) => {
    const confirmed = window.confirm(`確定要刪除「${item.name}」嗎？`);
    if (!confirmed) {
      return;
    }

    await dispatch(deleteShoppingItem(item.id)).unwrap();

    if (items.length === 1 && page > 1) {
      dispatch(setShoppingPage(page - 1));
      return;
    }
    await dispatch(fetchShoppingItems()).unwrap();
  };

  const onDrawerSubmit = async (payload: ShoppingCreatePayload) => {
    if (editingItem) {
      await dispatch(
        updateShoppingItem({
          itemId: editingItem.id,
          payload: {
            name: payload.name,
            quantity: payload.quantity,
            unit: payload.unit,
          },
        }),
      ).unwrap();
    } else {
      await dispatch(createShoppingItem(payload)).unwrap();
    }

    setDrawerOpen(false);
    setEditingItem(null);
    await dispatch(fetchShoppingItems()).unwrap();
  };

  const onOpenAddToPantry = (item: ShoppingItem) => {
    if (!item.is_purchased) {
      return;
    }
    setToPantryItem(item);
    setToPantryDrawerOpen(true);
  };

  const onAddToPantrySubmit = async (payload: PantryCreatePayload) => {
    if (!toPantryItem) {
      return;
    }

    setIntegrationError(null);
    setToPantryLoading(true);
    try {
      await pantryApi.create(payload);
      try {
        await dispatch(deleteShoppingItem(toPantryItem.id)).unwrap();
        setToPantryDrawerOpen(false);
        setToPantryItem(null);
        await dispatch(fetchShoppingItems()).unwrap();
        setIntegrationMessage("已加入庫存，並從購物清單移除。");
      } catch {
        setToPantryDrawerOpen(false);
        setToPantryItem(null);
        await dispatch(fetchShoppingItems()).unwrap();
        setIntegrationError("已加入庫存，但購物清單項目移除失敗，請稍後手動刪除。");
      }
    } catch (error) {
      setIntegrationError(getFriendlyShoppingMessage(error));
    } finally {
      setToPantryLoading(false);
    }
  };

  return (
    <section className="workspace-shopping">
      <ShoppingFilters
        filters={filters}
        sort={sort}
        onFiltersChange={(nextFilters) => dispatch(setShoppingFilters(nextFilters))}
        onSortChange={(nextSort) => dispatch(setShoppingSort(nextSort))}
        onCreateClick={onCreateClick}
      />

      {loading ? <div className="card shopping-loading">載入中...</div> : null}

      {error ? (
        <div className="card shopping-error" role="alert">
          <p>
            <FiAlertCircle aria-hidden="true" /> {error}
          </p>
          <div className="shopping-error-actions">
            <button type="button" className="btn ghost" onClick={() => void dispatch(fetchShoppingItems())}>
              重試
            </button>
            <button type="button" className="btn ghost" onClick={() => dispatch(clearShoppingError())}>
              關閉
            </button>
          </div>
        </div>
      ) : null}

      {integrationMessage ? (
        <div className="card integration-success" role="status">
          <p>{integrationMessage}</p>
          <button type="button" className="btn ghost" onClick={() => setIntegrationMessage(null)}>
            關閉
          </button>
        </div>
      ) : null}

      {integrationError ? (
        <div className="card shopping-error" role="alert">
          <p>
            <FiAlertCircle aria-hidden="true" /> {integrationError}
          </p>
          <div className="shopping-error-actions">
            <button type="button" className="btn ghost" onClick={() => setIntegrationError(null)}>
              關閉
            </button>
          </div>
        </div>
      ) : null}

      {isEmpty ? <ShoppingEmptyState /> : null}

      {!isEmpty && !error ? (
        <ShoppingTable
          items={items}
          onEdit={onEditClick}
          onDelete={(item) => void onDeleteClick(item)}
          onTogglePurchased={(item) => void onTogglePurchased(item)}
          onAddToPantry={onOpenAddToPantry}
        />
      ) : null}

      {!isEmpty && !error ? (
        <Pagination
          page={page}
          pageSize={pageSize}
          total={total}
          onPageChange={(nextPage) => dispatch(setShoppingPage(nextPage))}
          onPageSizeChange={(nextPageSize) => dispatch(setShoppingPageSize(nextPageSize))}
        />
      ) : null}

      <ShoppingFormDrawer
        open={drawerOpen}
        loading={loading}
        initialItem={editingItem}
        onClose={() => setDrawerOpen(false)}
        onSubmit={onDrawerSubmit}
      />

      <ShoppingToPantryDrawer
        open={toPantryDrawerOpen}
        loading={toPantryLoading}
        item={toPantryItem}
        onClose={() => {
          setToPantryDrawerOpen(false);
          setToPantryItem(null);
        }}
        onSubmit={onAddToPantrySubmit}
      />
    </section>
  );
}

function getFriendlyShoppingMessage(error: unknown): string {
  if (!(error instanceof Error)) {
    return "操作失敗，請稍後再試。";
  }

  const text = error.message.toLowerCase();
  if (text.includes("networkerror") || text.includes("failed to fetch") || text.includes("load failed")) {
    return "網路連線異常，請稍後再試。";
  }

  return "操作失敗，請稍後再試。";
}
