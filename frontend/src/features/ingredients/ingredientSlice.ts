import { createAsyncThunk, createSlice, PayloadAction } from "@reduxjs/toolkit";

import type { PantryCreatePayload } from "../pantry/pantryTypes";
import { ingredientsApi, pantryApi } from "../../services/apiClient";
import type {
  IngredientCandidateItem,
  IngredientConfirmSummary,
  IngredientPhotoJobCreateData,
  IngredientPhotoJobStatusData,
  IngredientState,
} from "./ingredientTypes";

const initialState: IngredientState = {
  uploading: false,
  polling: false,
  currentJobId: null,
  jobStatus: null,
  jobError: null,
  previewUrl: null,
  selectedImageName: null,
  candidates: [],
  resultNote: null,
  confirmLoading: false,
  confirmSummary: null,
  showNoItemsState: false,
};

function toStorageLocationUi(value: string): string {
  const normalized = value.trim().toLowerCase();
  if (normalized === "fridge") {
    return "冰箱";
  }
  return value;
}

function toStorageLocationApi(value: string): string {
  return value.trim() || "冰箱";
}

/** 建立食材照片辨識 job。 */
export const createIngredientPhotoJob = createAsyncThunk<IngredientPhotoJobCreateData, File, { rejectValue: string }>(
  "ingredients/createIngredientPhotoJob",
  async (file, { rejectWithValue }) => {
    try {
      return await ingredientsApi.createIngredientPhotoJob(file);
    } catch (error) {
      return rejectWithValue(toFriendlyIngredientError(error, "建立食材辨識任務失敗，請稍後再試。", "create"));
    }
  },
);

/** 查詢食材照片辨識 job 狀態。 */
export const fetchIngredientPhotoJobStatus = createAsyncThunk<IngredientPhotoJobStatusData, number, { rejectValue: string }>(
  "ingredients/fetchIngredientPhotoJobStatus",
  async (jobId, { rejectWithValue }) => {
    try {
      return await ingredientsApi.getIngredientPhotoJob(jobId);
    } catch (error) {
      return rejectWithValue(toFriendlyIngredientError(error, "目前無法查詢任務狀態，請稍後再試。", "status"));
    }
  },
);

/** 將候選資料逐筆寫入 pantry（不可 bulk）。 */
export const confirmCandidatesToPantry = createAsyncThunk<IngredientConfirmSummary, IngredientCandidateItem[], { rejectValue: string }>(
  "ingredients/confirmCandidatesToPantry",
  async (candidates, { rejectWithValue }) => {
    const failureItems: IngredientConfirmSummary["failureItems"] = [];
    let successCount = 0;

    for (let index = 0; index < candidates.length; index += 1) {
      const candidate = candidates[index];
      const payload: PantryCreatePayload = {
        name: candidate.name.trim(),
        category: candidate.category.trim(),
        quantity: Math.max(1, Math.floor(candidate.quantity)),
        unit: candidate.unit.trim(),
        expiration_date: candidate.expiration_date,
        storage_location: toStorageLocationApi(candidate.storage_location),
        note: candidate.note.trim() || null,
      };

      try {
        await pantryApi.create(payload);
        successCount += 1;
      } catch (error) {
        failureItems.push({
          index,
          name: candidate.name,
          reason: toFriendlyIngredientError(error, "加入庫存失敗，請稍後再試。", "confirm"),
        });
      }
    }

    if (successCount === 0 && failureItems.length > 0) {
      return rejectWithValue("所有候選食材都加入失敗，請檢查欄位後再試。");
    }

    return { successCount, failureItems };
  },
);

