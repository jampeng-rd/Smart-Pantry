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
Phase 06-5：Shopping UI ✅
Phase 06-6A：Pantry / Shopping 前端整合 UX 修正 ✅
Phase 06-6B：前端路由與登入導向整理 ✅
Phase 06-6C：前端共用元件盤點與小幅整理 ✅
Phase 07：CI/CD 與部署 ⏳
Phase 08-0：AI Server / AI Job 架構初始化 ✅
Phase 08-1：AI 食譜推薦 Mock（ai_jobs + fake worker）✅
Phase 08-2：AI 食譜推薦 LangChain + Ollama ✅
Phase 08-3：Recipes 前端 UI 串接 ✅
Phase 09-0：AI Worker 架構調整 / job_type 隔離 ✅
Phase 09-1：食材照片辨識 Job API + Storage + Mock Worker ⏳
Phase 09-2：Vision Model 食材候選辨識 ⏳
Phase 09-3：食材辨識前端 UI + 使用者確認寫入 Pantry ⏳
Phase 10-1：營養粗估 Job API + Mock Worker ⏳
Phase 10-2：Vision/Text Model 營養粗估 ⏳
Phase 10-3：Nutrition 前端 UI + 生活參考聲明 ⏳
Phase 11：AI Queue / Worker Scaling（RQ + Redis，視需要）⏳
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
- `expiring_soon`：`今天 <= expiration_date <= 今天 + 3 天`
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
- `source_pantry_item_id` 僅作內部來源關聯，不在 UI 顯示 ID。
- 已購買 shopping item 加入 pantry 成功後，前端會自動移除原 shopping item（既有 API 組合）。

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
- 未登入進入 `/pantry`：導回登入頁
- 登入成功：導向 `/pantry`
- 註冊成功：導向 `/pantry`
- 已登入進入 `/`：自動導向 `/pantry`
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
- Sidebar 主導覽移除 Settings；MVP 目前顯示 Pantry/Expiration/Shopping/Recipes/食材辨識/Nutrition
- `/dashboard` route 保留為未來總覽頁 placeholder，MVP 側欄暫時隱藏「儀表板」導航
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


## Phase 06-5：Shopping UI

已完成：
- Shopping 專屬 Redux 狀態管理（`items/page/pageSize/total/loading/error/filters/sort`）
- Shopping API 串接（`shoppingApi.list/create/update/remove`，統一走 `requestWithAuth`）
- 購物清單頁（`/shopping`）搜尋、狀態篩選、排序
- 購物項目新增、編輯、刪除
- 標記已購買 / 設為未購買
- 共用 Pagination 分頁（預設每頁 10，支援 10/20/50）
- Loading、Error + Retry、Empty state
- Desktop table + Mobile card-like（含欄位 label）
- `purchased_at` 以瀏覽器本地時區格式化顯示
- Shopping Drawer 輸入框高度已調整為與 Pantry Drawer 一致
- Shopping 新增/編輯表單：`name`、`quantity` 必填，`quantity` 必須為整數且 >= 1（`noValidate` + 自訂繁中訊息）

測試方式：
- `cd frontend && npm run build`
- 啟動前後端後登入，進入 `/shopping` 手動測試 CRUD、篩選/排序、分頁、狀態切換。

## Phase 06-6A / 06-6B / 06-6C：前端整合與 UX 修正

