# Phase 09-2：Vision Model 食材候選辨識（收尾）

## 目標

在既有 Phase 09-1 的 ingredient photo job-based 架構上，將 worker 從固定 mock 候選改為透過 Vision model 產生 `candidate_items`，並維持 backend 非同步、frontend 不直連 ai_server。本階段不包含前端確認 UI（Phase 09-3 才實作）。

## 本階段完成內容

1. Vision client：
- `ai_server/app/clients/ingredient_vision_client.py`
- 使用 Ollama Python client 原生 `chat` 呼叫 Vision（`llm_vision_model`）
- 讀取圖片、轉 base64、回傳 `message.content`
- 設定 `AI_VISION_TIMEOUT_SECONDS=60`

2. ingredient photo recognition service：
- `ai_server/app/services/ingredient_photo_recognition_service.py`
- 使用輕量 prompt（繁中食材名稱列舉）
- 支援「JSON optional + 文字 fallback」解析
- 文字 fallback 會轉成標準 `candidate_items` 預設欄位

3. worker ingredient_photo handler：
- `ai_server/workers/job_worker.py`
- `ingredient_photo` job 改呼叫 `IngredientPhotoRecognitionService`
- 保持 `job_type` isolation，不影響 `recipe_recommendation` 流程
- stale `running` job 逾時會標記 failed，避免永久卡住

4. result 格式維持 Phase 09-1 相容：

```json
{
  "candidate_items": [
    {
      "name": "番茄",
      "category": "蔬菜",
      "quantity": 1,
      "unit": "顆",
      "expiration_date": null,
      "storage_location": "fridge",
      "note": "AI 辨識候選，請確認"
    }
  ],
  "note": "AI 食材照片辨識結果，請使用者確認後再加入庫存。"
}
```

## 錯誤處理

- Vision 回傳非 JSON：可走文字 fallback 解析，不直接失敗。
- 缺欄位或欄位格式錯誤：job `failed`，中文錯誤訊息。
- 圖片不存在：job `failed`，中文錯誤訊息。
- 模型呼叫異常：job `failed`，中文錯誤訊息。
- timeout：`食材照片辨識逾時，請改用較清楚、單一或少量食材的照片後再試。`
- 不回傳 traceback 給使用者。

## MVP 使用範圍與限制

- 本階段主要支援「單一或少量未加工食材」照片辨識。
- 複雜場景（整桌料理、冰箱全景、多人餐點、過多品項）會增加 Vision 推論時間與 timeout 風險。
- 不建議將複雜餐點照片直接用於本階段食材庫存匯入。
- `candidate_items` 仍是 AI 候選結果，Phase 09-3 需由使用者確認後才可寫入 pantry。
- 整桌料理或餐點照片更適合後續 Nutrition 階段，非本階段主要目標。

## Ollama 資源限制補充

- `job_type` worker isolation 只隔離 process，不隔離模型推論硬體資源。
- 若 text/vision 共用同一個 `OLLAMA_BASE_URL`（或雖不同 port 但同機同 GPU/CPU），Vision 任務仍可能影響 recipe latency。
- 本地與雲端同機部署都會遇到相同問題；若要實質改善，需分開 runtime、GPU 或機器。

## 測試策略

- 單元測試全部使用 fake vision client，不呼叫真實 Ollama。
- 驗證成功解析（JSON/文字）、空內容失敗、圖片不存在、worker 不寫入 pantry_items。
- 既有 recipe worker 測試需維持通過。

## 階段結論

Phase 09-2 已接入 Vision model 的 worker-side 推論路徑，並完成 timeout/stale job 保護。仍維持 job-based 非同步流程與資料安全邊界（不直接寫入 pantry）。Phase 09-3 再完成前端候選確認與寫入流程。
