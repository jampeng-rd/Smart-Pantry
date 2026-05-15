# Phase 14-1：Admin 權限與會員管理基礎

## 目標

完成 admin 權限資料模型、第一個 admin 建立方式、admin 專用 API 基礎，以及前端「會員管理」最小可操作版本。

## 本階段完成內容

1. Admin 權限資料模型
   - 新增 `users.is_admin` 欄位。
   - 由 Alembic migration 管理，不手動改 DB。

2. 第一個 admin 建立方式
   - 實作 `python -m backend.app.jobs.bootstrap_admin` 命令。
   - 可將既有 `jampeng.rd@gmail.com` 設為 admin。
   - 支援空 DB 建立第一個 admin（`--create-if-not-exists`）。

3. Backend admin API 基礎
   - 新增獨立 `backend/app/admin_api/`。
   - 新增 admin guard：`get_current_admin_user_id`。
   - 新增會員列表 API：`GET /admin/members`。

4. Frontend 會員管理入口
   - Sidebar 新增「會員管理」導航（僅 admin 可見）。
   - 新增 `/admin/members` 頁面。
   - 頁面支援載入中、錯誤、空狀態、會員列表與分頁。

## Alembic Migration

- revision：`20260515_1401`
- down_revision：`20260515_0010`
- 檔案：`migrations/versions/20260515_1401_admin_role_and_members_api.py`

升級：

```bash
alembic upgrade head
```

## Admin Bootstrap 操作

### 1) 既有帳號設為 admin

```bash
python -m backend.app.jobs.bootstrap_admin --email jampeng.rd@gmail.com
```

### 2) 空 DB 建立第一個 admin

```bash
python -m backend.app.jobs.bootstrap_admin \
  --email first-admin@example.com \
  --create-if-not-exists \
  --password 'change-me-strong-password' \
  --display-name '第一位管理員'
```

## API 摘要

### GET /admin/members

- 僅 admin 可使用。
- Query：`page`（預設 1）、`page_size`（預設 20，上限 100）。
- 回傳：會員列表、分頁資訊、總筆數。
- 非 admin：`403`。

## 測試

已補齊並通過：

- `backend/tests/test_admin_member_service.py`
  - admin 權限驗證
  - 非 admin 拒絕
  - admin 查會員列表
  - 初始 admin 建立（既有帳號升級 + 空 DB 建立）
- `backend/tests/test_admin_members_api.py`
  - admin dependency 拒絕非 admin
  - 會員列表 route 回應
- `backend/tests/test_auth_service.py`
  - 既有 auth 流程回歸（含 `is_admin` 欄位相容）
- frontend build：`cd frontend && npm run build`

## 邊界確認

- 本階段未實作 Phase 14-2～14-6。
- Billing runtime（`/billing/upgrade`、藍新 one-time/subscription）尚未開始。
- Phase 13（AI Queue / Worker Scaling）定位不變。
