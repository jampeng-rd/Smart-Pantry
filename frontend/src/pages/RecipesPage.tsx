import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { FiAlertCircle, FiBookOpen, FiCheckCircle, FiClock, FiLoader, FiRefreshCw, FiSend, FiTag } from "react-icons/fi";

import { useAppDispatch, useAppSelector } from "../app/hooks";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingState } from "../components/common/LoadingState";
import {
  clearRecipePantryError,
  clearRecipeJobError,
  createRecipeRecommendationJob,
  fetchPantryItemsForRecipes,
  fetchRecipeRecommendationJobStatus,
  stopRecipePolling,
} from "../features/recipes/recipeSlice";
import type { RecipeRecommendationMode } from "../features/recipes/recipeTypes";

const POLLING_INTERVAL_MS = 2500;

/** Recipes AI 食譜建議頁。 */
export function RecipesPage() {
  const dispatch = useAppDispatch();
  const { pantryItems, pantryLoading, pantryError, creatingJob, polling, currentJobId, jobStatus, jobError, result } = useAppSelector(
    (state) => state.recipes,
  );

  const [recommendationMode, setRecommendationMode] = useState<RecipeRecommendationMode>("selected_items");
  const [selectedItemIds, setSelectedItemIds] = useState<number[]>([]);
  const [cookingTimeMinutes, setCookingTimeMinutes] = useState("30");
  const [cookingToolsText, setCookingToolsText] = useState("");
  const [dietPreference, setDietPreference] = useState("");
  const [allergiesText, setAllergiesText] = useState("");
  const [prioritizeExpiringSoon, setPrioritizeExpiringSoon] = useState(true);
  const [formError, setFormError] = useState<string | null>(null);

  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    void dispatch(fetchPantryItemsForRecipes());
  }, [dispatch]);

  useEffect(() => {
    if (!polling || !currentJobId) {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    intervalRef.current = window.setInterval(() => {
      void dispatch(fetchRecipeRecommendationJobStatus(currentJobId));
    }, POLLING_INTERVAL_MS);

    return () => {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [dispatch, polling, currentJobId]);

  useEffect(() => {
    return () => {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
      }
      dispatch(stopRecipePolling());
    };
  }, [dispatch]);

  const isPantryEmpty = useMemo(() => !pantryLoading && !pantryError && pantryItems.length === 0, [pantryItems.length, pantryLoading, pantryError]);
  const pendingMessage = useMemo(() => {
    if (jobStatus === "running") {
      return "AI 正在產生食譜，請稍候...";
    }
    if (jobStatus === "pending") {
      return "任務已建立，AI 正在排程中...";
    }
    return null;
  }, [jobStatus]);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormError(null);
    dispatch(clearRecipeJobError());

    const parsedCookingTime = Number.parseInt(cookingTimeMinutes, 10);
    if (!Number.isInteger(parsedCookingTime) || parsedCookingTime <= 0) {
      setFormError("料理時間需為正整數。");
      return;
    }
    if (recommendationMode === "selected_items" && selectedItemIds.length === 0) {
      setFormError("請至少選擇一項食材。");
      return;
    }

    const cookingTools = splitCommaValues(cookingToolsText);
    const allergies = splitCommaValues(allergiesText);
    await dispatch(
      createRecipeRecommendationJob({
        recommendation_mode: recommendationMode,
        selected_pantry_item_ids: recommendationMode === "selected_items" ? selectedItemIds : undefined,
        prioritize_expiring_soon: prioritizeExpiringSoon,
        cooking_time_minutes: parsedCookingTime,
        cooking_tools: cookingTools,
        diet_preference: dietPreference.trim() ? dietPreference.trim() : null,
        allergies,
      }),
    ).unwrap();
  };

  return (
    <section className="workspace-recipes">
      <form className="card recipes-form-card" noValidate onSubmit={(event) => void onSubmit(event)}>
        <header className="recipes-header">
          <h2 className="workspace-title">
            <FiBookOpen aria-hidden="true" /> AI 食譜建議
          </h2>
          <p>建立任務後會由後端背景處理，完成後自動顯示結果。</p>
        </header>

        <div className="recipes-mode-switch" role="group" aria-label="推薦模式">
          <button
            type="button"
            className={`btn ghost recipes-mode-btn ${recommendationMode === "selected_items" ? "active" : ""}`}
            onClick={() => setRecommendationMode("selected_items")}
          >
            <FiCheckCircle aria-hidden="true" /> 自選食材
          </button>
          <button
            type="button"
            className={`btn ghost recipes-mode-btn ${recommendationMode === "auto_from_pantry" ? "active" : ""}`}
            onClick={() => setRecommendationMode("auto_from_pantry")}
          >
            <FiRefreshCw aria-hidden="true" /> 自動從庫存挑選
          </button>
        </div>

        {recommendationMode === "selected_items" ? (
          <div className="recipes-section">
            <div className="recipes-section-title">
              <FiTag aria-hidden="true" />
              <h3>選擇食材（可複選）</h3>
            </div>
            {pantryLoading ? <LoadingState className="card pantry-loading recipes-inline-card" text="載入食材清單中..." /> : null}
            {pantryError ? (
              <ErrorState
                message={pantryError}
                className="card pantry-error recipes-inline-card"
                actionsClassName="pantry-error-actions"
                onRetry={() => void dispatch(fetchPantryItemsForRecipes())}
                onClose={() => dispatch(clearRecipePantryError())}
              />
            ) : null}
            {isPantryEmpty ? (
              <EmptyState
                icon={FiAlertCircle}
                title="目前沒有可選食材"
                description="請先到食材庫存新增資料，再回來建立食譜任務。"
                className="pantry-empty card recipes-inline-card"
              />
            ) : null}
            {!pantryLoading && !pantryError && pantryItems.length > 0 ? (
              <div className="recipes-pantry-grid">
                {pantryItems.map((item) => {
                  const checked = selectedItemIds.includes(item.id);
                  return (
                    <label key={item.id} className={`recipes-pantry-item ${checked ? "checked" : ""}`}>
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={(event) => {
                          setSelectedItemIds((prev) =>
                            event.target.checked ? [...prev, item.id] : prev.filter((selectedId) => selectedId !== item.id),
                          );
                        }}
                      />
                      <span className="recipes-pantry-name">{item.name}</span>
                      <span className="recipes-pantry-meta">
                        {item.category} | {item.quantity} {item.unit}
                      </span>
                      <span className="recipes-pantry-meta">狀態：{toStatusText(item.status)}</span>
                    </label>
                  );
                })}
              </div>
            ) : null}
          </div>
        ) : (
          <div className="card recipes-inline-card recipes-auto-tip">
            <FiRefreshCw aria-hidden="true" />
            <p>系統會由目前庫存自動挑選適合食材建立推薦任務。</p>
          </div>
        )}

        <div className="recipes-form-grid">
          <label>
            料理時間（分鐘）*
            <input
              type="number"
              min={1}
              step={1}
              value={cookingTimeMinutes}
              onChange={(event) => setCookingTimeMinutes(event.target.value)}
              placeholder="例如 30"
            />
          </label>
          <label>
            料理工具（逗號分隔）
            <input
              type="text"
              value={cookingToolsText}
              onChange={(event) => setCookingToolsText(event.target.value)}
              placeholder="例如 平底鍋, 電鍋"
            />
          </label>
          <label>
            飲食偏好
            <input
              type="text"
              value={dietPreference}
              onChange={(event) => setDietPreference(event.target.value)}
              placeholder="例如 高蛋白、低碳"
            />
          </label>
          <label>
            過敏原（逗號分隔）
            <input
              type="text"
              value={allergiesText}
              onChange={(event) => setAllergiesText(event.target.value)}
              placeholder="例如 花生, 蝦"
            />
          </label>
          <label className="recipes-checkbox-label">
            <input
              type="checkbox"
              checked={prioritizeExpiringSoon}
              onChange={(event) => setPrioritizeExpiringSoon(event.target.checked)}
            />
            優先使用即將過期食材
          </label>
        </div>

        {formError ? <p className="pantry-field-error">{formError}</p> : null}

        <div className="recipes-actions">
          <button type="submit" className="btn" disabled={creatingJob || polling}>
            {creatingJob ? <FiLoader aria-hidden="true" className="spin" /> : <FiSend aria-hidden="true" />}
            建立 AI 食譜任務
          </button>
        </div>
      </form>

      {pendingMessage ? (
        <div className="card recipes-job-status" role="status">
          <FiClock aria-hidden="true" />
          <p>{pendingMessage}</p>
        </div>
      ) : null}

      {jobError ? (
        <ErrorState
          message={jobError}
          className="card pantry-error"
          actionsClassName="pantry-error-actions"
          onClose={() => dispatch(clearRecipeJobError())}
        />
      ) : null}

      {result ? (
        <article className="card recipes-result-card">
          <h3>{result.recipe_name}</h3>
          <p className="recipes-result-time">
            <FiClock aria-hidden="true" /> 估計料理時間：{result.cooking_time_minutes} 分鐘
          </p>
          <section>
            <h4>使用食材</h4>
            <ul>{result.ingredients_used.map((item) => <li key={`used-${item}`}>{item}</li>)}</ul>
          </section>
          <section>
            <h4>缺少食材</h4>
            {result.missing_ingredients.length === 0 ? <p>無</p> : <ul>{result.missing_ingredients.map((item) => <li key={`missing-${item}`}>{item}</li>)}</ul>}
          </section>
          <section>
            <h4>步驟</h4>
            <ol>{result.steps.map((step) => <li key={step}>{step}</li>)}</ol>
          </section>
          <section>
            <h4>備註</h4>
            <p>{result.note}</p>
          </section>
        </article>
      ) : null}
    </section>
  );
}

function splitCommaValues(value: string): string[] {
  return value
    .split(",")
    .map((part) => part.trim())
    .filter((part) => part.length > 0);
}

function toStatusText(status: string | undefined): string {
  if (status === "expired") {
    return "已過期";
  }
  if (status === "expiring_soon") {
    return "即將到期";
  }
  return "一般";
}
