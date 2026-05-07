import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { authApi, refreshTokensOrThrow } from "../../services/apiClient";
import { clearTokens, getAccessToken, getRefreshToken, hasTokens, saveTokens } from "../../services/tokenService";
import type { AuthState, LoginPayload, RegisterPayload, UserProfile } from "./authTypes";

const initialState: AuthState = {
  user: null,
  accessToken: null,
  isAuthenticated: false,
  loading: false,
  initialized: false,
  error: null,
};

/** 初始化登入狀態（重新整理後恢復 session）。 */
export const initializeAuth = createAsyncThunk<UserProfile | null, void, { rejectValue: string }>(
  "auth/initializeAuth",
  async (_, { rejectWithValue }) => {
    if (!hasTokens()) {
      return null;
    }

    try {
      await refreshTokensOrThrow();
      const meData = await authApi.me();
      return meData.user;
    } catch (error) {
      clearTokens();
      return rejectWithValue(getErrorMessage(error));
    }
  },
);

/** 登入並取得目前使用者資訊。 */
export const login = createAsyncThunk<UserProfile, LoginPayload, { rejectValue: string }>(
  "auth/login",
  async (payload, { rejectWithValue }) => {
    try {
      const tokenData = await authApi.login(payload);
      saveTokens(tokenData.access_token, tokenData.refresh_token);
      const meData = await authApi.me();
      return meData.user;
    } catch (error) {
      clearTokens();
      return rejectWithValue(getErrorMessage(error));
    }
  },
);

/** 註冊成功後自動登入。 */
export const register = createAsyncThunk<UserProfile, RegisterPayload, { rejectValue: string }>(
  "auth/register",
  async (payload, { rejectWithValue }) => {
    try {
      await authApi.register(payload);
      const tokenData = await authApi.login({ email: payload.email, password: payload.password });
      saveTokens(tokenData.access_token, tokenData.refresh_token);
      const meData = await authApi.me();
      return meData.user;
    } catch (error) {
      clearTokens();
      return rejectWithValue(getErrorMessage(error));
    }
  },
);

/** 登出並清除本地 token。 */
export const logout = createAsyncThunk<void, void, { rejectValue: string }>("auth/logout", async (_, { rejectWithValue }) => {
  const refreshToken = getRefreshToken();

  try {
    if (refreshToken) {
      await authApi.logout({ refresh_token: refreshToken });
    }
  } catch (error) {
    clearTokens();
    return rejectWithValue(getErrorMessage(error));
  }

  clearTokens();
});

/** Auth 狀態 Slice。 */
const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    clearAuthError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(initializeAuth.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(initializeAuth.fulfilled, (state, action) => {
        state.loading = false;
        state.initialized = true;
        if (state.isAuthenticated && state.user && state.accessToken) {
          return;
        }
        state.user = action.payload;
        state.accessToken = getAccessToken();
        state.isAuthenticated = Boolean(action.payload && state.accessToken);
      })
      .addCase(initializeAuth.rejected, (state, action) => {
        state.loading = false;
        state.initialized = true;
        if (state.isAuthenticated && state.user && state.accessToken) {
          return;
        }
        state.user = null;
        state.accessToken = null;
        state.isAuthenticated = false;
        state.error = action.payload ?? "初始化登入狀態失敗";
      })
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.initialized = true;
        state.user = action.payload;
        state.accessToken = getAccessToken();
        state.isAuthenticated = true;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.user = null;
        state.accessToken = null;
        state.isAuthenticated = false;
        state.error = action.payload ?? "登入失敗";
      })
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.loading = false;
        state.initialized = true;
        state.user = action.payload;
        state.accessToken = getAccessToken();
        state.isAuthenticated = true;
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.user = null;
        state.accessToken = null;
        state.isAuthenticated = false;
        state.error = action.payload ?? "註冊失敗";
      })
      .addCase(logout.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(logout.fulfilled, (state) => {
        state.loading = false;
        state.user = null;
        state.accessToken = null;
        state.isAuthenticated = false;
      })
      .addCase(logout.rejected, (state, action) => {
        state.loading = false;
        state.user = null;
        state.accessToken = null;
        state.isAuthenticated = false;
        state.error = action.payload ?? "登出失敗";
      });
  },
});

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return "發生未知錯誤";
}

export const { clearAuthError } = authSlice.actions;
export default authSlice.reducer;
