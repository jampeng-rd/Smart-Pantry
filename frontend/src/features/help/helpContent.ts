/** Help 頁 FAQ 條目。 */
export interface HelpFaqItem {
  question: string;
  answer: string;
}

export const HELP_FAQ_ITEMS: HelpFaqItem[] = [
  {
    question: "AI 辨識不準怎麼辦？",
    answer: "請改用更清晰的單一食材照片，並手動修正候選結果後再寫入庫存。",
  },
  {
    question: "食譜為什麼有時候重複？",
    answer: "AI 會依現有食材與偏好生成建議，若食材組合相近，內容可能出現重複。",
  },
  {
    question: "Email 沒收到怎麼辦？",
    answer:
      "可先到「系統設定 > 到期 Email 提醒 > 最近寄送紀錄」確認狀態。寄送紀錄僅保留最近 7 天，並在每天上午 8:00 runner 順便清理舊紀錄。Phase 10-3 仍使用 fake email client，紀錄不代表真的寄出；真實 provider 會在後續 Production Infrastructure / External Services 階段串接。",
  },
  {
    question: "如何修改提醒設定？",
    answer: "請到 Settings 的「到期 Email 提醒」區塊，選擇不提醒、前 1 天或前 3 天後儲存。",
  },
];
