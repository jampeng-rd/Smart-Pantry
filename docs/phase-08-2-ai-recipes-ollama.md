# Phase 08-2：AI 食譜推薦 LangChain + Ollama

## 1. 階段目標

在 Phase 08-0/08-1 的 job-based 架構上，將 recipe recommendation 的 worker 處理從 mock 改為 LangChain + Ollama，並維持：
- backend 建立 job 後立即回 `job_id`
- frontend 只查 backend，不直連 ai_server
- API route 不直接 import/call LangChain 或 ChatOllama

## 2. 架構與分層

- `backend/`：維持既有 `POST /recipes/recommendation-jobs` 與 `GET /recipes/recommendation-jobs/{job_id}`，不做同步 AI 推論。
- `ai_server/workers/job_worker.py`：負責 polling、claim pending job、狀態流轉與錯誤寫回。
- `ai_server/app/services/recipe_recommendation_service.py`：封裝 prompt 組裝、JSON 解析、欄位驗證。
- `ai_server/app/clients/recipe_llm_client.py`：封裝 `ChatOllama` 呼叫（唯一 Ollama 入口）。

## 3. Worker 流程

1. `poll_once()` 依 `batch_size` claim `pending + recipe_recommendation` job，改為 `running`。
2. 依模式準備食材：
- `selected_items`：只使用 `input_snapshot.resolved_pantry_items`
- `auto_from_pantry`：僅查 `job.user_id` 的 pantry，挑 `normal/expiring_soon`，排除 expired
3. 呼叫 `RecipeRecommendationService.recommend()`：
- 組 JSON-only prompt
- 呼叫 `OllamaRecipeLlmClient`（LangChain + ChatOllama）
- 解析並驗證結果欄位
4. 成功：寫 `success + result + finished_at`
5. 失敗：寫 `failed + 中文 error_message + finished_at`

## 4. 相容結果格式

成功時 `result` 維持與 Phase 08-1 相容：
- `recipe_name`
- `ingredients_used`
- `missing_ingredients`
- `steps`
- `cooking_time_minutes`
- `note`

## 5. 錯誤處理策略

若 Ollama 回傳：
- 非 JSON
- 缺欄位
- 欄位型別錯誤
- 空內容或不合理值（如 `cooking_time_minutes <= 0`）

則 job 會標記 `failed`，並回中文友善訊息；不回 traceback。

## 6. 測試

新增/更新測試（皆不呼叫真實 Ollama）：
- `backend/tests/test_recipe_recommendation_service.py`
  - 成功解析合法 JSON
  - 非 JSON 失敗
  - 缺欄位失敗
- `backend/tests/test_recipe_job_worker_mock.py`
  - selected_items success
  - auto_from_pantry success
  - 無可用食材 failed（中文錯誤）
  - 不跨 user 使用 pantry
  - LLM 回傳非 JSON 時 failed（中文錯誤）

## 7. 限制與後續

- 本階段仍使用 PostgreSQL `ai_jobs` + DB polling worker。
- 未導入 Redis/Celery/RQ/Dramatiq/RabbitMQ。
- frontend 無新增直連 ai_server 行為。
- 後續可在 Phase 12 再評估 queue 升級與 retry/timeout 策略強化。
