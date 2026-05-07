import { ReactNode, useEffect } from "react";

interface ProtectedRouteProps {
  isAuthenticated: boolean;
  initialized: boolean;
  onUnauthorized: () => void;
  children: ReactNode;
}

/** 受保護路由：未登入時導回首頁登入。 */
export function ProtectedRoute({ isAuthenticated, initialized, onUnauthorized, children }: ProtectedRouteProps) {
  useEffect(() => {
    if (initialized && !isAuthenticated) {
      onUnauthorized();
    }
  }, [initialized, isAuthenticated, onUnauthorized]);

  if (!initialized) {
    return <main className="auth-shell">正在初始化登入狀態...</main>;
  }

  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
