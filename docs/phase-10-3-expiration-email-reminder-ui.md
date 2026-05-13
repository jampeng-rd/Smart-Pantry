# Phase 10-3：Expiration Email Reminder 前端設定與寄送紀錄

## 概要

本階段補齊到期 Email 提醒的「查詢 API + 前端 UI」，讓使用者可在 Settings 查看提醒偏好與最近寄送紀錄。

不變更 Phase 10-2 核心寄送邏輯，不串接真實 email provider。

## 後端

### 新增 API

- `GET /settings/expiration-reminder-deliveries`
- Query：`page`（預設 1）、`page_size`（預設 10，最大 50）

### 行為規則

- 僅可查詢目前登入使用者 (`user_id`) 自己的寄送紀錄。
- 依 `created_at desc, id desc` 排序（最新在前）。
- 回傳 `item_count`（`len(item_ids)`）。
- datetime 回傳為 timezone-aware ISO 字串。

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
- pagination（每頁 10 筆，上一頁 / 下一頁）

### RWD

- 桌機：table 顯示。
- 手機：card-like 顯示，避免嚴重橫向捲動。

## Help FAQ 更新

新增說明：

- 可在「系統設定 > 到期 Email 提醒 > 最近寄送紀錄」查看。
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
