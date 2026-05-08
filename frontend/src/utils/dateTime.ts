/**
 * 將 ISO datetime 字串格式化為使用者瀏覽器本地時間。
 * 若值為空或無法解析，回傳「-」避免畫面錯誤。
 */
export function formatLocalDateTime(dateTime: string | null | undefined): string {
  if (!dateTime) {
    return "-";
  }

  const parsed = new Date(dateTime);
  if (Number.isNaN(parsed.getTime())) {
    return "-";
  }

  return new Intl.DateTimeFormat("zh-TW", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(parsed);
}
