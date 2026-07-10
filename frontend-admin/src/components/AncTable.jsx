import { useState } from 'react';
import toast from 'react-hot-toast';

import { api, errorMessage } from '../lib/api.js';
import Collapsible from './Collapsible.jsx';

const FIELDS = [
  { key: 'visit_date', label: 'Itariki asuzumiweho', type: 'date' },
  { key: 'mother_weight_kg', label: 'Ibiro (kg)', type: 'number' },
  { key: 'mother_height_cm', label: 'Uburebure (cm)', type: 'number' },
  { key: 'fetal_position', label: 'Uko umwana ameze mu nda', type: 'text' },
  { key: 'fetal_heartbeat', label: "Gutera k'umutima", type: 'text' },
  { key: 'next_visit_date', label: 'Itariki azagarukira', type: 'date' },
  { key: 'notes', label: 'Icyitonderwa', type: 'text', wide: true },
];

function emptyRow(visitNumber) {
  return {
    visit_number: visitNumber,
    visit_date: '',
    mother_weight_kg: '',
    mother_height_cm: '',
    fetal_position: '',
    fetal_heartbeat: '',
    next_visit_date: '',
    notes: '',
  };
}

function buildRows(visits) {
  const byNumber = Object.fromEntries(visits.map((v) => [v.visit_number, v]));
  return Array.from({ length: 8 }, (_, i) => {
    const saved = byNumber[i + 1];
    return saved
      ? {
          ...emptyRow(i + 1),
          ...Object.fromEntries(
            Object.entries(saved).map(([k, v]) => [k, v ?? '']),
          ),
        }
      : emptyRow(i + 1);
  });
}

/**
 * Section B — "Kwipimisha Inda": one card per visit (8 total). Cards use a
 * responsive field grid so the page never scrolls horizontally.
 */
export default function AncTable({ woman, hasPregnancy, visits }) {
  const [rows, setRows] = useState(() => buildRows(visits));
  const [savingRow, setSavingRow] = useState(null);

  function setCell(index, key, value) {
    setRows((rs) => rs.map((r, i) => (i === index ? { ...r, [key]: value } : r)));
  }

  async function saveRow(index) {
    const row = rows[index];
    setSavingRow(index);
    try {
      const payload = { phone_number: woman.phone_number };
      for (const [key, value] of Object.entries(row)) {
        payload[key] = value === '' ? null : value;
      }
      // Text fields must be "" not null for DRF blank CharFields.
      for (const key of ['fetal_position', 'fetal_heartbeat', 'notes']) {
        payload[key] = row[key] ?? '';
      }
      const { data } = await api.post(
        '/api/pregnancy/midwife/anc-visit/',
        payload,
      );
      setRows((rs) =>
        rs.map((r, i) =>
          i === index
            ? {
                ...r,
                ...Object.fromEntries(
                  Object.entries(data).map(([k, v]) => [k, v ?? '']),
                ),
              }
            : r,
        ),
      );
      toast.success(`Inshuro ya ${row.visit_number} yabitswe`);
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setSavingRow(null);
    }
  }

  return (
    <Collapsible title="Kwipimisha Inda">
      {!hasPregnancy && (
        <p className="mb-4 rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Banza ubike Umwirondoro (Section A) mbere yo kwandika ibipimo.
        </p>
      )}
      <div className="space-y-4">
        {rows.map((row, index) => {
          const completed = Boolean(row.visit_date);
          return (
            <div
              key={row.visit_number}
              className={`rounded-xl border-l-4 bg-gray-50 p-4 ${
                completed ? 'border-green-500' : 'border-gray-300 opacity-70'
              }`}
            >
              <div className="mb-3 flex items-center justify-between gap-2">
                <span className="font-semibold text-gray-800">
                  Inshuro ya {row.visit_number}
                </span>
                <button
                  type="button"
                  onClick={() => saveRow(index)}
                  disabled={!hasPregnancy || savingRow === index}
                  className="rounded-md bg-teal-600 px-4 py-1.5 text-sm font-semibold text-white hover:bg-teal-700 disabled:opacity-50"
                >
                  {savingRow === index ? '...' : 'Bika'}
                </button>
              </div>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-3">
                {FIELDS.map((f) => (
                  <div key={f.key} className={f.wide ? 'sm:col-span-2 md:col-span-3' : ''}>
                    <label className="mb-1 block text-xs font-medium text-gray-500">
                      {f.label}
                    </label>
                    <input
                      type={f.type}
                      step={f.type === 'number' ? '0.1' : undefined}
                      value={row[f.key]}
                      onChange={(e) => setCell(index, f.key, e.target.value)}
                      disabled={!hasPregnancy}
                      className="w-full rounded-md border border-gray-300 bg-white px-2 py-1.5 text-sm focus:border-teal-500 focus:outline-none disabled:bg-gray-100"
                    />
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </Collapsible>
  );
}
