import { createAsyncThunk, createSlice, type PayloadAction } from "@reduxjs/toolkit";

import { pantryApi } from "../../services/apiClient";
import type {
  PantryCreatePayload,
  PantryFilters,
  PantryItem,
  PantryItemStatus,
  PantryListData,
  PantrySort,
  PantryState,
  PantryUpdatePayload,
} from "./pantryTypes";

const initialState: PantryState = {
  items: [],
  page: 1,
  pageSize: 10,
  total: 0,
  loading: false,
  error: null,
  filters: {
    q: "",
    category: "",
    status: "all",
  },
  sort: "expiration_date",
};

/** 取得食材列表（含搜尋、篩選、排序、分頁）。 */
export const fetchPantryItems = createAsyncThunk<PantryListData, void, { rejectValue: string; state: { pantry: PantryState } }>(
  "pantry/fetchPantryItems",
  async (_, { getState, rejectWithValue }) => {
    const pantryState = getState().pantry;

    try {
      const data = await pantryApi.list({
        q: pantryState.filters.q || undefined,
        category: pantryState.filters.category || undefined,
        status: pantryState.filters.status === "all" ? undefined : pantryState.filters.status,
        sort: pantryState.sort,
        page: pantryState.page,
        page_size: pantryState.pageSize,
      });
      return data;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "fetch"));
    }
  },
);

/** 新增食材。 */
export const createPantryItem = createAsyncThunk<PantryItem, PantryCreatePayload, { rejectValue: string }>(
  "pantry/createPantryItem",
  async (payload, { rejectWithValue }) => {
    try {
      return await pantryApi.create(payload);
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "create"));
    }
  },
);

/** 更新食材。 */
export const updatePantryItem = createAsyncThunk<PantryItem, { itemId: number; payload: PantryUpdatePayload }, { rejectValue: string }>(
  "pantry/updatePantryItem",
  async ({ itemId, payload }, { rejectWithValue }) => {
    try {
      return await pantryApi.update(itemId, payload);
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "update"));
    }
  },
);

/** 刪除食材。 */
export const deletePantryItem = createAsyncThunk<number, number, { rejectValue: string }>(
  "pantry/deletePantryItem",
  async (itemId, { rejectWithValue }) => {
    try {
      await pantryApi.remove(itemId);
      return itemId;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "delete"));
    }
  },
);

/** Pantry 狀態 Slice。 */
const pantrySlice = createSlice({
  name: "pantry",
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<PantryFilters>) => {
      state.filters = action.payload;
      state.page = 1;
    },
    setPage: (state, action: PayloadAction<number>) => {
      state.page = action.payload;
    },
    setPageSize: (state, action: PayloadAction<number>) => {
      state.pageSize = action.payload;
      state.page = 1;
    },
    setSort: (state, action: PayloadAction<PantrySort>) => {
      state.sort = action.payload;
      state.page = 1;
    },
    clearPantryError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPantryItems.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPantryItems.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload.items;
        state.page = action.payload.page;
        state.pageSize = action.payload.page_size;
        state.total = action.payload.total;
      })
      .addCase(fetchPantryItems.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? "取得食材列表失敗";
      })
      .addCase(createPantryItem.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createPantryItem.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(createPantryItem.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? "新增食材失敗";
      })
      .addCase(updatePantryItem.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updatePantryItem.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(updatePantryItem.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? "更新食材失敗";
      })
      .addCase(deletePantryItem.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deletePantryItem.fulfilled, (state, action) => {
        state.loading = false;
        state.items = state.items.filter((item) => item.id !== action.payload);
        state.total = Math.max(0, state.total - 1);
      })
      .addCase(deletePantryItem.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? "刪除食材失敗";
      });
  },
});

function getErrorMessage(error: unknown, action: "fetch" | "create" | "update" | "delete"): string {
  const fallback = "操作失敗，請稍後再試。";
  if (error instanceof Error) {
    const text = error.message.toLowerCase();
    if (action === "delete") {
      if (
        text.includes("networkerror") ||
        text.includes("failed to fetch") ||
        text.includes("load failed") ||
        text.includes("constraint") ||
        text.includes("foreign key")
      ) {
        return "此食材已加入購物清單，請先刪除購物清單中的相關項目，再刪除此食材。";
      }
      return fallback;
    }

    if (text.includes("networkerror") || text.includes("failed to fetch") || text.includes("load failed")) {
      return "網路連線異常，請稍後再試。";
    }
    return fallback;
  }
  return fallback;
}

export const { setFilters, setPage, setPageSize, setSort, clearPantryError } = pantrySlice.actions;
export type { PantryItemStatus };
export default pantrySlice.reducer;
