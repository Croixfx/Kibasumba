import { useState } from 'react';
import toast from 'react-hot-toast';

import { api, errorMessage } from '../lib/api.js';

/**
 * Left section of the dashboard: search a woman by phone; if she does not
 * exist, register her inline and load her (empty) record.
 */
export default function SearchRegister({ initialPhone = '', onRecordLoaded }) {
  const [phone, setPhone] = useState(initialPhone);
  const [fullName, setFullName] = useState('');
  const [showRegister, setShowRegister] = useState(false);
  const [loading, setLoading] = useState(false);

  async function loadRecord(phoneNumber) {
    const { data } = await api.get('/api/pregnancy/midwife/woman-record/', {
      params: { phone: phoneNumber },
    });
    onRecordLoaded(data);
  }

  async function handleSearch(e) {
    e.preventDefault();
    setShowRegister(false);
    setLoading(true);
    try {
      await loadRecord(phone.trim());
    } catch (err) {
      if (err?.response?.status === 404) {
        setShowRegister(true);
      } else {
        toast.error(errorMessage(err));
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister(e) {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/api/auth/midwife/create-woman/', {
        phone_number: phone.trim(),
        full_name: fullName.trim(),
      });
      toast.success('Yanditswe — SMS yoherejwe');
      setShowRegister(false);
      await loadRecord(phone.trim());
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-2xl bg-white p-6 shadow">
      <h2 className="mb-4 text-lg font-bold text-gray-800">
        Shakisha / Andikisha Umubyeyi
      </h2>

      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="tel"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          placeholder="07XXXXXXXX"
          className="min-w-0 flex-1 rounded-lg border border-gray-300 px-4 py-2.5 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-200"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-teal-600 px-5 py-2.5 font-semibold text-white hover:bg-teal-700 disabled:opacity-60"
        >
          Shakisha
        </button>
      </form>

      {showRegister && (
        <form
          onSubmit={handleRegister}
          className="mt-4 rounded-xl border border-dashed border-teal-400 bg-teal-50 p-4"
        >
          <p className="mb-3 text-sm text-gray-700">
            Nta mubyeyi ufite iyi nimero. Mwandikishe:
          </p>
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Amazina yose / Full name"
            className="mb-3 w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-200"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-teal-600 py-2.5 font-semibold text-white hover:bg-teal-700 disabled:opacity-60"
          >
            Andikisha
          </button>
        </form>
      )}
    </div>
  );
}
