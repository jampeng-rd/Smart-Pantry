/** OCR 匯入狀態定義。 */
export interface OcrState {
  items: string[];
  page: number;
  pageSize: number;
  total: number;
  loading: boolean;
  error: string | null;
}
