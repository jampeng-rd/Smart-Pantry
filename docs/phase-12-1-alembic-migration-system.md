# Phase 12-1：Alembic Migration System

## 目標

導入正式 migration 流程，讓後續 schema 變更一律透過 Alembic 管理，不再依賴手動 `ALTER TABLE` 或啟動時自動建表。

## 本階段完成內容

1. 新增 Alembic 基礎結構
   - `alembic.ini`
   - `migrations/`
   - `migrations/env.py`
   - `migrations/script.py.mako`

2. 連接既有 SQLAlchemy metadata
   - `migrations/env.py` 使用 `backend.app.domain.models.Base.metadata` 作為 `target_metadata`。
   - migration DB URL 透過 `backend.app.infra.settings.get_settings().database_url` 取得，與 backend 共用同一組設定來源。

3. 建立 baseline migration
   - `migrations/versions/20260514_1201_baseline_schema.py`
   - baseline 對齊目前既有主要資料表與索引：
     - `users`
     - `refresh_tokens`
     - `pantry_items`
     - `shopping_list_items`
     - `user_preferences`
     - `ai_jobs`
     - `expiration_reminder_deliveries`

4. 啟動流程調整
   - `backend.app.infra.database.init_database()` 改為不執行 `create_all`，避免繞過 migration。
   - schema 建置責任改由 `alembic upgrade head` 負責。

## 本地驗證流程

### 前置條件

- PostgreSQL 可連線
- `.env` 已設定 `DATABASE_URL`
- `.venv` 已安裝 `backend/requirements.txt`（含 Alembic）

### 驗證步驟

1. 套用 migration：

```bash
alembic upgrade head
```

2. 確認目前 revision：

```bash
alembic current
```

預期可看到 `20260514_1201`。

3. 啟動後端並檢查基本 API：

```bash
python -m uvicorn backend.app.main:app --reload
```

可用 `GET /health` 驗證服務可正常啟動。

### 既有資料庫（已存在資料表）對齊方式

若現有開發資料庫已由舊流程建立資料表，第一次導入 Alembic 時不可直接 `upgrade head`，應先把目前 schema 標記為 baseline：

```bash
alembic stamp 20260514_1201
```

完成 `stamp` 後，後續 schema 變更一律透過新的 migration revision 執行。

## 後續規範

- 後續任何 schema 變更都必須新增 Alembic revision。
- 不可再把手動 `ALTER TABLE` 當作正式流程。
- Phase 12-2 才會處理 forgot password / reset password 相關資料表，本階段不包含該內容。
