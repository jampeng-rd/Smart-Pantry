# Phase 08-1：AI 食譜推薦 Mock（job-based）

## 1. 階段目標

在 Phase 08-0 `ai_jobs` 架構上，完成：
- backend 建立 recipe job
- `ai_worker` DB polling claim pending job
- mock handler 寫回 `success` 或 `failed`
- backend 查詢 API 可讀取狀態與結果

本階段不呼叫 Ollama、不接 LangChain、不導入 Redis/Celery/RQ/Dramatiq/RabbitMQ。

## 2. Worker Mock 流程

`ai_server/workers/job_worker.py` 已完成：

1. `poll_once()`：
- 依 `ai_worker_batch_size` 查詢 `pending + recipe_recommendation`
- claim 成 `running` 並寫入 `started_at`
- 逐筆交由 `_process_recipe_job()` 處理

2. `_process_recipe_job()`：
- `selected_items`：只用 `input_snapshot.resolved_pantry_items` 產生結果，不重查其他資料
- `auto_from_pantry`：從該 `job.user_id` 的 pantry 抓 `normal/expiring_soon`，排除 `expired`
- 成功：`status=success`、寫入 `result`、`finished_at`
- 失敗：`status=failed`、寫入中文 `error_message`、`finished_at`
- 非預期例外：只記錄 server log，回給使用者固定中文錯誤，不暴露 traceback

3. `run_forever()`：
- 以 `ai_worker_poll_interval_seconds` 持續輪詢。

## 3. Mock Result 欄位

`result` 至少包含：
- `recipe_name`
- `ingredients_used`
- `missing_ingredients`
- `steps`
- `cooking_time_minutes`
- `note`

## 4. Backend 查詢行為

`GET /recipes/recommendation-jobs/{job_id}`：
- `pending/running`：`result = null`
- `success`：`result` 有 mock 內容
- `failed`：`error_message` 有中文友善訊息

## 5. 測試覆蓋

新增 `backend/tests/test_recipe_job_worker_mock.py`：
- selected_items job 可處理為 `success`
- auto_from_pantry job 可處理為 `success`
- auto_from_pantry 無可用食材時 `failed`
- failed 帶中文 `error_message`
- 不跨 user 取 pantry 資料
- worker 模組不含 Ollama 呼叫字樣

## 6. 效能與擴充風險

- DB polling 在任務量提高時會增加查詢頻率與 DB 負載。
- 目前單 worker + 小 batch 適合 MVP；高併發需評估 worker 水平擴充。
- 後續需補強：job timeout/retry、任務去重、更細緻索引與監控。
- Phase 12 再評估升級 RQ + Redis。

