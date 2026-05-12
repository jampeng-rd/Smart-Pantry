import { FiAlertCircle, FiCamera, FiHelpCircle, FiMail, FiShoppingCart } from "react-icons/fi";

import { HELP_FAQ_ITEMS } from "../features/help/helpContent";

/** Help 說明頁面。 */
export function HelpPage() {
  return (
    <section className="card workspace-card help-page">
      {/* <h2 className="workspace-title">
        <FiHelpCircle aria-hidden="true" /> 使用說明
      </h2> */}

      <h3 className="workspace-subtitle">1. 食材庫存基本使用方式</h3>
      <p>到「食材庫存」新增、編輯與刪除食材，並維持名稱、分類、數量與保存位置的正確性。</p>

      <h3 className="workspace-subtitle">2. 到期提醒說明</h3>
      <p>系統會依食材到期日顯示已過期、即將到期與正常狀態，協助優先消耗即將到期食材。</p>

      <h3 className="workspace-subtitle">3. 購物清單使用方式</h3>
      <p>
        <FiShoppingCart aria-hidden="true" /> 可手動新增購物項目，或從庫存快速加入。標記已購買僅更新購物狀態，不會自動寫入庫存。
      </p>

      <h3 className="workspace-subtitle">4. 食譜建議使用限制</h3>
      <p>AI 食譜結果僅供參考，可能重複或不完全符合需求，請依個人偏好與過敏資訊自行判斷。</p>

      <h3 className="workspace-subtitle">5. 食材辨識拍攝建議</h3>
      <p>
        <FiCamera aria-hidden="true" /> 建議拍攝單一或少量食材，避免整桌料理、冰箱全景與模糊照片，以提高辨識品質。
      </p>

      <h3 className="workspace-subtitle">6. 到期 Email 提醒規則</h3>
      <ul className="help-list">
        <li>不提醒</li>
        <li>前 1 天（預設）</li>
        <li>前 3 天</li>
        <li>未來寄送時間為上午 8:00 與下午 5:00（Phase 10-2 實作）</li>
      </ul>

      <h3 className="workspace-subtitle">7. FAQ</h3>
      <div className="help-faq">
        {HELP_FAQ_ITEMS.map((item) => (
          <article key={item.question} className="help-faq-item">
            <h4>
              <FiAlertCircle aria-hidden="true" /> {item.question}
            </h4>
            <p>{item.answer}</p>
          </article>
        ))}
      </div>

      <p className="muted-text">
        <FiMail aria-hidden="true" /> 若需回報問題，請在專案 issue 或維運通道提供重現步驟與畫面資訊。
      </p>
    </section>
  );
}
