# Phase 10-3：Expiration Email Reminder 前端設定與寄送紀錄

## 概要

本階段補齊到期 Email 提醒的「查詢 API + 前端 UI」，讓使用者可在 Settings 查看提醒偏好與最近寄送紀錄。

不開新階段，僅補 UX 與資料保留規則；不串接真實 email provider。

## 後端

### 新增 API

- `GET /settings/expiration-reminder-deliveries`
- Query：`page`（預設 1）、`page_size`（預設 10，最大 50）

### 行為規則

- 僅可查詢目前登入使用者 (`user_id`) 自己的寄送紀錄。
- 依 `created_at desc, id desc` 排序（最新在前）。
- 回傳 `item_count`（`len(item_ids)`）。
- datetime 回傳為 timezone-aware ISO 字串。

### 7 天資料保留規則

- 保留條件明確定義為：`scheduled_date >= (today - 7 days)`。
- 清除條件：`scheduled_date < (today - 7 days)`。
- cleanup 只在 `morning_08` runner 執行時觸發。
- `evening_17` 不執行 cleanup，避免同一天重複清理。
- cleanup 由 service/repository 處理，不放在 API route。

## 前端

### Settings 頁面新增區塊

位置：`到期 Email 提醒` 設定下方新增 `最近寄送紀錄`。

顯示欄位：

- 排程日期
- 寄送時段（`morning_08` -> 上午 8:00、`evening_17` -> 下午 5:00）
- 提醒天數（`1` -> 前 1 天、`3` -> 前 3 天、`none` -> 不提醒）
- 食材數量
- 收件 Email
- 狀態（`success`/`failed`/`pending`）
- 寄送時間
- 錯誤訊息（failed 時顯示）

### UI 狀態

- loading
- error + 重試
- empty state（尚無寄送紀錄）
- pagination（每頁 10 筆，使用共用 `Pagination` 元件）

### RWD

- 桌機：table 顯示。
- 手機：card-like 顯示，避免嚴重橫向捲動。

## Help FAQ 更新

新增說明：

- 可在「系統設定 > 到期 Email 提醒 > 最近寄送紀錄」查看。
- 最近寄送紀錄僅保留 7 天，並在每天上午 8:00 runner 順便清理舊資料。
- Phase 10-3 仍為 fake email client，紀錄不代表真實寄出。
- 真實 email provider 留待後續 Production Infrastructure / External Services。

## 驗證

- `python -m compileall -q backend/app`
- `.venv/bin/python -m pytest backend/tests -q`
- `cd frontend && npm run build`

## 已知限制

- 尚未串接真實 Email provider。
- 尚未導入 production scheduler / cron。
- 尚未導入 Redis/Celery/RQ/Dramatiq/RabbitMQ。
