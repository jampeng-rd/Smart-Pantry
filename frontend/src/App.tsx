import { useEffect, useMemo, useState } from "react";

import { useAppDispatch, useAppSelector } from "./app/hooks";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AppLayout } from "./components/layout/AppLayout";
import { initializeAuth } from "./features/auth/authSlice";
import { DashboardPage } from "./pages/DashboardPage";
import { ExpirationPage } from "./pages/ExpirationPage";
import { IngredientsPage } from "./pages/IngredientsPage";
import { LoginPage } from "./pages/LoginPage";
import { ForgotPasswordPage } from "./pages/ForgotPasswordPage";
import { NutritionPage } from "./pages/NutritionPage";
import { PantryPage } from "./pages/PantryPage";
import { RecipesPage } from "./pages/RecipesPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ResetPasswordPage } from "./pages/ResetPasswordPage";
import { SettingsPage } from "./pages/SettingsPage";
import { ShoppingPage } from "./pages/ShoppingPage";
import { ProfilePage } from "./pages/ProfilePage";
import { HelpPage } from "./pages/HelpPage";

type AuthViewMode = "login" | "register" | "forgot-password" | "reset-password";
type ProtectedPath =
  | "/dashboard"
  | "/pantry"
  | "/expiration"
  | "/shopping"
  | "/recipes"
  | "/ingredients"
  | "/nutrition"
  | "/settings"
  | "/profile"
  | "/help";

const protectedRoutes: ProtectedPath[] = [
  "/dashboard",
  "/pantry",
  "/expiration",
  "/shopping",
  "/recipes",
  "/ingredients",
  "/nutrition",
  "/settings",
  "/profile",
  "/help",
];

/** 前端入口：處理 Auth UI 與受保護路由。 */
function App() {
  const dispatch = useAppDispatch();
  const auth = useAppSelector((state) => state.auth);
  const [pathname, setPathname] = useState(window.location.pathname);
  const [authViewMode, setAuthViewMode] = useState<AuthViewMode>("login");
  const tokenFromUrl = useMemo(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get("token") ?? "";
  }, []);

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

  useEffect(() => {
    if (pathname === "/forgot-password") {
      setAuthViewMode("forgot-password");
      return;
    }
    if (pathname === "/reset-password") {
      setAuthViewMode("reset-password");
      return;
    }
    if (pathname === "/register") {
      setAuthViewMode("register");
      return;
    }
    setAuthViewMode("login");
  }, [pathname]);

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
          onShowRegister={() => navigateTo("/register", false, setPathname)}
          onShowForgotPassword={() => navigateTo("/forgot-password", false, setPathname)}
        />
      ) : authViewMode === "register" ? (
        <RegisterPage
          onRegistered={() => navigateTo("/pantry", false, setPathname)}
          onShowLogin={() => navigateTo("/", false, setPathname)}
        />
      ) : authViewMode === "forgot-password" ? (
        <ForgotPasswordPage
          onBackToLogin={() => navigateTo("/", false, setPathname)}
          onShowResetPassword={() => navigateTo("/reset-password", false, setPathname)}
        />
      ) : (
        <ResetPasswordPage tokenFromUrl={tokenFromUrl} onBackToLogin={() => navigateTo("/", false, setPathname)} />
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
    case "/ingredients":
      return <IngredientsPage />;
    case "/nutrition":
      return <NutritionPage />;
    case "/settings":
      return <SettingsPage />;
    case "/profile":
      return <ProfilePage />;
    case "/help":
      return <HelpPage />;
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
