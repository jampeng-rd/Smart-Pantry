import { createSlice } from "@reduxjs/toolkit";

import type { ThemeState } from "./themeTypes";

const THEME_STORAGE_KEY = "smartpantry_theme_mode";

function getInitialThemeMode(): ThemeState["mode"] {
  const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
  if (savedTheme === "light-soft" || savedTheme === "dark-soft") {
    return savedTheme;
  }
  return "dark-soft";
}

const initialState: ThemeState = {
  mode: getInitialThemeMode(),
};

/** 主題狀態 Slice。 */
const themeSlice = createSlice({
  name: "theme",
  initialState,
  reducers: {
    setTheme: (state, action: { payload: ThemeState["mode"] }) => {
      state.mode = action.payload;
      localStorage.setItem(THEME_STORAGE_KEY, state.mode);
      document.documentElement.setAttribute("data-theme", state.mode);
    },
    toggleTheme: (state) => {
      state.mode = state.mode === "light-soft" ? "dark-soft" : "light-soft";
      localStorage.setItem(THEME_STORAGE_KEY, state.mode);
      document.documentElement.setAttribute("data-theme", state.mode);
    },
  },
});

export const { toggleTheme, setTheme } = themeSlice.actions;
export default themeSlice.reducer;
