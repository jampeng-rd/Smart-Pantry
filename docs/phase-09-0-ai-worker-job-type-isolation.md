# Phase 09-0：AI Worker 架構調整 / job_type 隔離

## 目標

在不導入 Redis/Celery/RQ/Dramatiq/RabbitMQ 的前提下，延續 PostgreSQL `ai_jobs` + DB polling 架構，讓 worker 可以依 `job_type` 過濾任務，避免未來 Vision 任務拖慢 `recipe_recommendation`。

## 本階段完成內容

1. `ai_server` settings 新增 `ai_worker_job_types`。
2. 支援 `AI_WORKER_JOB_TYPES`（comma-separated）環境變數解析。
3. worker 支援 CLI 參數 `--job-types`（逗號分隔），且優先於 env。
4. pending job claim query 改為可依 `job_type IN (...)` 過濾。
5. worker 啟動 log 顯示 `poll_interval`、`batch_size`、`enabled_job_types`。
6. 新增測試驗證 worker 只 claim 指定 `job_type`，不 claim 非指定 `job_type`。
7. 既有 `recipe_recommendation` 流程維持可運作（pending -> running -> success/failed）。

## 主要設計

- DB polling 仍是 Phase 09/10 預設方案，避免過早引入 queue 複雜度。
- 透過 `job_type` 隔離，後續可拆分 worker：
  - `recipe_recommendation` worker
  - `ingredient_photo` worker
  - `nutrition_estimate` worker
- 當 Vision/Nutrition 任務變重時，可獨立擴充對應 worker，不影響 recipe 任務延遲。

## 使用方式

### 1) 使用 env

```bash
AI_WORKER_JOB_TYPES=recipe_recommendation,ingredient_photo python -m ai_server.workers.job_worker
```

### 2) 使用 CLI（優先於 env）

```bash
python -m ai_server.workers.job_worker --job-types recipe_recommendation
```

## 測試與驗證

- 單元測試：`backend/tests/test_recipe_job_worker_mock.py`
  - `test_worker_claims_only_enabled_job_types`
  - `test_worker_does_not_claim_jobs_outside_enabled_job_types`
- 既有 recipe mock worker 測試維持通過，不呼叫真實 Ollama。

## 階段結論

Phase 09-0 完成後，架構仍維持 `ai_jobs` + DB polling，但已具備 `job_type` 隔離能力，為 Phase 09（ingredient_photo）與 Phase 10（nutrition_estimate）預先建立可擴充的 worker 路徑。Phase 11 才視實際負載評估升級正式 queue（首選 RQ + Redis）。
