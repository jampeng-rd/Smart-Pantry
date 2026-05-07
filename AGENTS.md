# Smart Pantry & Nutritionist 專案 Codex 工作規範

## 1. 專案定位

本專案正式中文名稱：**智慧食材保存與膳食管理系統**。英文名稱：**Smart Pantry & Nutritionist**。

本專案是全端 MVP，目標是建立智慧食材庫存、過期提醒、購物清單與 AI 膳食輔助系統。

核心順序：先完成人工手動輸入、庫存 CRUD、過期提醒、購物清單、繁體中文 Web UI，再逐步加入 AI 食譜推薦、發票 / 收據 OCR 匯入、食材照片辨識、餐點營養粗估。

系統包含：`backend/` FastAPI、`frontend/` React + Vite + TypeScript + Redux Toolkit、PostgreSQL、Docker Compose、GitHub Actions、`docs/`、`agent-docs/`。

## 2. Codex 必須遵守的總規則

1. 每次任務開始前，先閱讀本檔案與 `agent-docs/`。
2. 後端必須分層：API Layer → Service Layer → Domain Layer → Infra Layer。
3. 不同功能必須分檔：auth、pantry、expiration、shopping、recipes、ocr、nutrition 不可混在同一 route/service。
4. 前端不同功能必須分 feature：auth、pantry、expiration、shopping、recipes、ocr、nutrition、theme。
5. 前端 UI 主要語言必須是繁體中文。
6. 前端按鈕需優先使用 `react-icons`；純 icon button 要有 `aria-label`；列表/導覽/選項使用「icon + 繁體中文」。
7. 前端必須支援柔和亮色與柔和暗色主題切換，不使用純白 `#ffffff` 或純黑 `#000000` 當主要背景。
8. Auth 必須使用 access token + refresh token；access token 快過期時前端自動 refresh，避免使用者突然被強制登出。
9. Python 函式、類別、重要方法都要有繁體中文 docstring。
10. TypeScript 公開函式、service、slice、重要工具函式要有繁體中文註解。
11. 後端每個功能都要有可單獨執行的單元測試。
12. 每階段完成後建立或更新 `docs/phase-xx-*.md`，並同步更新 README。
13. Python 套件只能安裝在 `.venv`，禁止全域安裝。
14. v1 資料庫必須使用 PostgreSQL，不用 SQLite 作主要資料庫。
15. 開發階段以本地 Docker PostgreSQL 為主；部署階段再使用 managed PostgreSQL。
16. AI 結果不可直接信任；涉及寫入資料庫的 OCR / 圖片辨識結果必須由使用者確認。
17. 餐點營養估算僅供生活參考，不可宣稱精準或專業營養診斷。
18. 文件需記錄效能與擴充性風險：DB 連線、pagination、索引、AI 任務延遲、背景任務、水平擴充。

## 3. 建議專案目錄

```text
backend/app/api/{health,auth,pantry,expiration,shopping,recipes,ocr,nutrition}.py
backend/app/services/{auth_service,pantry_service,expiration_service,shopping_service,recipe_service,ocr_import_service,nutrition_service}.py
backend/app/domain/{schemas,models,enums}.py
backend/app/infra/{database,repository,settings,security,llm_client,ocr_client,storage}.py
frontend/src/app/{store,hooks}.ts
frontend/src/features/{auth,pantry,expiration,shopping,recipes,ocr,nutrition,theme}/
frontend/src/services/{apiClient,tokenService}.ts
frontend/src/styles/{theme.css,globals.css}
```

## 4. Auth 與 Token 規範

- Access token 預設 15 分鐘。
- Refresh token 預設 7 天。
- 後端提供 `POST /auth/refresh` 與 `POST /auth/logout`。
- Refresh token 必須儲存在 DB 中的 `refresh_tokens`，且只儲存 token hash，不儲存明文 token。
- `refresh_tokens` 至少包含：`token_hash`、`user_id`、`expires_at`、`revoked_at`、`created_at`、`replaced_by_token_id`。
- Refresh token 必須支援 revoke / logout。
- 前端 MVP 可使用 `sessionStorage` 儲存 access token / refresh token。
- `sessionStorage` 關閉分頁後會清除，但仍有 XSS 風險，文件必須標示安全限制。
- 正式環境建議 refresh token 改用 `httpOnly secure cookie`。
- 前端 request 前檢查 access token 是否快過期；若快過期，先 refresh。
- 若 API 回傳 401，最多 refresh 一次並重送原 request。
- Refresh 失敗才清除登入狀態並導回登入頁。

## 4.1 時間與時區策略

- 後端與 DB 一律使用 UTC timezone-aware datetime。
- API datetime 回傳必須帶 `Z` 或 `+00:00`。
- 不在後端儲存使用者本地時間（例如 Asia/Taipei、America/New_York）。
- 前端顯示時再依瀏覽器 timezone 或未來 `user_preferences.timezone` 轉換成本地時間。
- Phase 06 MVP 先使用瀏覽器 `Intl API` 顯示本地時間。

