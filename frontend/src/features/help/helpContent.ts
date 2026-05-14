/** Help 頁 FAQ 條目。 */
export interface HelpFaqItem {
  question: string;
  answer: string;
}

export const HELP_FAQ_ITEMS: HelpFaqItem[] = [
  {
    question: "AI 辨識不準怎麼辦？",
    answer: "請改用更清晰的單一食材照片，並手動修正食材清單結果後再存入庫存。",
  },
  {
    question: "食譜為什麼有時候重複？",
    answer: "AI 會依現有食材與偏好生成建議，若食材組合相近，內容可能出現重複。",
  },
  {
    question: "Email 沒收到怎麼辦？",
    answer:
      "可先到「系統設定 > 即將到期 Email 提醒 > 最近寄送紀錄」確認狀態。寄送紀錄僅保留最近 7 天，並在每天上午 8:00 清理舊紀錄。",
  },
  {
    question: "如何修改提醒設定？",
    answer: "請到 「系統設定」 的「即將到期 Email 提醒」變更，可選擇「不提醒」、「前 1 天」或「前 3 天」後至下方儲存設定。",
  },
];
