# Phase 03：手動食材庫存管理

## 1. 階段目標

完成 pantry CRUD（僅手動食材庫存），並確保每筆資料與目前登入 `user_id` 綁定，查詢支援 pagination 與基本篩選。

## 2. 完成內容

- 建立 `pantry_items` model。
- 建立 pantry schema（create/update/item/list）。
- 建立 pantry repository（新增、查詢、更新、刪除）。
- 建立 pantry service（商業邏輯與 user_id 隔離）。
- 建立 pantry API：
  - `POST /pantry/items`
  - `GET /pantry/items`
  - `PATCH /pantry/items/{item_id}`
  - `DELETE /pantry/items/{item_id}`
- `GET /pantry/items` 支援 `page/page_size/category/q/sort=expiration_date`。
- 補測試：新增、查詢、pagination、category、q、更新、刪除、未登入、跨使用者操作限制。

## 3. 涉及檔案

- `backend/app/domain/models/pantry_item_model.py`
- `backend/app/domain/models/__init__.py`
- `backend/app/domain/schemas/pantry_schema.py`
- `backend/app/infra/repository/pantry_repository.py`
- `backend/app/services/pantry_service.py`
- `backend/app/api/pantry.py`
- `backend/app/api/dependencies.py`
- `backend/app/services/auth_service.py`
- `backend/app/main.py`
- `backend/tests/test_pantry_service.py`
- `backend/tests/test_pantry_auth_dependency.py`
- `README.md`

## 4. 如何啟動

後端：`python -m uvicorn backend.app.main:app --reload`

前端：`cd frontend && npm run dev`

Docker：`docker compose up --build`

## 5. 單元測試

全部測試：`pytest backend/tests -q`

## 6. Web UI 測試方式

1. `cd frontend && npm run dev`
2. 本階段主要完成 backend pantry API，前端可於下一階段再完整串接頁面。

## 7. API 串接說明

統一回應格式：
- 成功：`{"status":"success","data":...,"message":null}`
- 失敗：`{"status":"error","data":null,"message":"..."}`

Pantry API：
- `POST /pantry/items`
- `GET /pantry/items?page=1&page_size=20&category=蔬菜&q=番茄&sort=expiration_date`
- `PATCH /pantry/items/{item_id}`
- `DELETE /pantry/items/{item_id}`

## 8. PostgreSQL 測試方式

1. `docker compose up -d smartpantry-db`
2. 設定 `.env` 的 `DATABASE_URL` 指向本機 PostgreSQL。
3. 啟動 backend 後自動建立 `pantry_items`。
4. 使用 API 建立多位使用者資料，驗證不同 `user_id` 查詢互相隔離。

## 9. pagination 設計與 user_id 隔離

- pagination：`page`（>=1）、`page_size`（1~100），repository 以 `offset + limit` 查詢。
- total：使用 `count(*)` 依相同條件（含 `user_id/category/q`）計算。
- user_id 隔離：
  - 列表查詢固定 `where user_id = current_user_id`。
  - 更新/刪除固定 `item_id + user_id` 同時比對。
  - 不存在或非本人資料一律回 404。

## 10. 效能與擴充性注意事項

- 已避免一次讀取所有使用者資料，列表強制 pagination。
- `pantry_items` 對 `user_id/category/expiration_date/name` 建索引，改善篩選效能。
- `q` 目前使用 `ilike`，資料量大時需評估 trigram/full-text index。
- 後續若加入 expiration summary，應避免 N+1 查詢並考慮快取。

## 11. 已知限制

- 尚未加入 expiration/shopping/recipes/OCR/nutrition/background job。
- 尚未有 pantry API 的端對端 HTTP 測試（目前以 service 與授權依賴測試為主）。
- 尚未做 Alembic migration（目前仍為 `create_all`）。

## 12. 下一階段建議

- 進入 Phase 04：食材過期提醒與狀態篩選。
- 在 pantry 列表新增 status 篩選（expiring_soon/expired）。
- 補前端 pantry CRUD 頁面與 API client 串接。