const ingredientSlice = createSlice({
  name: "ingredients",
  initialState,
  reducers: {
    beginNewIngredientRecognition: (state, action: PayloadAction<{ previewUrl: string; fileName: string }>) => {
      state.previewUrl = action.payload.previewUrl;
      state.selectedImageName = action.payload.fileName;
      state.currentJobId = null;
      state.jobStatus = null;
      state.jobError = null;
      state.candidates = [];
      state.resultNote = null;
      state.polling = false;
      state.confirmLoading = false;
      state.confirmSummary = null;
      state.showNoItemsState = false;
    },
    clearIngredientJobError: (state) => {
      state.jobError = null;
    },
    clearIngredientResult: (state) => {
      state.previewUrl = null;
      state.selectedImageName = null;
      state.candidates = [];
      state.resultNote = null;
      state.confirmSummary = null;
      state.jobError = null;
      state.jobStatus = null;
      state.currentJobId = null;
      state.polling = false;
      state.showNoItemsState = false;
    },
    setIngredientPolling: (state, action: PayloadAction<boolean>) => {
      state.polling = action.payload;
    },
    updateCandidateField: (
      state,
      action: PayloadAction<{ index: number; field: keyof IngredientCandidateItem; value: string | number | null }>,
    ) => {
      const target = state.candidates[action.payload.index];
      if (!target) {
        return;
      }
      const { field, value } = action.payload;
      if (field === "quantity" && typeof value === "number") {
        target.quantity = Math.max(1, Math.floor(value));
        return;
      }
      if (field === "expiration_date") {
        target.expiration_date = typeof value === "string" ? value : null;
        return;
      }
      if (typeof value === "string") {
        target[field] = value as never;
      }
    },
    removeCandidate: (state, action: PayloadAction<number>) => {
      state.candidates = state.candidates.filter((_, index) => index !== action.payload);
      if (state.candidates.length === 0) {
        state.previewUrl = null;
        state.selectedImageName = null;
        state.resultNote = null;
        state.confirmSummary = null;
        state.jobError = null;
        state.jobStatus = null;
        state.currentJobId = null;
        state.polling = false;
        state.showNoItemsState = false;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(createIngredientPhotoJob.pending, (state) => {
        state.uploading = true;
        state.jobError = null;
        state.confirmSummary = null;
        state.showNoItemsState = false;
      })
      .addCase(createIngredientPhotoJob.fulfilled, (state, action) => {
        state.uploading = false;
        state.currentJobId = action.payload.job_id;
        state.jobStatus = action.payload.status;
        state.polling = action.payload.status === "pending" || action.payload.status === "running";
        state.candidates = [];
        state.resultNote = null;
        state.showNoItemsState = false;
      })
      .addCase(createIngredientPhotoJob.rejected, (state, action) => {
        state.uploading = false;
        state.polling = false;
        state.jobError = action.payload ?? "建立食材辨識任務失敗，請稍後再試。";
      })
      .addCase(fetchIngredientPhotoJobStatus.fulfilled, (state, action) => {
        state.currentJobId = action.payload.job_id;
        state.jobStatus = action.payload.status;
        if (action.payload.status === "success") {
          state.polling = false;
          state.jobError = null;
          state.candidates = (action.payload.result?.candidate_items ?? []).map((item) => ({
            ...item,
            quantity: Math.max(1, Math.floor(item.quantity)),
            storage_location: toStorageLocationUi(item.storage_location),
          }));
          state.resultNote = action.payload.result?.note ?? null;
          state.showNoItemsState = state.candidates.length === 0;
          return;
        }
        if (action.payload.status === "failed") {
          state.polling = false;
          state.jobError = action.payload.error_message ?? "食材辨識失敗，請稍後再試。";
          state.candidates = [];
          state.resultNote = null;
          state.showNoItemsState = false;
          return;
        }
        if (action.payload.status === "cancelled") {
          state.polling = false;
          state.jobError = "任務已取消，請重新上傳後再試。";
          return;
        }
        state.polling = true;
      })
      .addCase(fetchIngredientPhotoJobStatus.rejected, (state, action) => {
        state.polling = false;
        state.jobError = action.payload ?? "目前無法查詢任務狀態，請稍後再試。";
      })
      .addCase(confirmCandidatesToPantry.pending, (state) => {
        state.confirmLoading = true;
        state.jobError = null;
        state.confirmSummary = null;
      })
      .addCase(confirmCandidatesToPantry.fulfilled, (state, action) => {
        state.confirmLoading = false;
        state.confirmSummary = action.payload;
        if (action.payload.failureItems.length > 0) {
          const failureIndexSet = new Set(action.payload.failureItems.map((item) => item.index));
          state.candidates = state.candidates.filter((_, index) => failureIndexSet.has(index));
          state.showNoItemsState = false;
          return;
        }
        state.previewUrl = null;
        state.selectedImageName = null;
        state.candidates = [];
        state.resultNote = null;
        state.jobStatus = null;
        state.currentJobId = null;
        state.polling = false;
        state.showNoItemsState = false;
      })
      .addCase(confirmCandidatesToPantry.rejected, (state, action) => {
        state.confirmLoading = false;
        state.jobError = action.payload ?? "候選食材加入庫存失敗，請稍後再試。";
      });
  },
});

function toFriendlyIngredientError(error: unknown, fallback: string, scope: "create" | "status" | "confirm"): string {
  if (!(error instanceof Error)) {
    return fallback;
  }
  const message = error.message;
  const text = message.toLowerCase();
  if (message.includes("食材照片辨識逾時")) {
    return message;
  }
  if (text.includes("networkerror") || text.includes("failed to fetch") || text.includes("load failed")) {
    return "網路連線異常，請檢查網路後重試。";
  }
  if (text.includes("5mb")) {
    return "圖片大小不可超過 5MB，請改用較小檔案。";
  }
  if (text.includes("jpeg/png/webp") || text.includes("不支援的圖片格式")) {
    return "圖片格式不支援，請使用 JPG、PNG 或 WEBP。";
  }
  if (text.includes("找不到") || text.includes("not found")) {
    return scope === "status" ? "找不到對應任務，請重新上傳圖片。" : fallback;
  }
  if (text.includes("401") || text.includes("未登入") || text.includes("token")) {
    return "登入狀態已失效，請重新登入後再試。";
  }
  if (text.includes("403")) {
    return "你沒有權限執行此操作。";
  }
  return fallback;
}

export const {
  beginNewIngredientRecognition,
  clearIngredientJobError,
  clearIngredientResult,
  setIngredientPolling,
  updateCandidateField,
  removeCandidate,
} = ingredientSlice.actions;
export default ingredientSlice.reducer;
