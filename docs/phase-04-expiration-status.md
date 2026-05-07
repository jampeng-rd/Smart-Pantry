# Phase 04：食材分類、過期提醒與狀態篩選

## 1. 階段目標

完成 pantry 狀態計算（normal / expiring_soon / expired）、狀態篩選，以及 dashboard 用的過期提醒摘要 API。

## 2. 完成內容

- 定義 pantry item 狀態：`normal`、`expiring_soon`、`expired`。
- 擴充 `GET /pantry/items` 支援 `status` 篩選。
- 新增 expiration 模組：
  - `backend/app/api/expiration.py`
  - `backend/app/services/expiration_service.py`
  - `backend/app/domain/schemas/expiration_schema.py`
- 新增 `GET /expiration/summary`。
- repository 新增：
  - status 條件查詢
  - status count（DB count）
  - status 限制筆數查詢
- 所有查詢都限制 `current_user_id`。

## 3. 涉及檔案

- `backend/app/domain/schemas/pantry_schema.py`
- `backend/app/domain/schemas/expiration_schema.py`
- `backend/app/infra/repository/pantry_repository.py`
- `backend/app/services/pantry_service.py`
- `backend/app/services/expiration_service.py`
- `backend/app/api/pantry.py`
- `backend/app/api/expiration.py`
- `backend/app/api/dependencies.py`
- `backend/app/main.py`
- `backend/tests/test_expiration_service.py`
- `README.md`

## 4. 狀態規則

- `expired`：`expiration_date < 今天`
- `expiring_soon`：`今天 <= expiration_date <= 今天 + 7 天`
- `normal`：其他情況
- `expiration_date = null` 視為 `normal`

## 5. 如何啟動

後端：`python -m uvicorn backend.app.main:app --reload`

前端：`cd frontend && npm run dev`

Docker：`docker compose up --build`

## 6. 單元測試

全部測試：`pytest backend/tests -q`

## 7. API 測試方式

- Pantry list with status：
  - `GET /pantry/items?status=expired`
  - `GET /pantry/items?status=expiring_soon`
  - `GET /pantry/items?status=normal`
- Expiration summary：
  - `GET /expiration/summary`
  - 可用 `limit` 限制清單筆數（預設 10，最多 50）

統一回應格式：
- 成功：`{"status":"success","data":...,"message":null}`
- 失敗：`{"status":"error","data":null,"message":"..."}`

## 8. PostgreSQL 測試方式

1. `docker compose up -d smartpantry-db`
2. 設定 `.env` 的 `DATABASE_URL` 指向本機 PostgreSQL。
3. 以不同使用者新增 pantry items。
4. 驗證：
   - `GET /pantry/items` 僅回自己的資料
   - `GET /expiration/summary` count 與 items 只計算自己的資料

## 9. pagination / count 設計

- `GET /pantry/items` 維持 pagination：`page`、`page_size`，使用 `offset + limit`。
- `total` 由 DB `count(*)` 計算，不在 Python 讀完整資料後計算。
- `/expiration/summary` 的 count 由 DB `count(*)` 計算。
- `/expiration/summary` 的 items 以 `limit` 限制（預設 10）。

## 10. user_id 隔離方式

- API 透過 access token 取得 `current_user_id`。
- pantry/expiration 所有查詢固定加上 `where user_id = current_user_id`。
- 任何狀態計算與 summary 僅在該 user 資料集合內進行。

## 11. 已知限制

- 尚未實作前端完整 expiration dashboard 頁面。
- `q` 搜尋目前使用 `ilike`，大量資料時應評估全文索引策略。
- 目前仍使用 `create_all`，正式環境建議改 Alembic migration。

## 12. 下一階段建議

- 進入 Phase 05：購物清單（shopping list）功能。
- 連動過期/即將過期食材到購物清單建議。
- 補 API 整合測試與前端最小操作頁。 
