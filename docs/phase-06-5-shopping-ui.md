# Phase 06-5：Shopping UI

## 1. 階段目標

完成購物清單前端頁面（`/shopping`），包含列表、搜尋/篩選/排序、新增/編輯/刪除、購買狀態切換、pagination，以及 loading/error/empty state。

## 2. 完成內容

- 新增 shopping feature 型別與 Redux slice：
  - `items`
  - `page` / `pageSize`（預設 `1 / 10`）
  - `total`
  - `loading`
  - `error`
  - `filters`（`q`、`isPurchased`）
  - `sort`（`created_at`、`name`、`purchased_at`）
- 新增 thunks：
  - `fetchShoppingItems`
  - `createShoppingItem`
  - `updateShoppingItem`
  - `deleteShoppingItem`
- 新增 reducers：
  - `setShoppingFilters`
  - `setShoppingPage`
  - `setShoppingPageSize`
  - `setShoppingSort`
  - `clearShoppingError`
- `apiClient` 新增 `shoppingApi`：
  - `list(params)`
  - `create(payload)`
  - `update(itemId, payload)`
  - `remove(itemId)`
- 建立 Shopping 頁面與元件：
  - `ShoppingFilters`
  - `ShoppingTable`
  - `ShoppingFormDrawer`
  - `ShoppingEmptyState`
- 使用共用分頁元件 `components/common/Pagination`。
- 支援購買狀態切換（已購買 / 未購買）。

## 3. API 串接說明

- `GET /shopping/items`：支援 `page`、`page_size`、`is_purchased`、`q`、`sort`
- `POST /shopping/items`
- `PATCH /shopping/items/{item_id}`
- `DELETE /shopping/items/{item_id}`

全部 API 請求都透過 `requestWithAuth`，保留 access token pre-refresh 與 401 單次重試。

## 4. 表單驗證與可及性

- `name` 必填，空白訊息：`請輸入項目名稱`
- `quantity` 必填，預設 `1`
- `quantity` 驗證：
  - 空白：`請輸入數量`
  - 非整數：`數量必須是整數`
  - `< 1`：`數量必須大於或等於 1`
- 表單使用 `noValidate`，避免瀏覽器英文 tooltip。
- 欄位使用 `aria-required`、`aria-invalid`、`aria-describedby`。

## 5. Pagination 與互動行為

- 預設每頁 10 筆，可切換 `10 / 20 / 50`。
- 切換 `filters` 或 `sort` 會回到第 1 頁。
- 切換 `pageSize` 會回到第 1 頁。
- 分頁列沿用共用 Pagination 文案與按鈕。

## 6. 測試方式

1. 啟動 backend。
2. `cd frontend && npm run dev`。
3. 登入後進入 `/shopping`。
4. 驗證：
   - 搜尋、狀態篩選、排序
   - 新增、編輯、刪除
   - 標記已購買 / 設為未購買
   - pagination 切換
   - loading/error/empty state
   - 桌機表格與手機 card-like 列表
5. 建置驗證：`cd frontend && npm run build`

## 7. 已知限制

- 後端 `sort` 目前僅支援 `created_at` / `purchased_at`；前端「名稱」排序先對當頁資料做本地排序。
- 購買時間目前直接顯示 API datetime 字串；後續可統一用 `Intl API` 做本地時區格式化。
- 刪除確認目前使用 `window.confirm`，後續可改成統一風格 modal。
