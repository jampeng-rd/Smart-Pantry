# PostgreSQL 與資料庫規範

## 開發與部署資料庫策略

- 開發階段以本地 Docker PostgreSQL 為主。
- 部署階段再使用 managed PostgreSQL，例如 Render PostgreSQL、Railway PostgreSQL、AWS RDS。
- 不使用 SQLite 作為主要資料庫。

## Migration 規範（Phase 12-1）

- 導入 Alembic migration system（`alembic.ini` + `migrations/`）。
- 建立 baseline migration 對齊目前已存在 schema。
- 後續 schema 變更必須新增 migration（新增欄位/索引/資料表/約束）。
- 不可再以手動 `ALTER TABLE` 作為正式流程。
- deployment 流程需納入 `alembic upgrade head`。

## Docker Compose service

```yaml
services:
  smartpantry-db:
    image: postgres:16
    environment:
      POSTGRES_DB: smartpantry_db
      POSTGRES_USER: smartpantry_user
      POSTGRES_PASSWORD: smartpantry_password
    ports: ["5432:5432"]
    volumes:
      - smartpantry_postgres_data:/var/lib/postgresql/data
volumes:
  smartpantry_postgres_data:
```

本地開發環境變數範例：

```env
DATABASE_URL=postgresql+psycopg://smartpantry_user:smartpantry_password@localhost:5432/smartpantry_db
```

Docker Compose 內後端連 DB 可使用 service name：

```env
DATABASE_URL=postgresql+psycopg://smartpantry_user:smartpantry_password@smartpantry-db:5432/smartpantry_db
```

## 建議資料表

## 時間與時區策略

- 後端與 DB 一律使用 UTC timezone-aware datetime。
- 不在 DB 儲存使用者本地時間。
- API 輸出 datetime 需帶 `Z` 或 `+00:00`，前端再轉本地時區顯示。

### users

id、email unique indexed、password_hash、display_name、created_at、updated_at。

### refresh_tokens

id、user_id indexed、token_hash unique indexed、expires_at indexed、revoked_at nullable、created_at、replaced_by_token_id nullable。

規則：

- 只存 refresh token hash，不存明文 token。
- refresh token 預設 7 天。
- 支援 revoke / logout。
- `created_at`、`expires_at`、`revoked_at` 使用 UTC timezone-aware datetime。

### password_reset_tokens（Phase 12-2）

建議欄位：

- id
- user_id indexed
- token_hash unique indexed
- expires_at indexed
- used_at nullable
- created_at
- request_ip nullable（可選）
- request_user_agent nullable（可選）

規則：

- 只存 reset token hash，不存明文 token。
- token 過期、已使用、錯誤需視為無效 token。
- reset password 成功後需標記 `used_at` 並撤銷使用者既有 refresh tokens。

### pantry_items

id、user_id indexed、name indexed、category indexed、quantity、unit、expiration_date indexed、storage_location、note、created_at、updated_at。

`created_at`、`updated_at` 使用 UTC timezone-aware datetime。

### shopping_list_items

id、user_id indexed、source_pantry_item_id nullable、name、quantity、unit、is_purchased indexed、purchased_at nullable、created_at、updated_at。

規則：

- `source_pantry_item_id` 僅代表資料來源，不代表自動回寫 pantry。
- `is_purchased=true` 只記錄 `purchased_at`（UTC timezone-aware）。
- 不可自動把 shopping item 寫入 `pantry_items`。
- 若要轉入 pantry，必須由使用者確認 `name`、`category`、`quantity`、`unit`、`expiration_date`、`storage_location`、`note`。
- `source_pantry_item_id` 為內部關聯欄位，前端 UI 不顯示該 ID。
- 目前 MVP 為前端整合流程：`pantryApi.create()` 成功後再 `shoppingApi.remove()` 移除原購物項目（未新增 convert API）。

### user_preferences

id、user_id unique indexed、theme、timezone、language、expiration_email_reminder_days、created_at、updated_at。

規則：