已完成：
- Pantry 列表新增「加入購物清單」操作，使用既有 `shoppingApi.create()` 建立購物項目。
- Pantry -> Shopping payload 會帶入：`name`、`quantity`、`unit`、`source_pantry_item_id`。
- Pantry 成功提示不顯示 `source_pantry_item_id`，僅顯示「已加入購物清單」。
- Shopping 列表新增「加入庫存」操作，僅在已購買項目顯示。
- 「加入庫存」採 Drawer 人工確認流程（不自動寫入），預填 `name/quantity/unit`，使用者可補齊 `category/expiration_date/storage_location/note`。
- 「加入庫存」的 `category` 前端必填，空白時顯示「請輸入分類」並阻擋送出。
- 確認後呼叫既有 `pantryApi.create()` 新增 pantry item；成功後自動移除原購物清單項目。
- 新增整合成功/失敗中文提示，並維持 light/dark theme 與 mobile RWD。
- Pantry 刪除若因 shopping 關聯失敗，前端顯示友善中文提示，避免顯示原始 NetworkError。
- Pantry 新增/編輯 Drawer 的 `category` 已改為前端必填，空白時直接顯示「請輸入分類」，不送 API。
- Pantry 新增/編輯表單先做中文驗證（name/category/quantity），避免只看到後端錯誤或模糊失敗提示。
- Phase 06-6B 路由整理：登入成功、註冊成功、已登入進入首頁 `/`，皆導向 `/pantry`（食材庫存）。
- `/dashboard` 保留為未來總覽 placeholder；MVP 側欄暫時隱藏「儀表板」導航。
- 已移除不再使用的 `DashboardPlaceholderPage.tsx`（Phase 06-1 舊佔位頁）。
- 表單策略：全部使用 `noValidate` + 前端繁中錯誤訊息，不直接暴露 Pydantic 原始錯誤、NetworkError 或 fetch error。

流程限制說明：
- `source_pantry_item_id` 僅記錄 shopping 項目來源關聯，不代表自動更新 pantry。
- `source_pantry_item_id` 只作內部關聯，不在 UI 顯示 ID。
- 標記已購買僅更新 shopping item 的 `is_purchased/purchased_at`。
- 要將已購買項目加入 pantry，必須由使用者在 Drawer 中確認後手動送出；新增成功後才會移除 shopping 項目。

路由與導向（MVP）：
- 預設登入後工作頁為 `/pantry`。
- `/dashboard` 保留為未來總覽頁，現階段僅為 placeholder，不影響主流程。

共用 UX 規範（目前狀態）：
- 共用分頁元件：`frontend/src/components/common/Pagination.tsx`
- Pantry / Expiration / Shopping 預設每頁 10，支援 10 / 20 / 50。
- Pantry / Shopping Drawer 的 input 與 label spacing 保持一致。
- icon-only button 皆需 `aria-label`。
- mobile table-to-card 需顯示欄位 label，操作欄不顯示「操作」label。
- 已新增共用元件：`EmptyState`、`LoadingState`、`ErrorState`、`StatusBadge`（維持既有視覺與行為）。
- Drawer 共用骨架（例如 CommonDrawer）暫未抽離：欄位與驗證流程差異較大，本輪依 MVP 穩定優先。
- 刪除確認目前仍可能使用 `window.confirm`，後續可改共用 ConfirmModal。
- success/error 提示後續可再抽成共用 Toast/Alert 元件。

測試方式：
- `cd frontend && npm run build`

## AI 功能限制

AI 食譜為生活建議；食材照片辨識結果需由使用者確認；餐點營養估算僅供生活參考。

## AI Server / Worker 與 Job 架構（Phase 08 前置規範）

- `backend/` 是 Web API server：負責 auth、pantry、expiration、shopping、AI job API、使用者驗證與資料權限。
- `ai_server/`（或 `ai_worker`）是 AI runtime：負責 LangChain、Ollama、Vision、Nutrition 長任務。

## Phase 08-1：AI 食譜推薦 Mock（job-based）

已完成：
- `ai_worker` DB polling 可執行 `poll_once()` 與 `run_forever()`。
- worker 會 claim `pending` 的 `recipe_recommendation` job，狀態流轉為 `pending -> running -> success/failed`。
- `selected_items` 模式只使用 `input_snapshot.resolved_pantry_items` 產生 mock recipe。
- `auto_from_pantry` 模式從該使用者 pantry 選 `normal/expiring_soon`，排除 `expired`。
- 無可用食材時，job 會標記 `failed`，並回中文友善 `error_message`。
- 成功時 `result` 會寫入 `recipe_name/ingredients_used/missing_ingredients/steps/cooking_time_minutes/note`。
- frontend 仍只透過 backend 查詢 `GET /recipes/recommendation-jobs/{job_id}`，不直連 `ai_server`。
- 本階段未呼叫 Ollama、未接 LangChain。

## Phase 08-2：AI 食譜推薦 LangChain + Ollama

