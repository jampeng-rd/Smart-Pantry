# Phase 12-3：Deployment Migration / DB Upgrade 驗收

## 目標

建立 development / staging / production 一致且可執行的 migration 升級流程，並明確定義 deployment 前檢查、失敗處理、rollback 策略與 DB upgrade 驗收步驟。

## 範圍

本階段僅處理 migration 與 deployment 驗收流程文件，不變更 Phase 12-1 / 12-2 已完成的 runtime 行為與資料模型。

## 核心規範（必須遵守）

- deployment 前必須執行 `alembic upgrade head`。
- migration 失敗必須中止 deployment。
- production 不可使用 drop/recreate DB 作為升級方式。
- schema 變更正式流程一律走 Alembic migration，不可手動 `ALTER TABLE` 當作正式流程。

## Deployment 前 Migration Checklist

每次部署前都需完成下列檢查：

1. 版本與檔案檢查
   - 確認最新 migration 檔案已提交（`migrations/versions/`）。
   - 確認 `alembic heads` 僅有預期 head（避免多頭分支未處理）。
2. 設定與連線檢查
   - 確認目標環境 `DATABASE_URL` 指向正確 DB（dev/staging/prod 不可混用）。
   - 確認 `.env` 或 secret manager 已套用正確連線資訊。
3. 風險檢查
   - 確認 migration 無危險破壞性操作（尤其 `DROP TABLE`、不可逆資料刪除）。
   - 若含資料回填或長時間 DDL，先評估鎖表與停機風險。
4. 備援檢查
   - production 升級前必須完成 DB backup/snapshot。
   - 確認 rollback 路徑可執行（`alembic downgrade -1` 或 restore snapshot）。
5. 升級命令
   - 執行 `alembic upgrade head`。
6. 升級後檢查
   - 執行 `alembic current`，確認 revision 到達預期 head。
   - 啟動服務並做最小健康檢查（至少 `GET /health`）。

## Environment 差異流程

### Development

用途：本地開發與日常整合。

流程：

1. 啟動本地 PostgreSQL。
2. 設定 `.env` 的 `DATABASE_URL`。
3. 執行 `alembic upgrade head`。
4. 執行 `alembic current` 確認版本。
5. 啟動 backend 並做 smoke test（`GET /health`）。

備註：

- 若是舊開發 DB 第一次納管 Alembic，可先 `alembic stamp <baseline_revision>` 再進入正式 migration 流程。

### Staging

用途：正式部署前預演。

流程：

1. 先更新 staging 程式版本。
2. 部署流程執行 `alembic upgrade head`。
3. 若 migration 成功，再啟動或切換新版本服務。
4. 執行 API smoke test 與回歸驗收。

規則：

- staging migration 失敗時，staging 部署流程必須停止，不可帶錯誤狀態繼續上線。

### Production

用途：正式上線。

流程：

1. 建立 production DB backup/snapshot。
2. 於 deployment pipeline 執行 `alembic upgrade head`。
3. migration 成功後才可進行 app rollout。
4. rollout 後執行健康檢查與關鍵 API 驗收。

規則：

- production migration 失敗必須立即中止 deployment。
- 不可用 drop/recreate DB 當升級策略。
- 僅在明確驗證可行時執行 downgrade；高風險情境優先 restore backup。

## Migration Failure Handling

當 `alembic upgrade head` 失敗時：

1. 立即中止 deployment pipeline。
2. 保留錯誤日誌（migration revision、錯誤堆疊、SQL 錯誤碼）。
3. 確認是否有「部分成功」狀態（已套用部分 DDL/資料變更）。
4. 依風險選擇處置：
   - 可安全 downgrade：執行 `alembic downgrade -1` 或指定 revision。
   - 不可安全 downgrade：停止 rollout，改走 DB backup/snapshot restore。
5. 修正 migration 後重新部署，不可直接略過失敗 revision。

## Rollback 策略

### 原則

- rollback 不是預設手段，先判斷資料相容性與不可逆操作。
- 若 migration 含不可逆資料刪除/轉換，應以 restore backup 為主。
- downgrade 僅限已在 staging 驗證過且可安全回滾的 revision。

### 策略選擇

1. 小型、可逆 schema 變更
   - 可考慮 Alembic downgrade（例如 `alembic downgrade -1`）。
2. 高風險或不可逆變更
   - 優先使用 production backup/snapshot restore。
3. 服務層 rollback
   - 僅回滾 app 版本不足以修復 schema 問題時，不可單獨依賴 app rollback，必須搭配 DB rollback/restore 策略。

## DB Upgrade 驗收步驟

每次版本升級至少完成下列驗收：

1. Migration 狀態驗收
   - `alembic heads`
   - `alembic current`
2. 服務健康檢查
   - `GET /health` 回 200。
3. 核心功能 smoke test
   - Auth：登入/refresh 基本流程可用。
   - Pantry/Shopping：列表查詢至少可成功回應。
4. Schema 差異確認
   - 確認新欄位/新表可正常讀寫（依該次 revision 重點驗證）。
5. 失敗演練（建議至少在 staging）
   - 模擬 migration 錯誤，確認 pipeline 會中止。

## 本地可執行驗收方式（範例）

```bash
# 1) 套用 migration
alembic upgrade head

# 2) 確認目前 revision
alembic current

# 3) 啟動 backend
python -m uvicorn backend.app.main:app --reload

# 4) 健康檢查（另開終端）
curl http://127.0.0.1:8000/health
```

若 `alembic upgrade head` 任一步驟失敗：

- 立即停止後續啟動與驗收。
- 先處理 migration 問題，再重新執行完整流程。

## 驗收結論

- 已建立 deployment migration checklist。
- 已明確區分 development / staging / production 升級流程。
- 已定義 migration failure handling 與 rollback 策略。
- 已提供本地可執行 DB upgrade 驗收步驟。
- 未提前實作 Phase 13（RQ/Redis/Queue scaling）。
