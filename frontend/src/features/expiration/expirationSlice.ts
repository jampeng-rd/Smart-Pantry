import { createSlice } from "@reduxjs/toolkit";

import type { ExpirationState } from "./expirationTypes";

const initialState: ExpirationState = {
  items: [],
  page: 1,
  pageSize: 10,
  total: 0,
  loading: false,
  error: null,
};

/** 過期提醒狀態 Slice（Phase 01 僅保留骨架）。 */
const expirationSlice = createSlice({
  name: "expiration",
  initialState,
  reducers: {},
});

export default expirationSlice.reducer;
