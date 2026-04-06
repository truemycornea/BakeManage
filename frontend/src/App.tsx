import { Suspense, lazy } from "react";
import { Routes, Route, NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import LanguageSwitcher from "./components/LanguageSwitcher";

const Dashboard = lazy(() => import("./pages/Dashboard"));
const POS = lazy(() => import("./pages/POS"));
const Inventory = lazy(() => import("./pages/Inventory"));
const Telemetry = lazy(() => import("./pages/Telemetry"));
const Analytics = lazy(() => import("./pages/Analytics"));
const Admin = lazy(() => import("./pages/Admin"));

export default function App() {
  const { t } = useTranslation();
  return (
    <div style={{ fontFamily: "sans-serif" }}>
      <header style={{ background: "#1a1a2e", color: "#fff", padding: "0.75rem 1.5rem", display: "flex", alignItems: "center", gap: "1.5rem" }}>
        <strong>{t("app_title")}</strong>
        <nav style={{ display: "flex", gap: "1rem" }}>
          {(["dashboard", "pos", "inventory", "telemetry", "analytics", "admin"] as const).map((key) => (
            <NavLink
              key={key}
              to={`/${key === "dashboard" ? "" : key}`}
              style={({ isActive }) => ({ color: isActive ? "#f5c518" : "#ccc", textDecoration: "none" })}
            >
              {t(`nav.${key}`)}
            </NavLink>
          ))}
        </nav>
        <div style={{ marginLeft: "auto" }}>
          <LanguageSwitcher />
        </div>
      </header>
      <main style={{ padding: "1.5rem" }}>
        <Suspense fallback={<div>{t("common.loading")}</div>}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/pos" element={<POS />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/telemetry" element={<Telemetry />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </Suspense>
      </main>
    </div>
  );
}
