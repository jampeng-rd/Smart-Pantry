# Phase 05：購物清單（Shopping List）

## 1. 階段目標

完成 shopping list MVP 後端功能，支援手動新增、從 pantry item 加入、列表查詢（含 pagination / 篩選 / 搜尋 / 排序）、更新與刪除，並確保嚴格 user_id 資料隔離。

## 2. 完成內容

- 新增 `shopping_list_items` 資料模型。
- 新增 shopping schema：create / update / item data / list data。
- 新增 shopping repository，封裝 DB 查詢與 `count(*)`。
- 新增 shopping service，集中商業邏輯：
  - `source_pantry_item_id` 所屬驗證
  - `is_purchased` 與 `purchased_at` 自動同步
  - 使用者資料隔離
- 新增 shopping API：
  - `POST /shopping/items`
  - `GET /shopping/items`
  - `PATCH /shopping/items/{item_id}`
  - `DELETE /shopping/items/{item_id}`
- 全部回應格式符合 `agent-docs/api.md`：
  - 成功：`{"status":"success","data":{},"message":null}`
  - 失敗：`{"status":"error","data":null,"message":"錯誤訊息"}`
- 時間欄位統一改為 UTC timezone-aware（`users`、`refresh_tokens`、`pantry_items`、`shopping_list_items`）。
- API datetime 回傳為 ISO 8601，明確帶時區（`Z` 或 `+00:00`）。

## 3. 涉及檔案

- `backend/app/domain/models/shopping_list_item_model.py`
- `backend/app/domain/models/__init__.py`
- `backend/app/domain/schemas/shopping_schema.py`
- `backend/app/infra/repository/shopping_repository.py`
- `backend/app/services/shopping_service.py`
- `backend/app/api/shopping.py`
- `backend/app/api/dependencies.py`
- `backend/app/main.py`
- `backend/tests/test_shopping_service.py`
- `backend/tests/test_shopping_auth_dependency.py`
- `README.md`
- `docs/phase-05-shopping-list.md`

## 4. 如何啟動

後端：`python -m uvicorn backend.app.main:app --reload`

前端：`cd frontend && npm run dev`

Docker：`docker compose up --build`

## 5. 單元測試

全部測試：`pytest backend/tests -q`

本階段新增測試涵蓋：
- 手動新增 shopping item 成功
- 從 pantry item 加入成功
- `source_pantry_item_id` 不存在失敗
- `source_pantry_item_id` 屬於其他使用者失敗
- 查詢自己的 shopping list
- pagination
- `is_purchased` 篩選
- `q` 搜尋
- `is_purchased=true` 時自動設定 `purchased_at`
- `is_purchased=false` 時清空 `purchased_at`
- 更新成功
- 刪除成功
- 未登入不可操作（授權依賴）
- 不可查詢、更新、刪除其他使用者資料

## 6. API 測試方式

1. 先註冊並登入取得 access token。
2. 設定 Header：`Authorization: Bearer <access_token>`。
3. 測試新增：
   - `POST /shopping/items` body：`{"name":"牛奶","quantity":1,"unit":"瓶"}`
   - 或加入 `source_pantry_item_id`。
4. 測試列表：
   - `GET /shopping/items?page=1&page_size=20`
   - `GET /shopping/items?is_purchased=true`
   - `GET /shopping/items?q=牛奶`
   - `GET /shopping/items?sort=purchased_at`
5. 測試更新：
   - `PATCH /shopping/items/{item_id}` body：`{"is_purchased":true}`
   - 再測 `{"is_purchased":false}`
6. 測試刪除：
   - `DELETE /shopping/items/{item_id}`

## 7. PostgreSQL 測試方式

1. 啟動 DB：`docker compose up -d smartpantry-db`
2. 確認 `.env` 的 `DATABASE_URL` 指向 PostgreSQL。
3. 啟動後端後使用兩個不同使用者建立資料。
4. 驗證：
   - 各自 `GET /shopping/items` 只看得到自己的項目。
   - 嘗試更新或刪除其他使用者 `item_id`，應回 `404`。
   - 帶 `source_pantry_item_id` 指向他人 pantry item 應回 `404`。

## 8. pagination / count 設計

- `GET /shopping/items` 使用 `offset + limit`：
  - `offset = (page - 1) * page_size`
  - `limit = page_size`
- `page >= 1`、`page_size` 限制 `1~100`。
- `total` 使用 DB `count(*)`，不在 Python 端讀全量資料計算。
- 查詢條件（`is_purchased`、`q`）會同步套用在資料查詢與 count 查詢。

## 9. user_id 隔離方式

- API 透過 access token 解析 `current_user_id`。
- 所有 shopping 查詢固定帶 `user_id` 條件：
  - 列表：`where shopping_list_items.user_id = current_user_id`
  - 單筆更新/刪除：`item_id + user_id` 雙條件查詢
- `source_pantry_item_id` 驗證同樣必須 `pantry_items.user_id = current_user_id`。

## 10. 已知限制

- 目前僅完成後端 API，尚未實作完整 shopping 前端頁面。
- `sort` 目前提供 `created_at` 與 `purchased_at`，尚未擴充升冪/降冪參數。
- 目前仍採 `Base.metadata.create_all`，正式環境建議改 Alembic migration。
- 目前僅記錄購物完成狀態，不會自動把 shopping item 寫入 pantry item。

## 11. 購物完成後流程（保留設計）

- `is_purchased=false`：尚未購買，保留在購物清單。
- `is_purchased=true`：已購買，記錄 `purchased_at`（UTC timezone-aware）。
- 已購買後，Phase 06 前端可提示「是否加入或更新庫存？」。
- 寫入 `pantry_items` 前必須由使用者確認：`name`、`quantity`、`unit`、`expiration_date`、`storage_location`。
- 本階段不自動更新 pantry，避免實際購買數量、單位、保存期限與儲存位置錯誤。

## 12. 時間與時區策略

- 後端與 API 一律以 UTC 作為標準時間。
- 資料庫不直接儲存地區時間（例如台灣、美國、日本、英國本地時間）。
- 前端顯示時再依使用者瀏覽器時區轉換成本地時間（Phase 06 先用 `Intl` API）。
- 未來可在 `user_preferences` 新增 `timezone` 欄位，讓使用者手動覆蓋瀏覽器時區。

## 13. TODO（後續 API）

- 後續可新增 `POST /shopping/items/{item_id}/convert-to-pantry`。
- request 必須明確提供：`name`、`category`、`quantity`、`unit`、`expiration_date`、`storage_location`、`note`。
- 不可直接把 shopping item 原值自動寫入 pantry。

## 14. 下一階段建議

- 實作 Phase 06 前端完整 UI（含 shopping 操作流程與主題整合）。
- 新增 shopping API 整合測試（FastAPI TestClient + 測試資料庫）。
- 依實際使用情況補 `shopping_list_items` 複合索引（例如 `user_id + created_at`）。
