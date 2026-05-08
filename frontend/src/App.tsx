import { useEffect, useMemo, useState } from "react";

import { useAppDispatch, useAppSelector } from "./app/hooks";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AppLayout } from "./components/layout/AppLayout";
import { initializeAuth } from "./features/auth/authSlice";
import { DashboardPage } from "./pages/DashboardPage";
import { ExpirationPage } from "./pages/ExpirationPage";
import { LoginPage } from "./pages/LoginPage";
import { NutritionPage } from "./pages/NutritionPage";
import { OCRPage } from "./pages/OCRPage";
import { PantryPage } from "./pages/PantryPage";
import { RecipesPage } from "./pages/RecipesPage";
import { RegisterPage } from "./pages/RegisterPage";
import { SettingsPage } from "./pages/SettingsPage";
import { ShoppingPage } from "./pages/ShoppingPage";

type AuthViewMode = "login" | "register";
type ProtectedPath =
  | "/dashboard"
  | "/pantry"
  | "/expiration"
  | "/shopping"
  | "/recipes"
  | "/ocr"
  | "/nutrition"
  | "/settings";

const protectedRoutes: ProtectedPath[] = [
  "/dashboard",
  "/pantry",
  "/expiration",
  "/shopping",
  "/recipes",
  "/ocr",
  "/nutrition",
  "/settings",
];

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
      navigateTo("/pantry", true, setPathname);
    }
  }, [auth.initialized, auth.isAuthenticated, pathname]);

  const isProtectedRoute = useMemo(() => protectedRoutes.includes(pathname as ProtectedPath), [pathname]);

  if (isProtectedRoute) {
    return (
      <ProtectedRoute
        initialized={auth.initialized}
        isAuthenticated={auth.isAuthenticated}
        onUnauthorized={() => navigateTo("/", true, setPathname)}
      >
        <AppLayout pathname={pathname} onNavigate={(path) => navigateTo(path, false, setPathname)}>
          <WorkspaceByPath pathname={pathname as ProtectedPath} />
        </AppLayout>
      </ProtectedRoute>
    );
  }

  return (
    <main className="auth-shell">
      {authViewMode === "login" ? (
        <LoginPage
          onLoggedIn={() => navigateTo("/pantry", false, setPathname)}
          onShowRegister={() => setAuthViewMode("register")}
        />
      ) : (
        <RegisterPage
          onRegistered={() => navigateTo("/pantry", false, setPathname)}
          onShowLogin={() => setAuthViewMode("login")}
        />
      )}
    </main>
  );
}

function WorkspaceByPath({ pathname }: { pathname: ProtectedPath }) {
  switch (pathname) {
    case "/dashboard":
      return <DashboardPage />;
    case "/pantry":
      return <PantryPage />;
    case "/expiration":
      return <ExpirationPage />;
    case "/shopping":
      return <ShoppingPage />;
    case "/recipes":
      return <RecipesPage />;
    case "/ocr":
      return <OCRPage />;
    case "/nutrition":
      return <NutritionPage />;
    case "/settings":
      return <SettingsPage />;
    default:
      return <DashboardPage />;
  }
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
