import { createSlice } from "@reduxjs/toolkit";

import type { ThemeState } from "./themeTypes";

const initialState: ThemeState = {
  mode: "light-soft",
};

/** 主題狀態 Slice。 */
const themeSlice = createSlice({
  name: "theme",
  initialState,
  reducers: {
    toggleTheme: (state) => {
      state.mode = state.mode === "light-soft" ? "dark-soft" : "light-soft";
      document.documentElement.setAttribute("data-theme", state.mode);
    },
  },
});

export const { toggleTheme } = themeSlice.actions;
export default themeSlice.reducer;
