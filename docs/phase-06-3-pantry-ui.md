# Phase 06-3：Pantry UI

## 1. 階段目標

完成「食材庫存管理」前端功能，包含列表顯示、搜尋篩選、排序、pagination，以及新增/編輯/刪除與 loading/error/empty state。

## 2. 完成內容

- 新增 Pantry feature 型別：`PantryItem`、`PantryState`、查詢與 CRUD payload 型別。
- 完整實作 `pantrySlice`：
  - thunks：`fetchPantryItems`、`createPantryItem`、`updatePantryItem`、`deletePantryItem`
  - reducers：`setFilters`、`setPage`、`setPageSize`、`setSort`、`clearPantryError`
- `apiClient` 新增 `pantryApi`，統一走 `requestWithAuth`：
  - `list(params)`
  - `create(payload)`
  - `update(itemId, payload)`
  - `remove(itemId)`
- 新增 Pantry UI 元件：
  - `PantryFilters`
  - `PantryTable`
  - `PantryFormDrawer`
  - `PantryEmptyState`
  - `PantryPagination`
- `PantryPage` 從 placeholder 改為完整 CRUD 工作頁。
- 補齊 Pantry 專用 CSS（toolbar/table/drawer/status/error/loading/empty/responsive）。

## 3. 涉及檔案

- `frontend/src/features/pantry/pantryTypes.ts`
- `frontend/src/features/pantry/pantrySlice.ts`
- `frontend/src/pages/PantryPage.tsx`
- `frontend/src/components/pantry/PantryFilters.tsx`
- `frontend/src/components/pantry/PantryTable.tsx`
- `frontend/src/components/pantry/PantryFormDrawer.tsx`
- `frontend/src/components/pantry/PantryEmptyState.tsx`
- `frontend/src/components/pantry/PantryPagination.tsx`
- `frontend/src/services/apiClient.ts`
- `frontend/src/styles/globals.css`
- `docs/phase-06-3-pantry-ui.md`
- `README.md`

## 4. 如何啟動

```bash
cd frontend
npm install
npm run dev
```

## 5. Web UI 測試方式

1. 先啟動 backend（預設 `http://localhost:8000`）。
2. 啟動 frontend，登入後進入 `/pantry`。
3. 測試新增食材（名稱/數量必填）。
4. 測試編輯食材（開啟 drawer 後修改欄位）。
5. 測試刪除食材（確認視窗後刪除）。
6. 測試搜尋（名稱或備註關鍵字）。
7. 測試分類/狀態篩選、過期日排序。
8. 測試換頁與調整 page size。
9. 測試空資料、載入中與錯誤顯示。

## 6. API 串接說明

- `POST /pantry/items`：新增食材。
- `GET /pantry/items`：列表查詢，支援 `category/status/sort/q/page/page_size`。
- `PATCH /pantry/items/{item_id}`：更新食材。
- `DELETE /pantry/items/{item_id}`：刪除食材。

所有 Pantry API 都透過 `requestWithAuth` 發送，沿用 access token 快過期預先 refresh 與 401 單次 refresh 重送策略。

## 7. Pagination / Filter / Sort 說明

- `filters`：`q`（搜尋）、`category`（分類）、`status`（狀態）。
- `sort`：預設 `expiration_date`，可切到 `created_at`。
- `page` / `pageSize` 由 Redux 狀態控制。
- 任一篩選或排序更新時，會自動重置回第 1 頁。

## 8. 已知限制

- Pantry mobile 版目前使用 table-to-card CSS 轉換，後續可再抽成獨立 card component。
- 分類篩選目前為文字輸入，尚未改成後端分類選單。
- `sort=created_at` 需後端支援才有完整效果；若後端忽略此參數，實際排序仍以後端結果為準。
- 刪除確認目前使用 `window.confirm`，後續可改成一致化 modal。

## 9. 下一階段建議

- 進入 Phase 06-4：Expiration UI（summary、狀態群組、到期提醒視圖）。
- 將 pantry/expiration 的日期顯示統一套入 `Intl` 本地時區格式。
- 增加前端測試（slice thunk 與 page interaction）。
