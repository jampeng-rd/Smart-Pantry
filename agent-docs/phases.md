# 開發階段規劃

## Phase 01：專案初始化

建立 repo、AGENTS.md、agent-docs、backend、frontend、docs、Docker Compose、PostgreSQL service、README、最小 GitHub Actions CI。

文件：`docs/phase-01-project-init.md`

## Phase 02：使用者註冊 / 登入 + Refresh Token

建立 users、refresh_tokens、註冊、登入、access token（15 分鐘）、refresh token（7 天）、refresh、logout/revoke、refresh token hash 儲存、取得目前使用者、密碼雜湊、測試。

文件：`docs/phase-02-auth-refresh-token.md`

## Phase 03：手動食材庫存管理

建立 pantry_items、新增、編輯、刪除、查看自己的食材、分類查詢、過期日排序、pagination。

文件：`docs/phase-03-pantry-crud.md`

## Phase 04：食材分類、過期提醒與狀態篩選

定義 normal、expiring_soon、expired；根據 expiration_date 計算狀態；支援狀態篩選、搜尋、Dashboard 摘要。不做自動庫存不足判斷。

文件：`docs/phase-04-expiration-status.md`

## Phase 05：購物清單

建立 shopping_list_items；手動新增、從庫存加入、標記已購買、刪除；購物清單獨立於庫存但可引用 pantry_item_id。

文件：`docs/phase-05-shopping-list.md`

## Phase 06：前端完整 UI + 主題切換

React + Vite + TypeScript；Redux slices 分開；登入/註冊；自動 refresh token；Dashboard；食材頁；購物清單；react-icons；繁中 UI；柔和亮/暗主題；API 集中在 apiClient。

文件：`docs/phase-06-web-ui-theme.md`

## Phase 07：CI/CD 與部署

GitHub Actions、backend pytest、frontend build、Docker build、PostgreSQL 檢查、部署文件、CORS、環境變數、PR flow、擴充策略。

文件：`docs/phase-07-ci-cd.md`

## Phase 08：AI 食譜推薦

建立 recipe_recommendations；根據庫存、即將過期、設備、偏好、過敏原產生料理建議；本機 Ollama + LangChain；mock 測試；記錄延遲限制。

文件：`docs/phase-08-ai-recipes.md`

## Phase 09：發票 / 收據 OCR 匯入

上傳發票/收據；圖片大小限制 5MB；開發階段可存本機 uploads/；DB 只存 image_path / image_url；OCR 擷取；AI 整理候選食材；使用者確認後加入庫存；傳統市場無收據仍可手動輸入。

文件：`docs/phase-09-ocr-import.md`

## Phase 10：食材照片辨識

上傳單一或少量食材照片；圖片大小限制 5MB；開發階段可存本機 uploads/；DB 只存 image_path / image_url；Vision AI 產生候選食材；使用者確認後加入庫存；不做整個冰箱辨識。

文件：`docs/phase-10-ingredient-photo.md`

## Phase 11：餐點營養粗估

上傳餐點照片；AI 粗估菜色與熱量/蛋白質/碳水/脂肪；建立 meal_logs 與 nutrition_estimates；明確生活參考聲明。

文件：`docs/phase-11-nutrition-estimate.md`
