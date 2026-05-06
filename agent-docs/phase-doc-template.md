# 階段完成文件模板

檔名格式：`docs/phase-xx-階段名稱.md`

## 1. 階段目標

## 2. 完成內容

## 3. 涉及檔案

## 4. 如何啟動

後端：`python -m uvicorn backend.app.main:app --reload`

前端：`cd frontend && npm run dev`

Docker：`docker compose up --build`

## 5. 單元測試

全部測試：`pytest backend/tests -q`

## 6. Web UI 測試方式

## 7. API 串接說明

## 8. PostgreSQL 測試方式

## 9. 效能與擴充性注意事項

需說明是否有 pagination、是否需要 index、是否有延遲風險、未來如何擴充。

## 10. 已知限制

## 11. 下一階段建議
