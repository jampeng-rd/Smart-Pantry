# API 規格

## 統一 Response 格式

成功：`{"status":"success","data":{},"message":null}`

失敗：`{"status":"error","data":null,"message":"錯誤訊息"}`

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

### DELETE /shopping/items/{item_id}

刪除購物清單項目。

## AI

### POST /recipes/recommendations

AI 食譜推薦。

```json
{"selected_pantry_item_ids":[1,2,3],"prioritize_expiring_soon":true,"cooking_time_minutes":30,"cooking_tools":["電鍋","平底鍋"],"diet_preference":"高蛋白","allergies":["花生"]}
```

### POST /ocr/receipt/preview

上傳發票 / 收據並產生候選食材，不直接寫入庫存。圖片大小限制預設 5MB，DB 只存 image_path / image_url。

### POST /ocr/receipt/confirm

使用者確認候選食材後加入庫存。

### POST /ingredients/photo/preview

上傳單一或少量食材照片，AI 回傳候選食材，不直接寫入庫存。圖片大小限制預設 5MB，DB 只存 image_path / image_url。

### POST /nutrition/estimate

餐點營養粗估，僅供生活參考。
