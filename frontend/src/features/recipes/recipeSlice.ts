import { createSlice } from "@reduxjs/toolkit";

import type { RecipeState } from "./recipeTypes";

const initialState: RecipeState = {
  items: [],
  page: 1,
  pageSize: 10,
  total: 0,
  loading: false,
  error: null,
};

/** 食譜建議狀態 Slice（Phase 01 僅保留骨架）。 */
const recipeSlice = createSlice({
  name: "recipes",
  initialState,
  reducers: {},
});

export default recipeSlice.reducer;
