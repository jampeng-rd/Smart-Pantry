import { FiActivity, FiMoon, FiSun } from "react-icons/fi";

import { useAppDispatch, useAppSelector } from "./app/hooks";
import { toggleTheme } from "./features/theme/themeSlice";

/** Phase 01 首頁，提供基礎狀態與主題切換。 */
function App() {
  const dispatch = useAppDispatch();
  const theme = useAppSelector((state) => state.theme.mode);

  return (
    <main className="app-shell">
      <header className="app-header">
        <h1>智慧食材保存與膳食管理系統</h1>
        <p>Phase 01：專案初始化</p>
      </header>

      <section className="card">
        <h2>
          <FiActivity aria-hidden="true" /> 系統狀態
        </h2>
        <p>前端基礎架構已啟動，後續階段將逐步加入功能模組。</p>
        <button
          type="button"
          className="btn"
          onClick={() => dispatch(toggleTheme())}
          aria-label="切換主題"
        >
          {theme === "light-soft" ? <FiMoon aria-hidden="true" /> : <FiSun aria-hidden="true" />}
          切換主題（{theme}）
        </button>
      </section>
    </main>
  );
}

export default App;
