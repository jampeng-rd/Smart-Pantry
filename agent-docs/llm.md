# LLM 與 Vision AI 規範

## 核心原則

優先使用本機 Ollama 已下載模型。不使用雲端付費 LLM API 作為預設流程。AI 結果不可直接寫入正式資料，必須經使用者確認。

## LangChain 版本

AI 階段使用 LangChain 1.x 系列。

建議套件：

```text
langchain>=1.0,<2.0
langchain-core>=1.0,<2.0
langchain-ollama>=1.0,<2.0
```

Codex 實作時需以當時 pip 可安裝且相容的版本為準。

## 模型

文字模型：`qwen2.5:7b`，用於 AI 食譜推薦、餐點描述整理。

Vision 模型：`qwen3-vl:8b`，用於食材照片與餐點照片內容辨識。

## 分層限制

`ChatOllama` 只能在 `backend/app/infra/llm_client.py`。Vision provider 只能在 `backend/app/infra/ingredient_client.py`。API route 不可直接呼叫 LLM。Service 只能依賴 protocol / interface。

AI server 分工補充：

- frontend 不可直接連 `ai_server`，只透過 backend job API。
- backend 不可同步等待 LLM/Vision 任務完成。
- `ai_server/ai_worker` 可在背景任務內同步呼叫 Ollama（單一 job 執行期間），但整體流程仍是 job-based 非同步 API。

## AI 食譜推薦

輸入包含現有食材、即將過期食材、使用者選擇的食材、料理設備、料理時間、飲食偏好、過敏原。輸出包含食譜名稱、使用食材、缺少食材、步驟、時間估計、注意事項。

## 食材照片辨識

上傳單一或少量食材照片 → Vision AI 候選食材 → 使用者確認名稱、數量、單位、過期日 → 寫入庫存。不做整個冰箱辨識。

## 餐點營養粗估

必須顯示：「此營養估算由 AI 粗略推測，僅供日常生活參考，不能取代專業營養師或醫療建議。」禁止宣稱精準熱量或醫療診斷。

## AI 效能注意事項

LLM、Vision 可能很慢。Phase 08 起採 job-based API，backend 不同步等待；AI worker 內可同步執行模型推論。

Ollama runtime 與 worker 隔離注意：

- `job_type` worker isolation 只隔離「DB claim 與 process」，不是模型推論硬體隔離。
- 若 `OLLAMA_TEXT_BASE_URL` / `OLLAMA_VISION_BASE_URL` 留空，會 fallback 到 `OLLAMA_BASE_URL`，text/vision 仍共用同一個 Ollama runtime。
- 即使模型不同（例如 `qwen2.5:7b` 與 `qwen3-vl:8b`），共用同一台機器與同一張 GPU/CPU 時，Vision 任務仍可能拖慢 recipe latency。
- 本地可先用不同 port 分流 runtime（例如 `11434` 與 `11435`），但若同機同 GPU，仍可能互相影響。
- 真正隔離需分開 GPU 或分開機器（例如 `ollama-text.internal` / `ollama-vision.internal`）。

建議背景任務流程：

```text
建立 job → 回傳 job_id → worker 處理 → 前端輪詢或查詢 job 狀態 → 完成後顯示結果
```

Phase 13 queue/scaling 規劃以 RQ + Redis 為評估方向。AI 服務建議與一般 API server 分離。

階段策略：

- Phase 08-0～08-2：PostgreSQL `ai_jobs` + DB polling worker。
- Phase 09～12：延用同一 `ai_jobs` 架構（Vision/Nutrition）。
- Phase 13：首選升級 RQ + Redis；RabbitMQ 暫不採用，除非未來需要複雜 message routing 或多服務事件流。

Recipe recommendation 食材來源策略（Phase 08 起）：

- `selected_items`：使用者手動挑選 `selected_pantry_item_ids`，backend 建立 job 時需做 `user_id` 權限驗證。
- `auto_from_pantry`：後續 worker 自動挑選「可烹煮」食材，本階段僅保留模式，不直接把全部 pantry items 當可烹煮候選。
- 後續自動挑選應排除明顯不適合料理的項目（例如飲料、零食、保健品、調味品、已過期食材）。

## Phase 09-0：AI Worker 架構調整 / job_type 隔離

- worker 可依 job_type 過濾任務
- 避免 Vision 任務拖慢 recipe_recommendation
- 可用 env 或 CLI 指定 worker 處理的 job types
- 暫不導入 Redis / Celery / RQ / Dramatiq / RabbitMQ
