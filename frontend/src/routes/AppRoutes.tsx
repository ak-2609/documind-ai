import { Navigate, Route, Routes } from "react-router-dom";
import { SignIn, SignUp } from "@clerk/react";
import ProtectedRoute from "./ProtectedRoute";
import WorkspacePage from "../pages/WorkspacePage";
import NotFoundPage from "../pages/NotFoundPage";
export default function AppRoutes() { return <Routes><Route path="/sign-in/*" element={<main className="auth-page"><SignIn routing="path" path="/sign-in" signUpUrl="/sign-up" forceRedirectUrl="/chat" /></main>} /><Route path="/sign-up/*" element={<main className="auth-page"><SignUp routing="path" path="/sign-up" signInUrl="/sign-in" forceRedirectUrl="/chat" /></main>} /><Route path="/chat" element={<ProtectedRoute><WorkspacePage /></ProtectedRoute>} /><Route path="/" element={<Navigate to="/chat" replace />} /><Route path="*" element={<NotFoundPage />} /></Routes>; }