已完成：
- `ai_worker` 在處理 `recipe_recommendation` job 時，改由 `RecipeRecommendationService` + `OllamaRecipeLlmClient` 產生推薦結果。
- `ChatOllama` 呼叫集中在 `ai_server/app/clients/recipe_llm_client.py`，API route 與 backend service 未直接呼叫 LangChain/Ollama。
- worker 維持 job-based 非同步流程：`pending -> running -> success/failed`。
- `selected_items` 仍只使用 `input_snapshot.resolved_pantry_items`。
- `auto_from_pantry` 仍僅查 job 所屬 `user_id` 的 pantry，排除 expired。
- result 格式維持相容：`recipe_name/ingredients_used/missing_ingredients/steps/cooking_time_minutes/note`。
- LLM 回傳非 JSON、缺欄位、型別錯誤或解析失敗時，job 會 `failed` 並回中文友善錯誤訊息。
- frontend 仍沿用既有建立 job / 查詢 job API，沒有新增 frontend 直連 ai_server。
- frontend 不直接呼叫 `ai_server/`，只呼叫 backend。
- `ai_server/` 不直接暴露為一般使用者公開 API。
- backend 不同步等待 AI 推論結果。
- API route 不可直接呼叫 LangChain / ChatOllama。
- Phase 08-0 使用 DB polling worker：backend 建立 job 後立即返回，worker 另行處理並寫回資料庫。
- 本階段不是 frontend 直接呼叫 ai_server，也不是 backend 同步呼叫 ai_server 等待結果。

## Phase 08-3：Recipes 前端 UI 串接

已完成：
- `/recipes` 從 placeholder 改為可操作的 AI 食譜推薦頁。
- 前端透過 backend job API 建立/查詢任務：
  - `POST /recipes/recommendation-jobs`
  - `GET /recipes/recommendation-jobs/{job_id}`
- 支援 `recommendation_mode`：
  - `selected_items`（可從 pantry 多選食材）
  - `auto_from_pantry`（由 backend/worker 自動挑選）
- 支援表單欄位：
  - `cooking_time_minutes`（正整數驗證）
  - `cooking_tools`（逗號分隔）
  - `diet_preference`
  - `allergies`（逗號分隔）
  - `prioritize_expiring_soon`
- UI 顯示完整 job 狀態：`pending` / `running` / `success` / `failed` / `cancelled`。
- success 顯示結果欄位：
  - `recipe_name`
  - `ingredients_used`
  - `missing_ingredients`
  - `steps`
  - `cooking_time_minutes`
  - `note`
- failed 顯示中文友善錯誤，不顯示 traceback 或技術細節。
- polling 間隔約 2.5 秒；job 完成與 component unmount 都會停止 polling，避免 memory leak。

job-based 流程：
1. frontend 呼叫 backend 建立 job。
2. backend 驗證 user、整理 input、建立 `ai_jobs` 記錄，立即回 `job_id`。
3. ai_worker 背景處理 `pending` job，先改 `running` 再執行。
4. 成功寫入 `result` 與 `success`；失敗寫入 `error_message` 與 `failed`。
5. frontend 透過 backend job status API 輪詢結果。

job 狀態至少包含：`pending`、`running`、`success`、`failed`、`cancelled`。
job 查詢必須驗證 `user_id`，不可跨使用者查詢。

## Phase 08-0：AI Job 架構初始化（已完成）

已完成：
- backend 新增 `ai_jobs` 基礎資料結構（含 user/job_type/status/input_snapshot/result/error_message/時間欄位）。
- backend 新增 recipe recommendation job API：
  - `POST /recipes/recommendation-jobs`
  - `GET /recipes/recommendation-jobs/{job_id}`
- API 僅建立/查詢 job，不同步等待 AI 推論。
- `selected_items` 模式會驗證 `selected_pantry_item_ids` 皆屬於目前使用者，且不可為空。
- `auto_from_pantry` 模式本階段僅建立 job，`input_snapshot` 會標示 `pending_auto_selection=true`。
- 新增 `ai_server/ai_worker` 骨架與 DB polling loop placeholder（Phase 08-1 再接 fake handler）。

本階段限制：
- 不呼叫真實 Ollama。
- 不導入 Redis/Celery/RQ/Dramatiq/RabbitMQ。

