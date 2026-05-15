import { createSlice } from "@reduxjs/toolkit";

import type { ThemeState } from "./themeTypes";

const THEME_STORAGE_KEY_PREFIX = "smartpantry_theme_mode";
let currentThemeStorageKey = `${THEME_STORAGE_KEY_PREFIX}_guest`;

function readThemeFromStorage(storageKey: string): ThemeState["mode"] | null {
  const savedTheme = localStorage.getItem(storageKey);
  if (savedTheme === "light-soft" || savedTheme === "dark-soft") {
    return savedTheme;
  }
  return null;
}

function getInitialThemeMode(): ThemeState["mode"] {
  const savedTheme = readThemeFromStorage(currentThemeStorageKey);
  if (savedTheme) {
    return savedTheme;
  }
  return "dark-soft";
}

/** 切換 theme localStorage scope（依使用者隔離），並回傳該 scope 目前主題。 */
export function setThemeStorageScope(userId: number | null): ThemeState["mode"] {
  currentThemeStorageKey = userId ? `${THEME_STORAGE_KEY_PREFIX}_user_${userId}` : `${THEME_STORAGE_KEY_PREFIX}_guest`;
  return readThemeFromStorage(currentThemeStorageKey) ?? "dark-soft";
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
      localStorage.setItem(currentThemeStorageKey, state.mode);
      document.documentElement.setAttribute("data-theme", state.mode);
    },
    toggleTheme: (state) => {
      state.mode = state.mode === "light-soft" ? "dark-soft" : "light-soft";
      localStorage.setItem(currentThemeStorageKey, state.mode);
      document.documentElement.setAttribute("data-theme", state.mode);
    },
  },
});

export const { toggleTheme, setTheme } = themeSlice.actions;
export default themeSlice.reducer;
