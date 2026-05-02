import { Suspense, lazy } from "react";
import { Link, Route, Routes } from "react-router-dom";

const DashboardPage = lazy(() =>
  import("./pages/DashboardPage").then((module) => ({ default: module.DashboardPage })),
);
const WelcomePage = lazy(() =>
  import("./pages/WelcomePage").then((module) => ({ default: module.WelcomePage })),
);

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
        <Suspense
          fallback={
            <div className="mx-auto flex min-h-[calc(100vh-73px)] max-w-6xl items-center px-6 py-16 text-sm text-slate-400">
              Loading interface...
            </div>
          }
        >
          <Routes>
            <Route path="/" element={<WelcomePage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
          </Routes>
        </Suspense>
      </main>
    </div>
  );
}
