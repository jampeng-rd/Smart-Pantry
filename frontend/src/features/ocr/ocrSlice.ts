import { createSlice } from "@reduxjs/toolkit";

import type { OcrState } from "./ocrTypes";

const initialState: OcrState = {
  items: [],
  page: 1,
  pageSize: 10,
  total: 0,
  loading: false,
  error: null,
};

/** OCR 狀態 Slice（Phase 01 僅保留骨架）。 */
const ocrSlice = createSlice({
  name: "ocr",
  initialState,
  reducers: {},
});

export default ocrSlice.reducer;
