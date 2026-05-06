# LLM、OCR 與 Vision AI 規範

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

文字模型：`qwen2.5:7b`，用於 AI 食譜推薦、OCR 文字整理、餐點描述整理。

Vision 模型：`qwen3-vl:8b`，用於食材照片與餐點照片內容辨識。

## 分層限制

`ChatOllama` 只能在 `backend/app/infra/llm_client.py`。OCR provider 只能在 `backend/app/infra/ocr_client.py`。API route 不可直接呼叫 LLM / OCR。Service 只能依賴 protocol / interface。

## AI 食譜推薦

輸入包含現有食材、即將過期食材、使用者選擇的食材、料理設備、料理時間、飲食偏好、過敏原。輸出包含食譜名稱、使用食材、缺少食材、步驟、時間估計、注意事項。

## OCR 匯入

上傳發票 / 收據 → OCR 擷取文字 → LLM 整理候選食材 → 使用者確認 → 寫入 pantry_items。不可直接寫入庫存。

## 食材照片辨識

上傳單一或少量食材照片 → Vision AI 候選食材 → 使用者確認名稱、數量、單位、過期日 → 寫入庫存。不做整個冰箱辨識。

## 餐點營養粗估

必須顯示：「此營養估算由 AI 粗略推測，僅供日常生活參考，不能取代專業營養師或醫療建議。」禁止宣稱精準熱量或醫療診斷。

## AI / OCR 效能注意事項

LLM、OCR、Vision 可能很慢。MVP 可同步呼叫，但需標示限制。若任務處理時間長，後續應改為 background job。

建議背景任務流程：

```text
建立 job → 回傳 job_id → worker 處理 → 前端輪詢或查詢 job 狀態 → 完成後顯示結果
```

可選工具：Celery / RQ / Dramatiq。AI 服務建議與一般 API server 分離。
