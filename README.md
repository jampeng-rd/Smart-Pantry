# 智慧食材保存與膳食管理系統（Smart Pantry & Nutritionist）

## 專案狀態

```text
Phase 01：專案初始化 ✅
Phase 02：使用者註冊 / 登入 + Refresh Token ✅
Phase 03：手動食材庫存管理 ✅
Phase 04：食材分類、過期提醒與狀態篩選 ✅
Phase 05：購物清單 ✅
Phase 06-1：Auth UI + Protected Layout ✅
Phase 06-2：Dashboard + Sidebar + Theme ✅
Phase 06-3：Pantry UI ✅
Phase 06-4：Expiration UI ✅
Phase 06-5：Shopping UI ⏳
Phase 06-6：前端整合與 UX 修正 ⏳
Phase 07：CI/CD 與部署 ⏳
Phase 08：AI 食譜推薦 ⏳
Phase 09：發票 / 收據 OCR 匯入 ⏳
Phase 10：食材照片辨識 ⏳
Phase 11：餐點營養粗估 ⏳
```

## 環境需求

Python 3.10+、Node.js 20+、Docker、PostgreSQL、Ollama（AI 階段）。

## 環境變數

請先複製 `.env.example` 為 `.env`，並填入本機設定。`.env` 不可提交到版本控制，`.env.example` 僅放範例值，不可放真實 secret。

