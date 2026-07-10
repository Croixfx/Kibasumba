import { useNavigate } from 'react-router-dom';

import { clearToken } from '../lib/api.js';
import { useMe } from './RoleGuard.jsx';

export default function TopBar() {
  const me = useMe();
  const navigate = useNavigate();

  function logout() {
    clearToken();
    navigate('/login', { replace: true });
  }

  return (
    <header className="flex items-center justify-between bg-teal-700 px-4 py-3 text-white shadow md:px-8">
      <span className="text-lg font-extrabold tracking-wide">
        KIBASUMBA Admin
      </span>
      <div className="flex items-center gap-3">
        <span className="hidden text-sm sm:inline">{me.phone_number}</span>
        <span className="rounded-full bg-teal-900 px-3 py-1 text-xs font-semibold uppercase">
          {me.role}
        </span>
        <button
          onClick={logout}
          className="rounded-lg bg-white/15 px-3 py-1.5 text-sm font-medium hover:bg-white/25"
        >
          Gusohoka
        </button>
      </div>
    </header>
  );
}
