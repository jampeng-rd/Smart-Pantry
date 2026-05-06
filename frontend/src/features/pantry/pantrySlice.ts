import { createSlice } from "@reduxjs/toolkit";

import type { PantryState } from "./pantryTypes";

const initialState: PantryState = {
  items: [],
  page: 1,
  pageSize: 10,
  total: 0,
  loading: false,
  error: null,
};

/** 食材狀態 Slice（Phase 01 僅保留骨架）。 */
const pantrySlice = createSlice({
  name: "pantry",
  initialState,
  reducers: {},
});

export default pantrySlice.reducer;
