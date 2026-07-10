import { Navigate, Route, Routes } from 'react-router-dom';

import RoleGuard from './components/RoleGuard.jsx';
import { hasToken } from './lib/api.js';
import DashboardPage from './pages/DashboardPage.jsx';
import LoginPage from './pages/LoginPage.jsx';

export default function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={<Navigate to={hasToken() ? '/dashboard' : '/login'} replace />}
      />
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/dashboard"
        element={
          <RoleGuard>
            <DashboardPage />
          </RoleGuard>
        }
      />
      <Route
        path="/patient/:phone"
        element={
          <RoleGuard>
            <DashboardPage />
          </RoleGuard>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