- `expiration_email_reminder_days` 建議值：`none`、`1`、`3`，預設 `1`（到期前 1 天提醒）。
- Settings 偏好建議放在 `user_preferences` 或獨立一對一偏好表，不建議直接塞在 `users` auth 表。
- `theme` 可保存柔和亮色 / 柔和暗色；若前端仍用 localStorage，後續可同步到後端。
- `timezone` 可保存使用者指定時區；未設定時前端可使用瀏覽器時區。
- `language` MVP 固定繁體中文，可先保留欄位。



Phase 10-1 實作預設：

- `theme` 預設 `dark-soft`。
- `language` 預設 `zh-TW`。
- `expiration_email_reminder_days` 預設 `1`。
- `timezone` 允許 `null`，前端可 fallback 瀏覽器時區或 `Asia/Taipei`。

### expiration_reminder_deliveries（Phase 10-2 已實作）

id、user_id indexed、scheduled_date indexed、send_window、reminder_days、item_ids json/jsonb、email_to、status、sent_at、error_message、created_at。

規則：

- `send_window` 建議固定值：`morning_08`、`evening_17`。
- 同一使用者、同一天、同一 send_window 只能成功寄送一次，避免重複寄信。
- 系統每天上午 8:00 與下午 5:00 檢查每位使用者的提醒設定與即將到期食材。
- delivery logs 保留最近 7 天，清除條件定義為 `scheduled_date < (today - 7 days)`。
- cleanup 僅在 `morning_08` runner 執行；`evening_17` 不執行 cleanup，避免同日重複清理。
- `expiration_email_reminder_days=none` 的使用者不寄送。
- Email delivery log 必須可追蹤成功、失敗與錯誤原因。
- 本階段使用 fake email client 測試流程，不寄真信。

### recipe_recommendations

id、user_id indexed、model、input_snapshot json/jsonb、recommendation_text、created_at indexed。

### ai_jobs（Phase 08 起）

建議欄位：

- id
- user_id
- job_type
- status
- input_snapshot JSON/JSONB
- result JSON/JSONB 或 result_text
- error_message
- created_at
- started_at
- finished_at
- updated_at

`job_type` 建議 enum/固定值：

- `recipe_recommendation`
- `ingredient_photo`
- `nutrition_estimate`

`status` 至少包含：

- `pending`
- `running`
- `success`
- `failed`
- `cancelled`

索引建議：

- `user_id`
- `status`
- `job_type`
- `created_at`
- `(user_id, created_at)`
- `(status, created_at)`

規則：

- backend 建立 job 時先寫入 `pending` 並立即回傳 `job_id`，不可同步等待 AI 推論結果。
- worker 先將 job 狀態改為 `running` 後執行，完成後寫入 `success/failed` 與結果/錯誤訊息。
- job 查詢必須驗證 `user_id`，禁止跨使用者讀取。

### receipt_imports / ingredient_photo_imports

id、user_id indexed、image_path 或 image_url、raw_ocr_text 或 candidate_items json/jsonb、status indexed、created_at indexed。

圖片本體不得以 blob / base64 存在 PostgreSQL。

### meal_logs / nutrition_estimates

餐點紀錄與營養粗估。

## 圖片儲存規範

- 不把圖片 blob / base64 存 PostgreSQL。
- 開發階段可先存本機 `uploads/`。
- DB 只存 image_path / image_url。
- 上傳圖片大小限制預設 5MB。
- 可壓縮、resize 或轉換格式後再保存。
- 正式環境使用 S3 / R2 / MinIO 等 object storage。

## Repository 規範

API layer 不可直接操作資料庫。Service 透過 repository。DB session / connection 放在 `infra/database.py`，環境變數放在 `infra/settings.py`。

## 效能規範

- 所有使用者資料查詢帶 user_id。
- pantry_items 建 user_id、expiration_date、category 索引。
- shopping_list_items 建 user_id、is_purchased 索引。
- 列表 API 必須 pagination。
- 大型 JSON 只用於 AI snapshot / candidate，不作主要查詢欄位。

## Phase 09-0：AI Worker 架構調整 / job_type 隔離

- worker 可依 job_type 過濾任務
- 避免 Vision 任務拖慢 recipe_recommendation
- 可用 env 或 CLI 指定 worker 處理的 job types
- 暫不導入 Redis / Celery / RQ / Dramatiq / RabbitMQ
