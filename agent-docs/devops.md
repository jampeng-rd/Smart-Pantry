# DevOps、PR 與 CI/CD 規範

## 目標

```text
feature branch → PR → CI → merge → CD
```

## PR 流程

建立 feature branch → 完成功能 → 補測試 → 階段文件 → README → 本地測試 → push → PR → CI 通過 → merge → 部署平台自動部署。

## 分支命名

```text
feature/phase-01-project-init
feature/phase-02-auth-refresh-token
feature/phase-03-pantry-crud
feature/phase-04-expiration-status
feature/phase-05-shopping-list
feature/phase-06-web-ui-theme
feature/phase-07-ci-cd
feature/phase-08-ai-recipes
feature/phase-09-ocr-import
feature/phase-10-ingredient-photo
feature/phase-11-nutrition-estimate
```

## 最小 CI

```yaml
name: CI
on:
  push:
    branches: [master]
  pull_request:
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
      - run: pytest backend/tests -q
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: |
          cd frontend
          npm ci
          npm run build
```

## 部署規劃

- Backend：Render / Railway / AWS EC2。
- Frontend：Vercel / Netlify。
- 開發 DB：本地 Docker PostgreSQL。
- 部署 DB：Managed PostgreSQL。
- 圖片正式環境：S3 / R2 / MinIO 等 object storage。
- Ollama：本機或獨立 GPU / VPS，不建議免費雲端直接跑大型模型。

## 使用者過多與服務穩定性

風險：backend CPU/RAM 不足、DB connection 過多、慢查詢、AI 推論阻塞、圖片佔用頻寬與儲存。

策略：managed PostgreSQL、水平擴充 API server、DB index、pagination、query limit、background job queue、object storage、rate limit、health check、logging、retry 上限。

## Background Job 規劃

MVP 的 AI / OCR / Vision 可同步呼叫。若任務處理時間長，後續改用 Celery / RQ / Dramatiq：

```text
POST 建立任務 → 回傳 job_id → worker 執行 → GET 查詢狀態 → 前端顯示結果
```
