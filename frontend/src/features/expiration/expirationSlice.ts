import { createAsyncThunk, createSlice, type PayloadAction } from "@reduxjs/toolkit";

import { expirationApi, pantryApi } from "../../services/apiClient";
import type {
  ExpirationItem,
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
  items: [],
  loading: false,
  error: null,
  selectedStatusFilter: "all",
};

/** 取得到期提醒摘要與狀態統計。 */
export const fetchExpirationSummary = createAsyncThunk<
  { summary: ExpirationSummary; stats: ExpirationSummaryStats; items: ExpirationItem[] },
  void,
  { rejectValue: string }
>("expiration/fetchExpirationSummary", async (_, { rejectWithValue }) => {
  try {
    const [summary, expiredItems, expiringSoonItems, normalItems] = await Promise.all([
      expirationApi.getSummary(),
      fetchPantryItemsByStatus("expired"),
      fetchPantryItemsByStatus("expiring_soon"),
      fetchPantryItemsByStatus("normal"),
    ]);

    const stats: ExpirationSummaryStats = {
      expired: summary.expired_count,
      expiringSoon: summary.expiring_soon_count,
      normal: normalItems.length,
      total: summary.expired_count + summary.expiring_soon_count + normalItems.length,
    };

    const items = [...expiredItems, ...expiringSoonItems, ...normalItems];

    return { summary, stats, items };
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
        state.items = action.payload.items;
      })
      .addCase(fetchExpirationSummary.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? "取得到期提醒摘要失敗";
      });
  },
});

/** 依狀態分頁抓取 pantry items，合併為完整清單。 */
async function fetchPantryItemsByStatus(status: "expired" | "expiring_soon" | "normal"): Promise<ExpirationItem[]> {
  const pageSize = 100;
  let page = 1;
  let totalPages = 1;
  const collected: ExpirationItem[] = [];

  while (page <= totalPages) {
    const data = await pantryApi.list({
      status,
      page,
      page_size: pageSize,
      sort: "expiration_date",
    });

    collected.push(
      ...data.items.map((item) => ({
        id: item.id,
        name: item.name,
        category: item.category,
        quantity: item.quantity,
        unit: item.unit,
        expiration_date: item.expiration_date,
        status: item.status ?? status,
        storage_location: item.storage_location,
        note: item.note,
      })),
    );
    totalPages = Math.max(1, Math.ceil(data.total / pageSize));
    page += 1;
  }

  return collected;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return "發生未知錯誤";
}

export const { setExpirationStatusFilter, clearExpirationError } = expirationSlice.actions;
export default expirationSlice.reducer;
