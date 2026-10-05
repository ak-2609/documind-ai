import { useAuth } from "@clerk/react";
import { Navigate, useLocation } from "react-router-dom";

import LoadingSpinner from "../components/LoadingSpinner";

export default function ProtectedRoute({ children }) {
  const { isLoaded, isSignedIn } = useAuth();
  const location = useLocation();
  if (!isLoaded) return <main className="grid min-h-screen place-items-center"><LoadingSpinner label="Loading authentication…" /></main>;
  if (!isSignedIn) return <Navigate to="/sign-in" replace state={{ from: location.pathname }} />;
  return children;
}
