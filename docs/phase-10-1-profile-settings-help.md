# Phase 10-1：Profile / Settings / Help 前端與偏好資料模型

## 範圍

本階段只實作 Profile / Settings / Help 與 `user_preferences` 偏好模型。

不包含：

- Email 寄送排程
- Email provider 串接
- Nutrition 功能
- AI worker 流程調整

## 後端

### 新增資料模型

`user_preferences` 欄位：

- `id`
- `user_id`（`unique` + `index`）
- `theme`（預設 `light-soft`）
- `timezone`（可為 `null`）
- `language`（預設 `zh-TW`）
- `expiration_email_reminder_days`（預設 `1`，允許 `none`/`1`/`3`）
- `created_at`（UTC timezone-aware）
- `updated_at`（UTC timezone-aware）

### 新增 API

- `GET /profile`
- `PATCH /profile`
- `POST /profile/change-password`
- `GET /settings`
- `PATCH /settings`

行為重點：

- 只能操作目前登入使用者資料（`user_id` 隔離）。
- `email` 僅顯示，不可修改。
- `GET /settings` 在偏好不存在時自動建立預設值。
- `PATCH /settings` 只更新 `theme/timezone/expiration_email_reminder_days`；`language` MVP 固定 `zh-TW`。

## 前端

### Profile

- 顯示頭像區，無 `avatar_url` 時使用 `display_name` 第一個字元。
- 可編輯 `display_name`。
- 顯示但不可修改 `email`。
- 修改密碼區：目前密碼、新密碼、確認新密碼。
- 三個密碼欄位都有顯示/隱藏切換按鈕（含 `aria-label`）。
- 錯誤與成功提示為繁體中文。

### Settings

區塊順序：

1. 外觀設定（主題切換）
2. 到期 Email 提醒
3. 時區
4. 語言
5. 登出所有裝置（未來功能）
6. 最近登入時間（未來功能）

到期提醒選項順序固定：

- 不提醒
- 前 1 天（預設）
- 前 3 天

本階段僅儲存偏好，不寄信。

### Help

完成繁體中文內容：

- 食材庫存基本使用
- 到期提醒說明
- 購物清單使用方式
- 食譜建議限制
- 食材辨識拍攝建議
- 到期 Email 提醒規則（含未來 8:00 / 17:00）
- FAQ

## 測試

- `python -m compileall -q backend/app`
- `python -m pytest backend/tests -q`（系統 Python 缺少 `jose`，改以 `.venv/bin/python -m pytest backend/tests -q` 驗證）
- `cd frontend && npm run build`

結果：

- backend compile：通過
- backend tests（`.venv`）：`112 passed`
- frontend build：通過

## 風險與後續

- Phase 10-1 未寄送 Email，不具提醒通知能力。
- 真正寄送排程、delivery log 去重與重試策略留在 Phase 10-2。
