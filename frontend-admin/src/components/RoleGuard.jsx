import { createContext, useContext, useEffect, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';

import { api, clearToken, hasToken } from '../lib/api.js';

const MeContext = createContext(null);

/** The logged-in user's /me/ payload, available inside any guarded page. */
export function useMe() {
  return useContext(MeContext);
}

/**
 * Wraps every protected route: checks the token against GET /api/auth/me/.
 * Women are told this portal is staff-only; midwife/admin pass through;
 * missing/invalid tokens go back to /login.
 */
export default function RoleGuard({ children }) {
  const navigate = useNavigate();
  const [state, setState] = useState({ status: 'loading', me: null });

  useEffect(() => {
    if (!hasToken()) return;
    let cancelled = false;
    api
      .get('/api/auth/me/')
      .then((res) => {
        if (!cancelled) setState({ status: 'ok', me: res.data });
      })
      .catch((err) => {
        if (cancelled) return;
        if (err?.response?.status === 401) {
          clearToken();
          navigate('/login', { replace: true });
        } else {
          setState({ status: 'error', me: null });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [navigate]);

  if (!hasToken()) return <Navigate to="/login" replace />;

  if (state.status === 'loading') {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-teal-600 border-t-transparent" />
      </div>
    );
  }

  if (state.status === 'error') {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-gray-50 p-6 text-center">
        <p className="text-gray-700">
          Ntibyashobotse kugera kuri seriveri. Reba interineti yawe.
        </p>
        <button
          onClick={() => window.location.reload()}
          className="rounded-lg bg-teal-600 px-6 py-2 font-medium text-white hover:bg-teal-700"
        >
          Ongera ugerageze
        </button>
      </div>
    );
  }

  if (state.me.role === 'woman') {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-gray-50 p-6 text-center">
        <p className="max-w-md text-lg font-semibold text-gray-800">
          Uyu murongo wo gukorera abaganga gusa. Injira ukoresheje telefone
          yawe.
        </p>
        <p className="text-sm text-gray-500">
          This portal is for health workers only.
        </p>
        <button
          onClick={() => {
            clearToken();
            navigate('/login', { replace: true });
          }}
          className="rounded-lg bg-teal-600 px-6 py-2 font-medium text-white hover:bg-teal-700"
        >
          Gusohoka / Logout
        </button>
      </div>
    );
  }

  return <MeContext.Provider value={state.me}>{children}</MeContext.Provider>;
}
