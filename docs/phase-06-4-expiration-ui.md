# Phase 06-4：Expiration UI

## 1. 階段目標

完成到期提醒前端頁面（`/expiration`），包含摘要卡片、狀態篩選、到期清單與 loading/error/empty state，並延續既有 Dashboard / Pantry 視覺與主題規則。

## 2. 完成內容

- 新增 expiration feature 型別與 Redux slice：
  - `summary`
  - `stats`（已過期 / 即將到期 / 正常 / 全部）
  - `loading`
  - `error`
  - `selectedStatusFilter`
- 新增 thunk：`fetchExpirationSummary`。
- 新增 reducers：
  - `setExpirationStatusFilter`
  - `clearExpirationError`
- `apiClient` 新增 `expirationApi.getSummary()`，統一使用 `requestWithAuth`（含 pre-refresh 與 401 retry）。
- 建立 Expiration 頁面與元件：
  - `ExpirationSummaryCards`
  - `ExpirationFilters`
  - `ExpirationItemList`
  - `ExpirationEmptyState`
- `/expiration` 路由沿用既有 `AppLayout`，Sidebar 與 TopToolbar 顯示「到期提醒」與 icon。
- 完成桌機/手機版 RWD：
  - 摘要卡片桌機橫向排列、手機改 2 欄/1 欄。
  - 列表手機版轉 card-like 顯示，保留欄位標題（`data-label`）。

## 3. API 串接說明

- 主要摘要 API：`GET /expiration/summary`
  - 回傳 `expired_count`、`expiring_soon_count`、`expired_items`、`expiring_soon_items`。
- 為了顯示「正常」與「全部」卡片統計，前端同時讀取：
  - `GET /pantry/items?page=1&page_size=1`（取得 total）
  - `GET /pantry/items?status=normal&page=1&page_size=1`（取得 normal total）
- 三個請求都透過 `requestWithAuth`，不繞過 tokenService/auth flow。

## 4. 測試方式

1. 啟動 backend。
2. `cd frontend && npm run dev`。
3. 登入後進入 `/expiration`。
4. 驗證：
   - 摘要卡片顯示（已過期/即將到期/正常/全部）
   - 狀態篩選切換（全部/已過期/即將到期/正常）
   - loading、error + retry、empty state
   - 桌機與手機版顯示
5. 建置驗證：`cd frontend && npm run build`

## 5. 已知限制

- `GET /expiration/summary` 目前不提供 normal items 清單，因此「正常」篩選僅顯示空狀態提示，不顯示 normal item 明細。
- 列表日期目前直接顯示 API 字串（`YYYY-MM-DD`）；更完整本地化顯示將於後續 UX 整理階段統一處理。
