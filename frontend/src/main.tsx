import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";

import App from "./App";
import { store } from "./app/store";
import "./styles/globals.css";
import "./styles/theme.css";

const savedTheme = localStorage.getItem("smartpantry_theme_mode");
const themeMode = savedTheme === "dark-soft" || savedTheme === "light-soft" ? savedTheme : "light-soft";
document.documentElement.setAttribute("data-theme", themeMode);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>,
);