## Phase 09-0：AI Worker 架構調整 / job_type 隔離（已完成）

已完成：
- `ai_worker` 支援依 `job_type` 過濾 pending jobs（`job_type IN (...)`）。
- `AI_WORKER_JOB_TYPES` 支援逗號分隔設定（例如 `recipe_recommendation,ingredient_photo`）。
- worker 支援 CLI：`python -m ai_server.workers.job_worker --job-types recipe_recommendation`。
- worker 啟動 log 顯示 `poll_interval`、`batch_size`、`enabled_job_types`。
- 新增測試驗證只 claim 指定 job type，且不 claim 非指定 job type。
- recipe job 既有流程維持不變（frontend 建立 job -> worker claim -> running -> success/failed）。

本階段目的：
- 避免未來 Vision 任務拖慢 `recipe_recommendation`。
- 為 Phase 09（ingredient photo）與 Phase 10（nutrition estimate）預留 worker 擴充路徑。

## AI Queue 階段策略

- Phase 08-0～08-2：使用 PostgreSQL `ai_jobs` + DB polling worker。
- Phase 08～10：不導入 Redis / Celery / RQ / Dramatiq / RabbitMQ。
- Phase 09～10：Vision / Nutrition 先共用 `ai_jobs`。
- 若任務延遲或數量增加，再進入 Phase 11。
- Phase 11 首選：RQ + Redis；備選：Dramatiq + Redis。
- RabbitMQ 暫不採用，除非未來有複雜 message routing、多服務事件流或更高階 broker 需求。

選 RQ + Redis 的原因：
- Python 生態簡單，導入成本低。
- 適合中小型 background jobs。
- 相較 Celery / RabbitMQ 組合更容易理解與維護。

## AI 相關環境變數與 Compose 規劃（本次僅文件）

建議 `.env`：

```env
AI_SERVER_HOST=0.0.0.0
AI_SERVER_PORT=8100
AI_WORKER_POLL_INTERVAL_SECONDS=5
AI_WORKER_BATCH_SIZE=1
AI_WORKER_JOB_TYPES=recipe_recommendation
AI_JOB_TIMEOUT_SECONDS=300
OLLAMA_BASE_URL=http://localhost:11434
LLM_TEXT_MODEL=qwen2.5:7b
LLM_VISION_MODEL=qwen3-vl:8b
```

docker-compose 後續規劃：
- 新增 `ai-server` 或 `ai-worker` service。
- 共用同一個 PostgreSQL。
- Phase 08～10 暫不新增 `redis` service。
- Phase 11 若導入 RQ + Redis，再新增 `redis` service。

目前設定檔策略：
- backend 與 ai_server 共用同一份 `.env`。
- backend Settings 明確支援 AI env。
- ai_server Settings 只宣告 AI worker 必要欄位，並忽略 backend/frontend 專用 env（`extra="ignore"`）。
- ai_server 不需要 frontend CORS；CORS 僅適用於 browser frontend → backend。
- 後續若部署拆分，可改為 `backend.env` 與 `ai_server.env` 分開管理。

## 效能與擴充性

開發階段以本地 Docker PostgreSQL 為主，部署階段使用 managed PostgreSQL。列表 API 使用 pagination，常用查詢需 DB index。AI/Vision 在 worker 內可同步呼叫模型，但 backend 不同步等待；Phase 08～11 先採 `ai_jobs` + DB polling worker，Phase 12 視需求升級 RQ + Redis。圖片不存 DB blob/base64；DB 只存 image_path / image_url。


## AI 階段完成門檻（Phase 08～11）

Phase 08～11 不可只完成 backend API 或 ai_worker。每個 AI 階段都必須達成「前後端完整可操作」後，才能進入下一階段。

每個 AI 階段至少需完成：

1. backend job API
2. ai_worker / LangChain / Vision 流程
3. frontend UI 與 polling
4. pending/running/success/failed 狀態 UI
5. 使用者確認流程
6. backend 測試 + frontend build
7. docs 與 README 更新
8. 手動整合驗收（backend + frontend + worker + Ollama）

frontend 不可直接呼叫 ai_server，只能透過 backend job API。
