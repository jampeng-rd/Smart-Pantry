import { createAsyncThunk, createSlice, type PayloadAction } from "@reduxjs/toolkit";

import { expirationApi, pantryApi } from "../../services/apiClient";
import type {
  ExpirationState,
  ExpirationStatusFilter,
  ExpirationSummary,
  ExpirationSummaryStats,
} from "./expirationTypes";

const initialState: ExpirationState = {
  summary: null,
  stats: {
    expired: 0,
    expiringSoon: 0,
    normal: 0,
    total: 0,
  },
  loading: false,
  error: null,
  selectedStatusFilter: "all",
};

/** 取得到期提醒摘要與狀態統計。 */
export const fetchExpirationSummary = createAsyncThunk<
  { summary: ExpirationSummary; stats: ExpirationSummaryStats },
  void,
  { rejectValue: string }
>("expiration/fetchExpirationSummary", async (_, { rejectWithValue }) => {
  try {
    const [summary, allList, normalList] = await Promise.all([
      expirationApi.getSummary(),
      pantryApi.list({ page: 1, page_size: 1 }),
      pantryApi.list({ status: "normal", page: 1, page_size: 1 }),
    ]);

    const stats: ExpirationSummaryStats = {
      expired: summary.expired_count,
      expiringSoon: summary.expiring_soon_count,
      normal: normalList.total,
      total: allList.total,
    };

    return { summary, stats };
  } catch (error) {
    return rejectWithValue(getErrorMessage(error));
  }
});

/** Expiration 狀態 Slice。 */
const expirationSlice = createSlice({
  name: "expiration",
  initialState,
  reducers: {
    setExpirationStatusFilter: (state, action: PayloadAction<ExpirationStatusFilter>) => {
      state.selectedStatusFilter = action.payload;
    },
    clearExpirationError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchExpirationSummary.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchExpirationSummary.fulfilled, (state, action) => {
        state.loading = false;
        state.summary = action.payload.summary;
        state.stats = action.payload.stats;
      })
      .addCase(fetchExpirationSummary.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? "取得到期提醒摘要失敗";
      });
  },
});

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return "發生未知錯誤";
}

export const { setExpirationStatusFilter, clearExpirationError } = expirationSlice.actions;
export default expirationSlice.reducer;
