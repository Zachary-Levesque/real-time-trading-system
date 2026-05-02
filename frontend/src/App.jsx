import { Link, Route, Routes } from "react-router-dom";

import { DashboardPage } from "./pages/DashboardPage";
import { WelcomePage } from "./pages/WelcomePage";

export default function App() {
  return (
    <div className="min-h-screen bg-ink text-white">
      <header className="border-b border-white/10 bg-slate-950/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link to="/" className="text-sm font-semibold uppercase tracking-[0.3em] text-mist">
            Real-Time Trading System
          </Link>
          <nav className="flex gap-6 text-sm text-slate-300">
            <Link to="/" className="transition hover:text-white">
              Welcome
            </Link>
            <Link to="/dashboard" className="transition hover:text-white">
              Dashboard
            </Link>
          </nav>
        </div>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<WelcomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </main>
    </div>
  );
}

