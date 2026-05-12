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
    answer: "Phase 10-1 僅儲存提醒偏好，尚未啟用實際寄信，寄送排程會在 Phase 10-2 實作。",
  },
  {
    question: "如何修改提醒設定？",
    answer: "請到 Settings 的「到期 Email 提醒」區塊，選擇不提醒、前 1 天或前 3 天後儲存。",
  },
];
