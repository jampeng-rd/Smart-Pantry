import { useEffect, useMemo, useState } from "react";

import { useAppDispatch, useAppSelector } from "./app/hooks";
import { ProtectedLayout } from "./components/ProtectedLayout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { initializeAuth } from "./features/auth/authSlice";
import { DashboardPlaceholderPage } from "./pages/DashboardPlaceholderPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";

type AuthViewMode = "login" | "register";

/** 前端入口：處理 Auth UI 與受保護路由。 */
function App() {
  const dispatch = useAppDispatch();
  const auth = useAppSelector((state) => state.auth);
  const [pathname, setPathname] = useState(window.location.pathname);
  const [authViewMode, setAuthViewMode] = useState<AuthViewMode>("login");

  useEffect(() => {
    void dispatch(initializeAuth());
  }, [dispatch]);

  useEffect(() => {
    const onPopState = () => setPathname(window.location.pathname);
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  useEffect(() => {
    if (auth.initialized && auth.isAuthenticated && pathname === "/") {
      navigateTo("/dashboard", true, setPathname);
    }
  }, [auth.initialized, auth.isAuthenticated, pathname]);

  const isDashboardRoute = useMemo(() => pathname === "/dashboard", [pathname]);

  if (isDashboardRoute) {
    return (
      <ProtectedRoute
        initialized={auth.initialized}
        isAuthenticated={auth.isAuthenticated}
        onUnauthorized={() => navigateTo("/", true, setPathname)}
      >
        <ProtectedLayout onLoggedOut={() => navigateTo("/", true, setPathname)}>
          <DashboardPlaceholderPage />
        </ProtectedLayout>
      </ProtectedRoute>
    );
  }

  return (
    <main className="auth-shell">
      {authViewMode === "login" ? (
        <LoginPage
          onLoggedIn={() => navigateTo("/dashboard", false, setPathname)}
          onShowRegister={() => setAuthViewMode("register")}
        />
      ) : (
        <RegisterPage
          onRegistered={() => navigateTo("/dashboard", false, setPathname)}
          onShowLogin={() => setAuthViewMode("login")}
        />
      )}
    </main>
  );
}

function navigateTo(path: string, replace: boolean, setPathname: (path: string) => void): void {
  if (window.location.pathname === path) {
    setPathname(path);
    return;
  }

  if (replace) {
    window.history.replaceState({}, "", path);
  } else {
    window.history.pushState({}, "", path);
  }
  setPathname(path);
}

export default App;