## 後端啟動

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --reload
```

## 前端啟動

```bash
cd frontend
npm install
npm run dev
```

## Docker Compose 啟動

```bash
docker compose up --build
```

## Auth 與 Token

已完成 `register/login/refresh/logout/me`：
- Access token 預設 15 分鐘。
- Refresh token 預設 7 天。
- Refresh token 僅存 DB hash，不存明文。
- `logout` 會撤銷 refresh token，撤銷後 refresh 會失敗。

MVP 前端可使用 sessionStorage 儲存 token（有 XSS 風險）；正式環境建議 refresh token 改為 httpOnly secure cookie。

## Pantry 與 Expiration

已完成：
- `POST /pantry/items`
- `GET /pantry/items`（支援 `page/page_size/category/q/sort=expiration_date/status`）
- `PATCH /pantry/items/{item_id}`
- `DELETE /pantry/items/{item_id}`
- `GET /expiration/summary`

狀態規則：
- `expired`：`expiration_date < 今天`
- `expiring_soon`：`今天 <= expiration_date <= 今天 + 7 天`
- `normal`：其他情況，`expiration_date=null` 視為 `normal`

所有 pantry/expiration 查詢都強制綁定目前登入 `user_id`，不可跨使用者讀寫。

## Shopping List

已完成：
- `POST /shopping/items`（支援手動新增與 `source_pantry_item_id`）
- `GET /shopping/items`（支援 `page/page_size/is_purchased/q/sort`）
- `PATCH /shopping/items/{item_id}`（支援 `name/quantity/unit/is_purchased`）
- `DELETE /shopping/items/{item_id}`

資料與行為規則：
- `source_pantry_item_id` 若有提供，會驗證該 pantry item 必須存在且屬於目前登入使用者，否則回 `404`。
- `is_purchased` 由 `false -> true` 時自動寫入 `purchased_at=now`。
- `is_purchased` 由 `true -> false` 時自動清空 `purchased_at=null`。
- 所有 shopping 查詢與操作都強制 `user_id` 隔離，禁止跨使用者讀寫。
- 已購買項目目前不會自動更新 pantry；需由使用者確認後才可寫入 pantry。

## 時間與時區策略（MVP）

- 後端資料庫時間欄位統一使用 UTC（timezone-aware）儲存。
- API 回傳 datetime 為 ISO 8601，必須明確帶時區（例如 `Z` 或 `+00:00`）。
- 後端不直接儲存各地區本地時間（例如 Asia/Taipei、America/New_York）。
- 前端顯示時再轉為本地時間：Phase 06 先用瀏覽器 `Intl` API 依使用者本機時區顯示。
- 未來可在 `user_preferences` 新增 `timezone` 欄位，讓使用者覆蓋瀏覽器偵測（例如 `Asia/Taipei`、`America/New_York`、`Europe/London`、`Asia/Tokyo`）。

## 前端 UI

主要介面使用繁體中文，按鈕與導覽使用 react-icons，支援柔和亮色與柔和暗色主題。

## Phase 06-1：Auth UI + Protected Layout

已完成：
- `LoginPage`、`RegisterPage`
- `DashboardPlaceholderPage`（僅佔位，不含完整 Sidebar 功能頁）
- `tokenService`（集中管理 token 的 sessionStorage 讀寫與到期判斷）
- `authSlice`（初始化登入狀態、登入、註冊、登出、loading/error）
- `apiClient` auth 串接：`register/login/refresh/logout/me`
- route guard（未登入不可進 `/dashboard`）
- Login/Register 頁面改為互斥顯示（不會同時 render）
- 修正 `initializeAuth` 與 `login/register` 的狀態競態覆蓋
- 預設主題為 `light-soft`（無偏好時 fallback 到 `light-soft`）
- `dark-soft` 主背景改為單純柔和深色，不使用漸層
- `theme.css` 使用完整 `light-soft` / `dark-soft` token（含 surface/accent/border/semantic/shadow）
- 全域樣式改用 theme variables（card/input/button/ghost/error/divider/body）
- 按鈕圓角統一約 `10px`，與 input 風格一致
- 主題切換從登入後 header 移除，改到登入後使用者設定區塊
- 首頁 Login/Register 採單一卡片置中版型（`100vh` 置中）
- 系統名稱與英文副標題移入 auth card 內，不再獨立於卡片外
- 首頁移除主題切換與額外提示文字
- Login/Register 密碼欄位支援顯示/隱藏切換（含註冊確認密碼）
- `frontend/tsconfig.json` 已移除 deprecated `baseUrl` 設定

Route 行為：
- 未登入進入 `/`：顯示登入/註冊 UI
- 未登入進入 `/dashboard`：導回登入頁
- 登入成功：導向 `/dashboard`
- 已登入重新整理：嘗試恢復登入狀態
- 登出：清除 token 並回登入頁

## Phase 06-2：Dashboard + Sidebar + Theme

已完成：
- 正式 Dashboard 版型（`AppLayout + Sidebar + TopToolbar + Workspace`）
- Sidebar 支援 desktop 收合（`260px/84px`）與 transition 動畫
- Sidebar brand 文案簡化為「智慧食材系統 / Smart Pantry」
- 收合狀態依 theme 顯示 logo（light-soft/dark-soft），僅顯示 icon 不顯示文字，並縮小 logo 尺寸
- 收合 sidebar header 預設顯示 logo，hover/focus 才顯示展開按鈕（不常駐）
- Mobile/Tablet 改為 overlay drawer + 遮罩層，開啟時鎖定 `body` 捲動
- Sidebar 主導覽移除 Settings，保留 Dashboard/Pantry/Expiration/Shopping/Recipes/OCR/Nutrition
- Sidebar 底部使用者區與向上展開 user menu（Profile/Settings/Help/Theme Toggle/Log out）
- 收合 sidebar 的 nav/user 改為 square icon button（40x40），修正 hover/active 框外溢
- 收合 sidebar 的 user menu 改為 sidebar 內 icon-only menu（不浮到外側）
- 收合 sidebar 的 user menu 修正 x 軸 overflow，不再出現 horizontal scrollbar
- 使用者區不顯示 email，僅顯示 display_name，並預留 PRO badge（有 `subscription_tier === "PRO"` 才顯示）
- Top toolbar（頁面標題 + 搜尋框佔位 + icon-only 更多操作按鈕）
- 新增 8 個功能頁 placeholder（本階段不實作 CRUD）
- 全部 layout/card/button/input/sidebar/toolbar 以 theme variables 套用（含 hover/active/transition）


## Phase 06-3：Pantry UI

已完成：
- Pantry 專屬 Redux 狀態管理（filters/sort/page/pageSize/total/loading/error）
- Pantry API 串接（`list/create/update/remove`，統一走 `requestWithAuth`）
- Pantry 頁工具列（搜尋、分類篩選、狀態篩選、過期日排序、新增食材）
- 食材列表與操作（編輯/刪除）
- 新增/編輯 Drawer 表單（name/quantity 必填）
- 刪除前確認（`window.confirm`）
- Empty state、Loading、Error（含重試）
- Pagination（頁碼切換與 page size 切換）

測試方式：
- `cd frontend && npm run build`
- 啟動前後端後登入，進入 `/pantry` 手動測試 CRUD + 搜尋/篩選/排序/分頁。

## Phase 06-4：Expiration UI

已完成：
- Expiration 專屬 Redux 狀態管理（`summary/stats/items/page/pageSize/loading/error/selectedStatusFilter`）
- Expiration API 串接（`expirationApi.getSummary()`，統一走 `requestWithAuth`）
- 到期提醒頁（`/expiration`）摘要卡片（已過期/即將到期/正常/全部）
- 狀態篩選（全部/已過期/即將到期/正常）
- 到期提醒列表（桌機表格 + 手機 card-like），作為「所有食材到期狀態總覽」
- 到期提醒列表支援 pagination（預設每頁 10，支援 10/20/50）
- 切換 filter / pageSize 會自動回到第 1 頁
- Loading、Error + Retry、Empty state
- 延續現有 Dashboard/TopToolbar/Sidebar 樣式與 light-soft/dark-soft 主題
- 「全部」篩選會顯示 `expired + expiring_soon + normal`
- 「正常」篩選會顯示 normal 食材明細（非空白）
- 新增共用分頁元件 `components/common/Pagination`，Pantry 與 Expiration 共用

資料來源策略：
- `GET /expiration/summary`：提供 `expired/expiring_soon` 摘要計數
- `pantryApi.list({ status: "normal" })`：補齊 normal items
- 前端再合併 `expired + expiring_soon + normal` 為 unified list，供列表與篩選顯示
- 若後端未來提供完整 expiration list API，可改為單一 API 來源

測試方式：
- `cd frontend && npm run build`
- 啟動前後端後登入，進入 `/expiration` 手動測試摘要、篩選、RWD、error/retry。

## AI 功能限制

AI 食譜為生活建議；OCR / 食材照片辨識結果需由使用者確認；餐點營養估算僅供生活參考。

## 效能與擴充性

開發階段以本地 Docker PostgreSQL 為主，部署階段使用 managed PostgreSQL。列表 API 使用 pagination，常用查詢需 DB index，AI / OCR / 圖片處理 MVP 可同步呼叫，後續可改 Celery / RQ / Dramatiq background job。圖片不存 DB blob/base64；DB 只存 image_path / image_url。
