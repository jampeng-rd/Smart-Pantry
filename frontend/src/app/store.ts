import { configureStore } from "@reduxjs/toolkit";

import authReducer from "../features/auth/authSlice";
import expirationReducer from "../features/expiration/expirationSlice";
import nutritionReducer from "../features/nutrition/nutritionSlice";
import ocrReducer from "../features/ocr/ocrSlice";
import pantryReducer from "../features/pantry/pantrySlice";
import recipesReducer from "../features/recipes/recipeSlice";
import shoppingReducer from "../features/shopping/shoppingSlice";
import themeReducer from "../features/theme/themeSlice";

/** 建立 Redux 全域狀態管理。 */
export const store = configureStore({
  reducer: {
    auth: authReducer,
    pantry: pantryReducer,
    expiration: expirationReducer,
    shopping: shoppingReducer,
    recipes: recipesReducer,
    ocr: ocrReducer,
    nutrition: nutritionReducer,
    theme: themeReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
