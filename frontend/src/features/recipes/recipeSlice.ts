import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import type { RecipeState } from "./recipeTypes";
import type {
  RecipeRecommendationJobCreateData,
  RecipeRecommendationJobCreatePayload,
  RecipeRecommendationJobStatusData,
} from "./recipeTypes";
import type { PantryListData } from "../pantry/pantryTypes";
import { pantryApi, recipesApi } from "../../services/apiClient";

const initialState: RecipeState = {
  pantryItems: [],
  pantryLoading: false,
  pantryError: null,
  creatingJob: false,
  polling: false,
  currentJobId: null,
  jobStatus: null,
  jobError: null,
  result: null,
};

/** 載入 Recipes 頁用的 pantry 清單（僅取第一頁大量資料供多選）。 */
export const fetchPantryItemsForRecipes = createAsyncThunk<PantryListData, void, { rejectValue: string }>(
  "recipes/fetchPantryItemsForRecipes",
  async (_, { rejectWithValue }) => {
    try {
      return await pantryApi.list({ page: 1, page_size: 100, sort: "expiration_date" });
    } catch (error) {
      return rejectWithValue(toFriendlyRecipeError(error, "目前無法載入食材清單，請稍後再試。", "pantry_list"));
    }
  },
);

/** 建立食譜推薦 job。 */
export const createRecipeRecommendationJob = createAsyncThunk<
  RecipeRecommendationJobCreateData,
  RecipeRecommendationJobCreatePayload,
  { rejectValue: string }
>("recipes/createRecipeRecommendationJob", async (payload, { rejectWithValue }) => {
  try {
    return await recipesApi.createRecommendationJob(payload);
  } catch (error) {
    return rejectWithValue(toFriendlyRecipeError(error, "建立食譜任務失敗，請稍後再試。", "recipe_job_create"));
  }
});

/** 查詢食譜推薦 job 狀態。 */
export const fetchRecipeRecommendationJobStatus = createAsyncThunk<
  RecipeRecommendationJobStatusData,
  number,
  { rejectValue: string }
>("recipes/fetchRecipeRecommendationJobStatus", async (jobId, { rejectWithValue }) => {
  try {
    return await recipesApi.getRecommendationJobStatus(jobId);
  } catch (error) {
    return rejectWithValue(toFriendlyRecipeError(error, "目前無法查詢任務狀態，請稍後再試。", "recipe_job_status"));
  }
});

/** 食譜建議狀態 Slice。 */
const recipeSlice = createSlice({
  name: "recipes",
  initialState,
  reducers: {
    clearRecipeState: (state) => {
      state.creatingJob = false;
      state.polling = false;
      state.currentJobId = null;
      state.jobStatus = null;
      state.jobError = null;
      state.result = null;
    },
    clearRecipeJobError: (state) => {
      state.jobError = null;
    },
    clearRecipePantryError: (state) => {
      state.pantryError = null;
    },
    stopRecipePolling: (state) => {
      state.polling = false;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPantryItemsForRecipes.pending, (state) => {
        state.pantryLoading = true;
        state.pantryError = null;
      })
      .addCase(fetchPantryItemsForRecipes.fulfilled, (state, action) => {
        state.pantryLoading = false;
        state.pantryItems = action.payload.items;
      })
      .addCase(fetchPantryItemsForRecipes.rejected, (state, action) => {
        state.pantryLoading = false;
        state.pantryError = action.payload ?? "載入食材清單失敗，請稍後再試。";
      })
      .addCase(createRecipeRecommendationJob.pending, (state) => {
        state.creatingJob = true;
        state.jobError = null;
        state.result = null;
      })
      .addCase(createRecipeRecommendationJob.fulfilled, (state, action) => {
        state.creatingJob = false;
        state.polling = true;
        state.currentJobId = action.payload.job_id;
        state.jobStatus = action.payload.status;
      })
      .addCase(createRecipeRecommendationJob.rejected, (state, action) => {
        state.creatingJob = false;
        state.polling = false;
        state.jobError = action.payload ?? "建立食譜任務失敗，請稍後再試。";
      })
      .addCase(fetchRecipeRecommendationJobStatus.fulfilled, (state, action) => {
        state.currentJobId = action.payload.job_id;
        state.jobStatus = action.payload.status;
        if (action.payload.status === "success") {
          state.result = action.payload.result;
          state.jobError = null;
          state.polling = false;
          return;
        }
        if (action.payload.status === "failed") {
          state.jobError = action.payload.error_message ?? "食譜產生失敗，請稍後再試。";
          state.result = null;
          state.polling = false;
          return;
        }
        if (action.payload.status === "cancelled") {
          state.jobError = "任務已取消，請重新送出需求。";
          state.result = null;
          state.polling = false;
          return;
        }
        state.polling = true;
      })
      .addCase(fetchRecipeRecommendationJobStatus.rejected, (state, action) => {
        state.polling = false;
        state.jobError = action.payload ?? "目前無法查詢任務狀態，請稍後再試。";
      });
  },
});

function toFriendlyRecipeError(error: unknown, fallback: string, scope: "pantry_list" | "recipe_job_create" | "recipe_job_status"): string {
  if (!(error instanceof Error)) {
    return fallback;
  }
  const text = error.message.toLowerCase();
  if (text.includes("networkerror") || text.includes("failed to fetch") || text.includes("load failed")) {
    return "網路連線異常，請檢查網路後重試。";
  }
  if (text.includes("not found") && scope !== "pantry_list") {
    return "找不到任務資料，請重新送出。";
  }
  if (text.includes("page_size") || text.includes("validation") || text.includes("422")) {
    if (scope === "pantry_list") {
      return "食材清單參數不符合後端限制，請重新整理後再試。";
    }
    return "輸入條件格式不正確，請檢查後再送出。";
  }
  if (text.includes("401") || text.includes("token") || text.includes("未登入")) {
    return "登入狀態已失效，請重新登入後再試。";
  }
  if (text.includes("403")) {
    return "你沒有權限執行此操作。";
  }
  if (text.includes("500") || text.includes("internal")) {
    return "伺服器暫時忙碌，請稍後再試。";
  }
  return fallback;
}

export const { clearRecipeState, clearRecipeJobError, clearRecipePantryError, stopRecipePolling } = recipeSlice.actions;
export default recipeSlice.reducer;
