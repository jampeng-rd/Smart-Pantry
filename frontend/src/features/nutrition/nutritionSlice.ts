import { createSlice } from "@reduxjs/toolkit";

import type { NutritionState } from "./nutritionTypes";

const initialState: NutritionState = {
  items: [],
  page: 1,
  pageSize: 10,
  total: 0,
  loading: false,
  error: null,
};

/** 營養估算狀態 Slice（Phase 01 僅保留骨架）。 */
const nutritionSlice = createSlice({
  name: "nutrition",
  initialState,
  reducers: {},
});

export default nutritionSlice.reducer;
