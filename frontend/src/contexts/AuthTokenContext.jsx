import { useAuth } from "@clerk/react";
import { useEffect } from "react";

import { configureAuthTokenProvider } from "../api/client";

export function AuthTokenProvider({ children }) {
  const { getToken } = useAuth();
  const template = import.meta.env.VITE_CLERK_JWT_TEMPLATE?.trim();

  useEffect(() => {
    configureAuthTokenProvider(async () => getToken(template ? { template } : undefined));
    return () => configureAuthTokenProvider(null);
  }, [getToken, template]);

  return children;
}
