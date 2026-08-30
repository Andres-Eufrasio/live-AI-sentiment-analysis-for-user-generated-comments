import { useEffect, useState } from "react";
import ModerationDashboard from "./Components/ModerationDashboard.jsx";
import Settings from "./Components/Settings.jsx";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import AuditLog from "./Components/AuditLog.jsx";
import "./App.css";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("moderator-theme") || "cappuccino";
  });

  useEffect(() => {
    localStorage.setItem("moderator-theme", theme);
  }, [theme]);

  return (
    <BrowserRouter>
      <div className={`app theme-${theme}`}>
        {/* Top Bar */}
        <header className="topbar">
          <div className="topbar-title">
            <button
              className="sidebar-toggle"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              aria-label="Toggle sidebar"
            >
              ☰
            </button>

            <h1>Moderator tools</h1>
          </div>

          <div className="moderator-user">
            <span className="user-avatar">M</span>
            <span className="username">Moderator</span>
          </div>
        </header>


        {/* Sidebar */}
        <aside className={`sidebar ${sidebarOpen ? "open" : "closed"}`}>
          <div className="sidebar-content">
            <NavLink
              to="/"
              className={({ isActive }) =>
                isActive ? "sidebar-link active" : "sidebar-link"
              }
              title={!sidebarOpen ? "Dashboard" : ""}
            >
              <span className="sidebar-icon">⌂</span>
              {sidebarOpen && <span>Dashboard</span>}
            </NavLink>

            <NavLink
              to="/reviewed"
              className={({ isActive }) =>
                isActive ? "sidebar-link active" : "sidebar-link"
              }
              title={!sidebarOpen ? "Reviewed" : ""}
            >
              <span className="sidebar-icon">✓</span>
              {sidebarOpen && <span>Reviewed</span>}
            </NavLink>

            <NavLink
              to="/analytics"
              className={({ isActive }) =>
                isActive ? "sidebar-link active" : "sidebar-link"
              }
              title={!sidebarOpen ? "Analytics" : ""}
            >
              <span className="sidebar-icon">▥</span>
              {sidebarOpen && <span>Analytics</span>}
            </NavLink>

            <NavLink
              to="/settings"
              className={({ isActive }) =>
                isActive ? "sidebar-link active" : "sidebar-link"
              }
              title={!sidebarOpen ? "Settings" : ""}
            >
              <span className="sidebar-icon">⚙</span>
              {sidebarOpen && <span>Settings</span>}
            </NavLink>
          </div>

          {/* Logout */}
          <div className="sidebar-bottom">
            <button
              className="logout-button"
              type="button"
              onClick={() => {}}
              title={!sidebarOpen ? "Log out" : ""}
            >
              <span className="sidebar-icon">↪</span>
              {sidebarOpen && <span>Log out</span>}
            </button>
          </div>
        </aside>



        {/* Main Content */}
        <main
          className={`main-content ${
            sidebarOpen ? "sidebar-is-open" : "sidebar-is-closed"
          }`}
        >
          <Routes>
            <Route path="/" element={<ModerationDashboard />} />

            <Route
              path="/reviewed"
              element={
                <div className="page-placeholder">
                  <h2>Reviewed</h2>
                  <p>Reviewed comments will appear here.</p>
                </div>
              }
            />

            <Route
              path="/analytics"
              element={
                <div className="page-placeholder">
                  <h2>Analytics</h2>
                  <p>Moderation analytics will appear here.</p>
                </div>
              }
            />

            <Route
              path="/settings"
              element={
                <Settings
                  theme={theme}
                  setTheme={setTheme}
                />
              }
            />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;

