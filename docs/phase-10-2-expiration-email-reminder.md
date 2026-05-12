# Phase 10-2：Expiration Email Reminder 後端排程與寄信服務

## 範圍

本階段完成後端到期提醒排程流程：delivery log、email abstraction、service、runner 與測試。

本階段不包含：

- 前端寄送紀錄 UI（留到 Phase 10-3）
- 真實 Email provider 串接
- Redis / Celery / RQ / Dramatiq / RabbitMQ

## 實作內容

### 1. delivery log model

新增資料表模型：`expiration_reminder_deliveries`

欄位：

- `id`
- `user_id`
- `scheduled_date`
- `send_window`（`morning_08` / `evening_17`）
- `reminder_days`（`none` / `1` / `3`）
- `item_ids`（JSON）
- `email_to`
- `status`（`pending` / `success` / `failed`）
- `sent_at`
- `error_message`
- `created_at`

限制策略：

- 同一 `user_id + scheduled_date + send_window` 若已有 `success`，本次排程略過（service 層保護）。

### 2. Email abstraction

新增：`backend/app/infra/email_client.py`

- `BaseEmailClient`
- `FakeEmailClient`
- `EmailMessage`
- `EmailSendResult`

本階段只用 fake client，會記錄寄送內容並回傳成功/失敗，不寄真信。

### 3. reminder service

新增：`backend/app/services/expiration_email_reminder_service.py`

職責：

- 讀取 `user_preferences.expiration_email_reminder_days`
- 依 `scheduled_date + reminder_days` 精準比對 `pantry_items.expiration_date`
- 建立 `pending` delivery log
- 呼叫 email client
- 更新 `success/failed` 與 `error_message`
- 防止同時段重複成功寄送

提醒規則：

- `none`：不寄
- `1`：只提醒 `expiration_date = scheduled_date + 1`
- `3`：只提醒 `expiration_date = scheduled_date + 3`

### 4. scheduler / runner

新增：`backend/app/jobs/expiration_email_runner.py`

可手動執行：

```bash
python -m backend.app.jobs.expiration_email_runner
```

可指定參數：

- `--send-window morning_08|evening_17`
- `--scheduled-date YYYY-MM-DD`

目前使用 DB polling/simple runner，不導入 queue system。

### 5. email 內容

使用純文字內容，至少包含：

- 使用者名稱
- 即將到期食材清單
- 到期日期
- 提醒設定（前 1 天 / 前 3 天）

## 測試

新增測試：

- `backend/tests/test_expiration_email_reminder_service.py`
- `backend/tests/test_expiration_email_runner.py`

覆蓋情境：

1. `none` 不寄送
2. 1 天提醒正確
3. 3 天提醒正確
4. `morning_08` duplicate protection
5. `evening_17` duplicate protection
6. fake email success
7. fake email failed
8. failed 寫入 `error_message`
9. 不跨 `user_id`
10. 無符合 items 不寄送
11. runner 可正常執行

## 風險與後續

- 本階段不寄真信，僅以 fake client 驗證流程。
- Phase 10-3 再補前端寄送紀錄 UI。
- 若未來寄送量升高，再於 Phase 11 評估 queue 系統。
