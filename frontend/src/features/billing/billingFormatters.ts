/** 將會員狀態值轉為繁體中文顯示。 */
export function formatMembershipStatusZh(status: string): string {
  return status === "active" ? "啟用" : "未啟用";
}
