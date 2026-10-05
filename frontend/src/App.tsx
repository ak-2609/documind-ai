import { AuthTokenProvider } from "./contexts/AuthTokenContext";
import AppRoutes from "./routes/AppRoutes";
export default function App() { return <AuthTokenProvider><AppRoutes /></AuthTokenProvider>; }