## 5. 圖片與檔案儲存規範

- 不可把圖片 blob 或 base64 直接存入 PostgreSQL。
- 開發階段可先將圖片存入本機 `uploads/` 目錄。
- PostgreSQL 只存 `image_path` 或 `image_url`。
- 上傳圖片大小限制預設為 5MB。
- 圖片上傳後可進行壓縮、resize 或格式轉換，以降低儲存與傳輸成本。
- 正式環境使用 object storage，例如 AWS S3、Cloudflare R2、MinIO 或相容服務。
- OCR / Vision 的候選結果可用 JSON / JSONB 儲存，但大型圖片內容不可放入 DB。

## 6. AI / OCR 效能規範

- MVP 階段 AI / OCR / Vision 可先同步呼叫。
- 若任務處理時間長、超時或阻塞 API，後續必須改為 background job。
- Background job 可使用 Celery / RQ / Dramatiq。
- 建議流程：建立 job → 回傳 `job_id` → worker 處理 → 前端輪詢或查詢 job 狀態。
- AI 服務後續可與一般 API server 分離，避免 LLM 推論阻塞一般 CRUD API。

## 7. LangChain 與 AI 套件規範

- AI 階段使用 LangChain 1.x 系列。
- 建議使用：`langchain>=1.0,<2.0`、`langchain-core>=1.0,<2.0`、`langchain-ollama>=1.0,<2.0`。
- Codex 實作時需以當時 pip 可安裝且相容的版本為準。
- LLM client 必須封裝在 `backend/app/infra/llm_client.py`。
- API route 不可直接 import 或呼叫 LangChain / ChatOllama。
- Service 層只能依賴 protocol / interface，不可直接依賴 LangChain 類別。

## 8. 效能與穩定性規範

MVP 可先以單一 backend instance + 本地 Docker PostgreSQL 運作，但需保留擴充可能：

- 所有列表 API 必須支援 pagination。
- 查詢需使用 user_id 條件與必要索引。
- DB engine / session factory 集中管理，不可每次 request 重新建立 engine。
- 可水平擴充 backend。
- 部署階段 DB 使用 managed PostgreSQL。
- 可用 Redis cache 熱門 Dashboard summary。
- 加入 rate limit，避免大量請求造成服務阻塞。

## 9. 購物清單與庫存關係規範

- `pantry_items` 代表目前庫存。
- `shopping_list_items` 代表購物清單。
- `source_pantry_item_id` 只表示購物項目來源於某筆庫存項目，不代表自動更新庫存。
- 標記 `is_purchased=true` 只記錄 `purchased_at`。
- 不可自動寫入 `pantry_items`。
- 若要把已購買項目加入庫存，必須由使用者確認 `name`、`category`、`quantity`、`unit`、`expiration_date`、`storage_location`、`note` 後才可寫入。
- 未來可新增 convert-to-pantry API，但 request 必須明確提供上述欄位。

## 10. 前端 UI 架構與 Dashboard 規範

- Web UI 必須是一個完整系統，而不是單獨頁面集合。
- 未登入使用者進入網站時，首頁必須先顯示登入 / 註冊頁。
- 使用者登入成功後才可進入 Dashboard。
- Dashboard 採用「左側 Sidebar + 右側 Workspace」版型。

### Sidebar 規範

Sidebar 需包含：
- 最上方 Logo。
- Logo 右側需有 Sidebar 收合按鈕（icon button）。
- 中間為功能導覽區：Dashboard、Pantry、Expiration、Shopping、Recipes、OCR、Nutrition、Settings。
- 底部固定顯示目前登入使用者。

### 使用者選單規範

點擊 Sidebar 底部使用者區塊後：
- 需在側邊欄內向上展開使用者選單。
- 第一列顯示目前登入使用者。
- 下方至少包含：
  - Profile
  - Settings
  - Help
  - Log out

### Workspace 規範

- Dashboard 右側為主要工作區。
- Workspace 最上方需有當前頁面工具列（page toolbar / action bar）。
- Toolbar 可放搜尋、篩選、新增按鈕、排序等頁面功能。

## 11. 前端實作階段拆分

Phase 06 不可一次做完整前端。必須拆分子階段：

- Phase 06-1：Auth UI + App Layout
- Phase 06-2：Dashboard + Sidebar + Theme
- Phase 06-3：Pantry UI
- Phase 06-4：Expiration UI
- Phase 06-5：Shopping UI
- Phase 06-6：前端整合與 UX 修正

每個子階段都需：
- 可單獨測試
- 更新 docs
- 更新 README
- 維持 frontend build 可通過
