import { createSlice } from "@reduxjs/toolkit";

import type { ShoppingState } from "./shoppingTypes";

const initialState: ShoppingState = {
  items: [],
  page: 1,
  pageSize: 10,
  total: 0,
  loading: false,
  error: null,
};

/** 購物清單狀態 Slice（Phase 01 僅保留骨架）。 */
const shoppingSlice = createSlice({
  name: "shopping",
  initialState,
  reducers: {},
});

export default shoppingSlice.reducer;
