import { createSlice } from "@reduxjs/toolkit";

import type { AuthState } from "./authTypes";

const initialState: AuthState = {
  isAuthenticated: false,
  loading: false,
  error: null,
};

/** Auth 狀態 Slice（Phase 01 僅保留骨架）。 */
const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {},
});

export default authSlice.reducer;
