# API 規格

## 統一 Response 格式

成功：`{"status":"success","data":{},"message":null}`

失敗：`{"status":"error","data":null,"message":"錯誤訊息"}`

## 時間欄位規範

- API datetime 欄位使用 ISO 8601，且必須帶時區資訊（`Z` 或 `+00:00`）。
- 後端時間標準為 UTC timezone-aware datetime。
- 不回傳無時區的 datetime 字串，避免前端誤判為本地時間。

## Auth

### POST /auth/register

註冊使用者。

```json
{"email":"user@example.com","password":"password123","display_name":"PG"}
```

### POST /auth/login

登入並取得 access token 與 refresh token。Access token 預設 15 分鐘，refresh token 預設 7 天。

Response data：

```json
{"access_token":"jwt-access-token","refresh_token":"jwt-refresh-token-or-cookie-mode","token_type":"bearer","expires_in":900}
```

### POST /auth/refresh

使用 refresh token 更新 access token。Refresh token 後端只儲存 hash，需支援 revoke / logout。

```json
{"refresh_token":"jwt-refresh-token"}
```

### POST /auth/logout

登出並使 refresh token 失效。

### GET /auth/me

取得目前登入使用者。

## Pantry

### POST /pantry/items

新增食材。

```json
{"name":"雞蛋","category":"蛋類","quantity":10,"unit":"顆","expiration_date":"2026-05-20","storage_location":"fridge","note":"全聯購買"}
```

### GET /pantry/items

取得目前使用者食材列表。必須支援 pagination。

```text
category=蔬菜&status=expiring_soon&sort=expiration_date&q=番茄&page=1&page_size=20
```

### PATCH /pantry/items/{item_id}

更新食材。

### DELETE /pantry/items/{item_id}

刪除食材。

## Expiration

### GET /expiration/summary

取得過期提醒摘要。

```json
{"expiring_soon_count":3,"expired_count":1,"expiring_soon_items":[],"expired_items":[]}
```

## Shopping

### POST /shopping/items

新增購物清單項目。

```json
{"name":"牛奶","quantity":1,"unit":"瓶","source_pantry_item_id":12}
```

### GET /shopping/items

取得購物清單。

### PATCH /shopping/items/{item_id}

更新購物清單項目，例如標記已購買。

規則：

- `is_purchased=true` 時只記錄 `purchased_at`。
- 不可自動寫入 `pantry_items`。
- `source_pantry_item_id` 僅作來源關聯，不應作為 UI 顯示資訊。

### DELETE /shopping/items/{item_id}

刪除購物清單項目。

### （未來）POST /shopping/items/{item_id}/convert-to-pantry

- 本 API 目前不在 MVP 必做範圍。
- 若未來新增，request 必須明確提供：`name`、`category`、`quantity`、`unit`、`expiration_date`、`storage_location`、`note`。
- 不可直接使用 shopping item 原值自動寫入 pantry。

## 前端現行整合流程（不新增 API）

- Pantry -> Shopping：使用既有 `POST /shopping/items`，帶入 `name/quantity/unit/source_pantry_item_id`。
- Shopping（已購買）-> Pantry：使用既有 `POST /pantry/items`，由使用者確認欄位後送出。
- Pantry 新增成功後，前端再呼叫既有 `DELETE /shopping/items/{item_id}` 移除原購物項目。

## AI

Phase 08 起改為 job-based API。frontend 只呼叫 backend，backend 建立 job 後立即回應，不同步等待 AI 結果。

### POST /recipes/recommendation-jobs

建立食譜推薦任務。

```json
{"selected_pantry_item_ids":[1,2,3],"prioritize_expiring_soon":true,"cooking_time_minutes":30,"cooking_tools":["電鍋","平底鍋"],"diet_preference":"高蛋白","allergies":["花生"]}
```

request 補充：

- `recommendation_mode` 必填：`selected_items` 或 `auto_from_pantry`
- `selected_items` 模式必須提供 `selected_pantry_item_ids`，且不可為空
- `selected_pantry_item_ids` 必須屬於目前使用者（backend 建立 job 前驗證）
- `auto_from_pantry` 模式本階段只建立 job，不立即做自動挑選

建立 job 回應（範例）：

```json
{"job_id":"uuid-or-int","status":"pending","created_at":"2026-05-09T12:00:00Z"}
```

### GET /recipes/recommendation-jobs/{job_id}

查詢任務狀態。必須驗證 user_id，使用者不可查詢他人的 job。

查詢 job 回應欄位：

- `status`
- `result`
- `error_message`
- `created_at`
- `started_at`
- `finished_at`

規則：

- `pending/running` 時 `result` 可為 `null`。
- `failed` 時需回傳可理解錯誤訊息，不可暴露 raw traceback。
- job 查詢需驗證 `user_id`，不可跨使用者讀取。

### （未來可類推）POST /ingredients/photo/jobs

上傳食材照片並建立 Vision job，不直接寫入庫存。

### （未來可類推）GET /ingredients/photo/jobs/{job_id}

查詢食材照片辨識 job 狀態與結果。

### （未來可類推）POST /nutrition/estimate-jobs

建立營養粗估 job，僅供生活參考。

### （未來可類推）GET /nutrition/estimate-jobs/{job_id}

查詢營養粗估 job 狀態與結果。

## AI Job API 共通規則

Phase 08～11 AI 功能統一採 job-based API：

- POST 建立 job
- GET 查詢 job status/result
- backend 建立 job 後立即回傳
- frontend 只呼叫 backend
- job 查詢必須驗證 user_id
- pending/running 時 result 可為 null
- failed 必須回中文友善 error_message
- 不可暴露 traceback
