# 開發階段規劃

## Phase 01：專案初始化

建立 repo、AGENTS.md、agent-docs、backend、frontend、docs、Docker Compose、PostgreSQL service、README、最小 GitHub Actions CI。

文件：`docs/phase-01-project-init.md`

## Phase 02：使用者註冊 / 登入 + Refresh Token

建立 users、refresh_tokens、註冊、登入、access token（15 分鐘）、refresh token（7 天）、refresh、logout/revoke、refresh token hash 儲存、取得目前使用者、密碼雜湊、測試。

文件：`docs/phase-02-auth-refresh-token.md`

## Phase 03：手動食材庫存管理

建立 pantry_items、新增、編輯、刪除、查看自己的食材、分類查詢、過期日排序、pagination。

文件：`docs/phase-03-pantry-crud.md`

## Phase 04：食材分類、過期提醒與狀態篩選

定義 normal、expiring_soon、expired；根據 expiration_date 計算狀態；支援狀態篩選、搜尋、Dashboard 摘要。不做自動庫存不足判斷。

文件：`docs/phase-04-expiration-status.md`

## Phase 05：購物清單

建立 shopping_list_items；手動新增、從庫存加入、標記已購買、刪除；購物清單獨立於庫存但可引用 pantry_item_id。

本階段補充規範：

- `is_purchased=true` 只記錄 `purchased_at`，不可自動寫入 pantry。
- `source_pantry_item_id` 僅為來源關聯，不是庫存同步機制。
- 若要把已購買項目加入庫存，需由使用者確認 `name`、`category`、`quantity`、`unit`、`expiration_date`、`storage_location`、`note` 後再寫入。
- 未來可新增 convert-to-pantry API，但 request 必須明確提供上述欄位。

文件：`docs/phase-05-shopping-list.md`

## Phase 06：前端完整 UI + 主題切換

React + Vite + TypeScript；Redux slices 分開；登入/註冊；自動 refresh token；Dashboard；食材頁；購物清單；react-icons；繁中 UI；柔和亮/暗主題；API 集中在 apiClient。

本階段補充規範：

- 時間顯示先用瀏覽器 `Intl API` 將 API 回傳 UTC datetime 轉為本地時間。
- 後續可新增 `user_preferences.timezone` 讓使用者覆蓋瀏覽器時區。

文件：

- `docs/phase-06-1-auth-ui.md`
- `docs/phase-06-2-dashboard-layout.md`
- `docs/phase-06-3-pantry-ui.md`
- `docs/phase-06-4-expiration-ui.md`
- `docs/phase-06-5-shopping-ui.md`
- `docs/phase-06-6-frontend-integration-ux.md`

## Phase 07：CI/CD 與部署

GitHub Actions、backend pytest、frontend build、Docker build、PostgreSQL 檢查、部署文件、CORS、環境變數、PR flow、擴充策略。

文件：`docs/phase-07-ci-cd.md`

## Phase 08-0：AI Server / AI Job 架構初始化

建立 `ai_jobs` 基礎結構、backend job API 骨架、ai_worker DB polling 流程與狀態機（pending/running/success/failed/cancelled）。

文件：`docs/phase-08-0-ai-job-architecture.md`

## Phase 08-1：AI 食譜推薦 Mock（job-based）

使用 `ai_jobs` + fake worker 完成食譜推薦非同步流程，不呼叫真實 Ollama。

文件：`docs/phase-08-1-ai-recipes-mock.md`

## Phase 08-2：AI 食譜推薦 LangChain + Ollama

在既有 job-based 架構接入 LangChain + Ollama。

文件：`docs/phase-08-2-ai-recipes-ollama.md`

## Phase 09：食材照片辨識

上傳單一或少量食材照片；圖片大小限制 5MB；開發階段可存本機 uploads/；DB 只存 image_path / image_url；Vision AI 產生候選食材；使用者確認後加入庫存；不做整個冰箱辨識。

文件：`docs/phase-09-ingredient-photo.md`

## Phase 10：Profile / Settings / Help / Expiration Email Reminder

Nutrition 暫緩，不在下一階段實作。原因是單張餐點照片難以準確推估份量、油量、醬料與熱量，容易造成使用者誤解。Phase 10 改為補齊 Profile、Settings、Help 與到期 Email 提醒。

文件：`docs/phase-10-profile-settings-help-email-reminder.md`

## Phase 11：AI Queue / Worker Scaling（視需要）

當 job 延遲與數量增加，再由 DB polling 升級正式 queue。

- 首選：RQ + Redis
- 備選：Dramatiq + Redis
- Celery + RabbitMQ：僅在複雜 routing、多服務事件流或更高階 broker 需求時評估

文件：`docs/phase-11-ai-queue-worker-scaling.md`

## AI Queue 策略補充

