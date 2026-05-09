# Phase 08-0：AI Server / AI Job 架構初始化

## 1. 階段目標

建立 AI job-based 基礎架構，先完成 backend job API、`ai_jobs` 資料結構與 `ai_server/ai_worker` 骨架；本階段不實作真實 AI 食譜推薦，不呼叫 Ollama。

## 2. 完成內容

### 2.1 backend / ai_server 分工

- `backend/`：Web API server，負責使用者驗證、資料權限、建立/查詢 AI job。
- `ai_server/ai_worker`：背景 worker runtime，負責後續長任務執行（本階段僅骨架）。
- frontend 只呼叫 backend，不直接呼叫 ai_server。

### 2.2 ai_jobs 資料模型

新增 `ai_jobs` 欄位：
- `id`
- `user_id`
- `job_type`
- `status`
- `input_snapshot`
- `result`
- `result_text`
- `error_message`
- `created_at`
- `started_at`
- `finished_at`
- `updated_at`

`job_type`：
- `recipe_recommendation`
- `receipt_ocr`
- `ingredient_photo`
- `nutrition_estimate`

`status`：
- `pending`
- `running`
- `success`
- `failed`
- `cancelled`

索引：
- `user_id`
- `status`
- `job_type`
- `created_at`
- `(user_id, created_at)`
- `(status, created_at)`

### 2.3 job-based API（recipe）

- `POST /recipes/recommendation-jobs`
  - 需登入。
  - 建立 `pending` job，立即回傳 `job_id/status/created_at`。
  - 不呼叫 AI、不等待 worker。
- `GET /recipes/recommendation-jobs/{job_id}`
  - 需登入。
  - 僅能查詢自己的 job（`user_id` 隔離）。
  - 回傳 `status/result/error_message/created_at/started_at/finished_at`。

### 2.4 recipe input 模式（本階段已支援 schema 與 snapshot）

- `recommendation_mode = "selected_items"`
  - 需提供 `selected_pantry_item_ids`。
  - backend 建立 job 前驗證 item 是否都屬於目前使用者。
  - 空陣列會回傳可理解錯誤。
- `recommendation_mode = "auto_from_pantry"`
  - 本階段只建立 job，不做自動挑選與推論。
  - `input_snapshot` 以 `pending_auto_selection=true` 標示後續由 worker 處理。

`input_snapshot` 內容包含：
- `recommendation_mode`
- `selected_pantry_item_ids`
- `resolved_pantry_items`
- `pending_auto_selection`
- `prioritize_expiring_soon`
- `cooking_time_minutes`
- `cooking_tools`
- `diet_preference`
- `allergies`

## 3. ai_worker（DB polling）骨架

新增 `ai_server/`：
- `ai_server/app/main.py`
- `ai_server/app/infra/settings.py`
- `ai_server/workers/job_worker.py`
- `ai_server/requirements.txt`
- `ai_server/Dockerfile`

本階段 worker 僅提供 polling loop 與設定讀取：
- `AI_WORKER_POLL_INTERVAL_SECONDS`
- `AI_WORKER_BATCH_SIZE`
- `AI_JOB_TIMEOUT_SECONDS`

## 4. 佇列策略

- Phase 08-0～08-2：PostgreSQL `ai_jobs` + DB polling worker。
- Phase 08～11：不導入 Redis/Celery/RQ/Dramatiq/RabbitMQ。
- Phase 08-1 才做 AI 食譜推薦 Mock。
- Phase 08-2 才接 LangChain + Ollama。
- Phase 12 才評估升級 RQ + Redis。

## 5. 測試

新增 `backend/tests/test_recipe_job_service.py`，覆蓋：
- selected_items 建立 job 與 `pending` 狀態。
- selected_items 權限驗證與空陣列錯誤。
- auto_from_pantry 建立 `pending` job。
- input_snapshot 記錄 recommendation_mode。
- 查詢自己 job 成功、跨使用者查詢失敗。
- status 回應欄位格式。

## 6. 注意事項

- 本階段沒有呼叫真實 Ollama。
- 後續 worker 在 `auto_from_pantry` 模式不可直接把全部 pantry items 視為可烹煮食材，需做可烹煮篩選與狀態檢查。
