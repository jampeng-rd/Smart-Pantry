# Phase 02：使用者註冊 / 登入 + Refresh Token

## 1. 階段目標

完成使用者認證與 token 流程，包含註冊、登入、refresh、logout、me，並建立環境變數管理與 refresh token hash 儲存機制。

## 2. 完成內容

- 建立 `.env.example` 並調整 `.gitignore`（忽略 `.env`，保留 `.env.example`）。
- 建立 `users`、`refresh_tokens` SQLAlchemy model。
- 建立 `infra/security.py`：密碼 hash/verify、access/refresh token 建立與 refresh token hash。
- 建立 `AuthRepository`（DB 操作集中在 infra/repository）。
- 建立 `AuthService`（商業邏輯集中在 service）。
- 建立 `POST /auth/register`、`POST /auth/login`、`POST /auth/refresh`、`POST /auth/logout`、`GET /auth/me`。
- 建立統一 API 錯誤回應格式（`status/data/message`）。
- 新增 auth 單元測試（不依賴外部 DB 服務）。

## 3. 涉及檔案

- `.env.example`
- `.gitignore`
- `backend/app/api/auth.py`
- `backend/app/api/dependencies.py`
- `backend/app/api/error_handlers.py`
- `backend/app/services/auth_service.py`
- `backend/app/domain/models/{base.py,user_model.py,refresh_token_model.py}`
- `backend/app/domain/schemas/{auth_schema.py,common_schema.py}`
- `backend/app/infra/{settings.py,database.py,security.py}`
- `backend/app/infra/repository/auth_repository.py`
- `backend/app/main.py`
- `backend/requirements.txt`
- `backend/tests/test_auth_service.py`
- `docker-compose.yml`
- `README.md`

## 4. 如何啟動

後端：`python -m uvicorn backend.app.main:app --reload`

前端：`cd frontend && npm run dev`

Docker：`docker compose up --build`

## 5. 單元測試

全部測試：`pytest backend/tests -q`

## 6. Web UI 測試方式

1. `cd frontend && npm run dev`
2. 檢查首頁正常顯示。
3. 本階段前端尚未串接 auth 頁面，可用 API 工具測後端 auth。

## 7. API 串接說明

統一格式：
- 成功：`{"status":"success","data":...,"message":null}`
- 失敗：`{"status":"error","data":null,"message":"..."}`

Auth API：
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/me`（Authorization: `Bearer <access_token>`）

## 8. PostgreSQL 測試方式

1. `docker compose up -d smartpantry-db`
2. 設定 `.env` 的 `DATABASE_URL` 指向本機 PostgreSQL。
3. 啟動 backend 後會自動建立 `users`、`refresh_tokens` 表。
4. 可用 psql 檢查 `refresh_tokens` 僅保存 `token_hash`，不保存明文 token。

## 9. Token 流程與 revoke 流程

- Login：簽發 access token（15 分鐘）與 refresh token（7 天），並將 refresh token hash 存入 DB。
- Refresh：驗證 refresh JWT 與 DB 紀錄狀態（存在、未撤銷、未過期）後，簽發新 access+refresh，舊 refresh 標記 revoked 並記錄 replacement。
- Logout：將指定 refresh token hash 標記 revoked。
- Revoke 後 refresh 會回傳 401。

## 10. 效能與擴充性注意事項

- DB 連線：engine/session factory 已集中於 `infra/database.py`。
- Index：`users.email`、`refresh_tokens.token_hash/user_id/expires_at` 已設索引，支援快速查詢。
- 查詢風險：refresh 流量上升時，`token_hash` 查詢與撤銷更新會增加 DB 寫入壓力。
- 擴充方向：後續可加入 Alembic 管理 migration、token 黑名單快取、rate limit、防暴力登入。
- CI 風險：目前僅跑測試與前端 build，後續應補 lint/type/security scan。

## 11. 已知限制

- 尚未實作前端 auth 表單與 token 自動 refresh 流程。
- 尚未導入 Alembic migration。
- 目前 `startup` 以 `metadata.create_all` 建表，正式環境建議改為 migration 管理。

## 12. 下一階段建議

- 進入 Phase 03，實作 pantry CRUD 與 pagination。
- 建立 pantry model/repository/service/API 與單元測試。
- 在前端新增 auth UI 與 API client/tokenService 串接。
