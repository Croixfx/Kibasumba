import { useState } from 'react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

import { api, errorMessage, setToken } from '../lib/api.js';

export default function LoginPage() {
  const navigate = useNavigate();
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await api.post('/api/auth/login/', {
        phone_number: phone.trim(),
        password,
      });
      setToken(data.token);
      // Fetch role now so the guard's decision is instant; the guard
      // re-checks on every protected route anyway.
      await api.get('/api/auth/me/');
      navigate('/dashboard', { replace: true });
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 p-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm rounded-2xl bg-white p-8 shadow-lg"
      >
        <h1 className="mb-8 text-center text-3xl font-extrabold tracking-wide text-teal-700">
          KIBASUMBA
        </h1>

        <label className="mb-1 block text-sm font-medium text-gray-700">
          Nimero ya telefoni / Phone number
        </label>
        <input
          type="tel"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          placeholder="07XXXXXXXX"
          className="mb-4 w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-200"
          required
        />

        <label className="mb-1 block text-sm font-medium text-gray-700">
          Ijambo ry'ibanga / Password
        </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mb-6 w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-200"
          required
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-teal-600 py-2.5 font-semibold text-white transition hover:bg-teal-700 disabled:opacity-60"
        >
          {loading ? 'Tegereza...' : 'Injira / Login'}
        </button>
      </form>
    </div>
  );
}