- Phase 08-0～08-2：使用 PostgreSQL `ai_jobs` + DB polling worker，不導入 Redis / Celery / RQ / Dramatiq / RabbitMQ。
- Phase 09～10：若 DB polling worker 可接受，持續沿用，Vision/Nutrition 共用 `ai_jobs`。
- 任務量與延遲明顯上升時才進入 Phase 11 升級。

## Phase 06 子階段規劃

### Phase 06-1：Auth UI + Protected Layout

內容：

- Login/Register UI
- tokenService
- auth guard
- 登入前首頁
- 登入後導向 Pantry（`/pantry`）

文件：

- docs/phase-06-1-auth-ui.md

### Phase 06-2：Dashboard + Sidebar + Theme

內容：

- Dashboard Layout
- Sidebar
- collapsible sidebar
- 使用者選單
- light-soft / dark-soft theme
- Toolbar layout
- `/dashboard` 保留為未來總覽頁（目前 placeholder）

文件：

- docs/phase-06-2-dashboard-layout.md

### Phase 06-3：Pantry UI

內容：

- pantry CRUD UI
- pagination
- search/filter/sort
- drawer/modal form

文件：

- docs/phase-06-3-pantry-ui.md

### Phase 06-4：Expiration UI

內容：

- expiration summary cards
- expired/expiring_soon UI
- status filter

文件：

- docs/phase-06-4-expiration-ui.md

### Phase 06-5：Shopping UI

內容：

- shopping list UI
- purchase state UI
- shopping -> pantry UX flow

文件：

- docs/phase-06-5-shopping-ui.md

### Phase 06-6：UX 修正與整合

內容：

- loading/error UX
- timezone display
- responsive layout
- accessibility
- mobile/tablet polish

文件：

- docs/phase-06-6-frontend-integration-ux.md

## Phase 08：AI 食譜推薦完整功能

### Phase 08-0：AI Server / AI Job 架構初始化

建立 ai_jobs、backend job API、ai_worker skeleton。

### Phase 08-1：AI 食譜推薦 Mock Worker

使用 fake worker 驗證 job-based 流程。

### Phase 08-2：AI 食譜推薦 LangChain + Ollama

worker 改用 LangChain + Ollama 產生推薦結果。

### Phase 08-3：Recipes 前端 UI 串接

完成：

- Recipes 頁面
- 建立 recommendation job
- frontend polling
- pending/running/success/failed UI
- result 顯示
- 中文友善錯誤
- selected_items / auto_from_pantry UI
- 不直連 ai_server

完成標準：backend + worker + frontend UI + 手動驗收皆完成。

## Phase 09：食材照片辨識完整功能

### Phase 09-1：Ingredient Photo Job API + Mock Worker

### Phase 09-2：Vision Model 食材辨識

### Phase 09-3：Ingredient Photo 前端 UI + 使用者確認寫入 Pantry

## Phase 10：Profile / Settings / Help / Expiration Email Reminder

### Phase 10-0：Phase 10 文件與方向調整

暫緩 Nutrition，更新 AGENTS.md、README.md、agent-docs/*。

### Phase 10-1：Profile / Settings / Help 前端與偏好資料模型

完成 Profile、Settings、Help 頁面；Settings 第一項為主題切換；到期 Email 提醒設定順序為不提醒、前 1 天（預設）、前 3 天。

### Phase 10-2：Expiration Email Reminder 後端排程與寄信服務

建立 user_preferences/reminder 設定、delivery log、email client abstraction、scheduler/worker。每天上午 8:00 與下午 5:00 檢查並寄送。

### Phase 10-3：Expiration Email Reminder 前端設定與寄送紀錄

完成提醒設定 UI、寄送狀態/說明、錯誤提示與 Help 文件。

## Phase 09-0：AI Worker 架構調整 / job_type 隔離

- worker 可依 job_type 過濾任務
- 避免 Vision 任務拖慢 recipe_recommendation
- 可用 env 或 CLI 指定 worker 處理的 job types
- 暫不導入 Redis / Celery / RQ / Dramatiq / RabbitMQ

補充：

- `job_type` 隔離是 worker process 層級，不是 Ollama runtime/GPU 隔離。
- 若 `OLLAMA_TEXT_BASE_URL` / `OLLAMA_VISION_BASE_URL` 留空，會 fallback 到 `OLLAMA_BASE_URL`，text/vision 共用同一 runtime。
- 本地或雲端只要同機共用 CPU/GPU/RAM/VRAM，Vision 推論仍可能拖慢 recipe。
- Phase 11 的 queue/scaling（RQ + Redis）重點是提升任務調度與擴充能力；若要解決模型互搶，仍需 runtime/硬體分離。

收據 OCR 暫不列入 MVP，未來若能取得商品明細再評估。
