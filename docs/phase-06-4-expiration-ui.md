# Phase 06-4：Expiration UI

## 1. 階段目標

完成到期提醒前端頁面（`/expiration`），定位為「所有食材的到期狀態總覽」，包含摘要卡片、狀態篩選、到期清單與 loading/error/empty state，並延續既有 Dashboard / Pantry 視覺與主題規則。

## 2. 完成內容

- 新增 expiration feature 型別與 Redux slice：
  - `summary`
  - `stats`（已過期 / 即將到期 / 正常 / 全部）
  - `items`（合併後 unified list）
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
- Expiration 頁 filter 語意：
  - 全部：顯示 `expired + expiring_soon + normal`
  - 已過期：僅顯示 `expired`
  - 即將到期：僅顯示 `expiring_soon`
  - 正常：僅顯示 `normal`
- 完成桌機/手機版 RWD：
  - 摘要卡片桌機橫向排列、手機改 2 欄/1 欄。
  - 列表手機版轉 card-like 顯示，保留欄位標題（`data-label`）。

## 3. API 串接說明

- 主要摘要 API：`GET /expiration/summary`
  - 回傳 `expired_count`、`expiring_soon_count`、`expired_items`、`expiring_soon_items`。
- 為了補齊完整列表（特別是 normal items），前端另外依狀態讀取 pantry：
  - `GET /pantry/items?status=expired&page=...&page_size=100`
  - `GET /pantry/items?status=expiring_soon&page=...&page_size=100`
  - `GET /pantry/items?status=normal&page=...&page_size=100`
- 前端會分頁抓取各狀態所有資料並合併為 unified list。
- Summary 卡片計算：
  - `已過期`：來自 `summary.expired_count`
  - `即將到期`：來自 `summary.expiring_soon_count`
  - `正常`：來自 normal items 數量
  - `全部`：`已過期 + 即將到期 + 正常`
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

- `GET /expiration/summary` 目前僅提供 expired/expiring_soon 明細；normal items 由 `pantryApi.list({ status: "normal" })` 補齊。
- 若後端未來提供完整 expiration list API，可改為單一 API 來源並減少前端合併邏輯。
- 列表日期目前直接顯示 API 字串（`YYYY-MM-DD`）；更完整本地化顯示將於後續 UX 整理階段統一處理。
