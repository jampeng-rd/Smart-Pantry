import { createAsyncThunk, createSlice, type PayloadAction } from "@reduxjs/toolkit";

import { shoppingApi } from "../../services/apiClient";
import type {
  ShoppingCreatePayload,
  ShoppingFilters,
  ShoppingItem,
  ShoppingListData,
  ShoppingSort,
  ShoppingState,
  ShoppingUpdatePayload,
} from "./shoppingTypes";

const initialState: ShoppingState = {
  items: [],
  page: 1,
  pageSize: 10,
  total: 0,
  loading: false,
  error: null,
  filters: {
    q: "",
    isPurchased: "all",
  },
  sort: "created_at",
};

/** 取得購物清單（含搜尋、篩選、排序、分頁）。 */
export const fetchShoppingItems = createAsyncThunk<ShoppingListData, void, { rejectValue: string; state: { shopping: ShoppingState } }>(
  "shopping/fetchShoppingItems",
  async (_, { getState, rejectWithValue }) => {
    const shoppingState = getState().shopping;

    try {
      const data = await shoppingApi.list({
        q: shoppingState.filters.q || undefined,
        is_purchased:
          shoppingState.filters.isPurchased === "all"
            ? undefined
            : shoppingState.filters.isPurchased === "purchased",
        sort: shoppingState.sort === "name" ? "created_at" : shoppingState.sort,
        page: shoppingState.page,
        page_size: shoppingState.pageSize,
      });

      if (shoppingState.sort === "name") {
        return {
          ...data,
          items: [...data.items].sort((a, b) => a.name.localeCompare(b.name, "zh-Hant")),
        };
      }

      return data;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error));
    }
  },
);

/** 新增購物項目。 */
export const createShoppingItem = createAsyncThunk<ShoppingItem, ShoppingCreatePayload, { rejectValue: string }>(
  "shopping/createShoppingItem",
  async (payload, { rejectWithValue }) => {
    try {
      return await shoppingApi.create(payload);
    } catch (error) {
      return rejectWithValue(getErrorMessage(error));
    }
  },
);

/** 更新購物項目。 */
export const updateShoppingItem = createAsyncThunk<ShoppingItem, { itemId: number; payload: ShoppingUpdatePayload }, { rejectValue: string }>(
  "shopping/updateShoppingItem",
  async ({ itemId, payload }, { rejectWithValue }) => {
    try {
      return await shoppingApi.update(itemId, payload);
    } catch (error) {
      return rejectWithValue(getErrorMessage(error));
    }
  },
);

/** 刪除購物項目。 */
export const deleteShoppingItem = createAsyncThunk<number, number, { rejectValue: string }>(
  "shopping/deleteShoppingItem",
  async (itemId, { rejectWithValue }) => {
    try {
      await shoppingApi.remove(itemId);
      return itemId;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error));
    }
  },
);

/** Shopping 狀態 Slice。 */
const shoppingSlice = createSlice({
  name: "shopping",
  initialState,
  reducers: {
    setShoppingFilters: (state, action: PayloadAction<ShoppingFilters>) => {
      state.filters = action.payload;
      state.page = 1;
    },
    setShoppingPage: (state, action: PayloadAction<number>) => {
      state.page = action.payload;
    },
    setShoppingPageSize: (state, action: PayloadAction<number>) => {
      state.pageSize = action.payload;
      state.page = 1;
    },
    setShoppingSort: (state, action: PayloadAction<ShoppingSort>) => {
      state.sort = action.payload;
      state.page = 1;
    },
    clearShoppingError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchShoppingItems.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchShoppingItems.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload.items;
        state.page = action.payload.page;
        state.pageSize = action.payload.page_size;
        state.total = action.payload.total;
      })
      .addCase(fetchShoppingItems.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? "取得購物清單失敗";
      })
      .addCase(createShoppingItem.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createShoppingItem.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(createShoppingItem.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? "新增購物項目失敗";
      })
      .addCase(updateShoppingItem.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateShoppingItem.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(updateShoppingItem.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? "更新購物項目失敗";
      })
      .addCase(deleteShoppingItem.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteShoppingItem.fulfilled, (state, action) => {
        state.loading = false;
        state.items = state.items.filter((item) => item.id !== action.payload);
        state.total = Math.max(0, state.total - 1);
      })
      .addCase(deleteShoppingItem.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? "刪除購物項目失敗";
      });
  },
});

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return "發生未知錯誤";
}

export const { setShoppingFilters, setShoppingPage, setShoppingPageSize, setShoppingSort, clearShoppingError } = shoppingSlice.actions;
export default shoppingSlice.reducer;
