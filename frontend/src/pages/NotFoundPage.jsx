import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return <main className="grid min-h-screen place-items-center bg-canvas p-6 text-center"><div><p className="text-sm font-semibold text-terracotta">404</p><h1 className="mt-2 text-3xl font-bold text-ink">Page not found</h1><p className="mt-3 text-muted">This route does not exist in DocuMind AI.</p><Link className="mt-6 inline-flex rounded-xl bg-terracotta px-4 py-2.5 text-sm font-medium text-white" to="/chat">Go to chat</Link></div></main>;
}
