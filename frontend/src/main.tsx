import React from "react";
import ReactDOM from "react-dom/client";
import { ClerkProvider } from "@clerk/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, useNavigate } from "react-router-dom";
import App from "./App";
import "./index.css";
const key = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
if (!key) throw new Error("VITE_CLERK_PUBLISHABLE_KEY is required.");
const client = new QueryClient({ defaultOptions: { queries: { staleTime: 30_000, retry: 1 } } });
function ClerkWithRouter() { const navigate = useNavigate(); return <ClerkProvider publishableKey={key} signInUrl="/sign-in" signUpUrl="/sign-up" signInFallbackRedirectUrl="/chat" signUpFallbackRedirectUrl="/chat" routerPush={(to) => navigate(to)} routerReplace={(to) => navigate(to, { replace: true })}><App /></ClerkProvider>; }
ReactDOM.createRoot(document.getElementById("root")!).render(<React.StrictMode><QueryClientProvider client={client}><BrowserRouter><ClerkWithRouter /></BrowserRouter></QueryClientProvider></React.StrictMode>);
