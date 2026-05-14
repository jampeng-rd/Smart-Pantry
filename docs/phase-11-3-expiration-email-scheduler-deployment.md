# Phase 11-3：正式 scheduler / cron / docker deployment

## 範圍

本階段目標：將 `expiration_email_runner` 整理為可部署的自動排程執行方案。

- 每日 `08:00` 執行 `morning_08`
- 每日 `17:00` 執行 `evening_17`
- 保留手動 runner
- 不導入 Redis/Celery/RQ/Dramatiq/RabbitMQ
- 不變更 email provider 架構
- 不變更 reminder service 商業邏輯
- retry/monitoring 留到 Phase 11-4

## Runner 行為

檔案：`backend/app/jobs/expiration_email_runner.py`

支援能力：

- 不帶 `--send-window`：依排程時區當前小時自動判斷。
  - `08` -> `morning_08`
  - `17` -> `evening_17`
  - 其他時段 -> 不執行，回傳 `executed=false`
- `--send-window morning_08|evening_17`：可覆蓋自動判斷
- `--scheduled-date YYYY-MM-DD`：可指定業務日期
- 發生例外時回傳非 0 exit code
- 會輸出 summary log（含 scheduled_date/send_window/success/failed/skipped）

## 手動測試指令

```bash
# 自動判斷 send_window（需在 08 或 17 時段）
python -m backend.app.jobs.expiration_email_runner

# 明確指定上午批次
python -m backend.app.jobs.expiration_email_runner --send-window morning_08 --scheduled-date 2026-05-14

# 明確指定下午批次
python -m backend.app.jobs.expiration_email_runner --send-window evening_17 --scheduled-date 2026-05-14
```

## 部署方式 1：Linux cron

建議使用部署主機本地時區或明確設 `CRON_TZ=Asia/Taipei`。

```cron
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
CRON_TZ=Asia/Taipei

# 每天 08:00
0 8 * * * cd /srv/smart_pantry && /srv/smart_pantry/.venv/bin/python -m backend.app.jobs.expiration_email_runner --send-window morning_08 >> /var/log/smartpantry-expiration-scheduler.log 2>&1

# 每天 17:00
0 17 * * * cd /srv/smart_pantry && /srv/smart_pantry/.venv/bin/python -m backend.app.jobs.expiration_email_runner --send-window evening_17 >> /var/log/smartpantry-expiration-scheduler.log 2>&1
```

## 部署方式 2：Docker Compose scheduler service

### 本地/開發 compose（已加入）

`docker-compose.yml` 新增 `expiration-email-scheduler` service，與 backend 分離。

### production override 範例

可搭配 `docker-compose.scheduler.prod.yml`：

```bash
docker compose -f docker-compose.yml -f docker-compose.scheduler.prod.yml up -d expiration-email-scheduler
```

此 service 以簡單 shell loop 執行，每小時檢查一次：

- 小時為 `08` 時執行 `morning_08`
- 小時為 `17` 時執行 `evening_17`

## 時區與業務日期策略

- DB datetime 持續使用 UTC（timezone-aware）
- `scheduled_date` 是「業務日期」，不是 DB 儲存時區
- 排程觸發時間由部署時區控制（MVP 先固定 `Asia/Taipei`）
- `SCHEDULER_TIMEZONE` 控制 runner 自動判斷時區
- 未來若多時區用戶增加，應依 `user_preferences.timezone` 分批/分區域執行（例如每個時區各自 08:00 / 17:00 批次）

## 避免重複寄送

主要保護仍為 delivery log success 去重：

- 同一 `user_id + scheduled_date + send_window`
- 若已有 `success`，該批次跳過

此規則由 `ExpirationEmailReminderService + Repository.has_success_delivery` 保護，Phase 11-3 不改商業邏輯。

## Email provider 與 secret 注意事項

- `EMAIL_PROVIDER=fake`：測試模式，不寄真信
- `EMAIL_PROVIDER=gmail_smtp`：開發/測試/少量寄送
- `EMAIL_PROVIDER=production` + `PRODUCTION_EMAIL_PROVIDER=resend`：正式建議
- production secret（如 `RESEND_API_KEY`、Gmail app password）不可提交 git

## 不在本階段處理

- retry/backoff
- monitoring/告警
- provider 失敗追蹤強化

上述項目留到 Phase 11-4。
