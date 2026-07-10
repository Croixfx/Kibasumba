import { useState } from 'react';
import toast from 'react-hot-toast';

import {
  districtsByProvince,
  hospitalsByDistrict,
  provinces,
} from '../data/rwandaLocations.js';
import { api, errorMessage } from '../lib/api.js';
import {
  calculateEdd,
  formatDdMmYyyy,
  weeksSince,
} from '../utils/eddCalculator.js';
import Collapsible from './Collapsible.jsx';

const PROVISIONS = [
  { key: 'iron_folic', emoji: '💊', label: "Ibinini by'icyuma n'acide folique" },
  { key: 'mebendazole', emoji: '💊', label: 'Mebendazole', minWeek: 12 },
  { key: 'mms', emoji: '💊', label: 'MMS' },
  { key: 'mosquito_net', emoji: '🦟', label: "Urugi rw'inzitiramaraso" },
];

function initialForm(pregnancy, woman) {
  return {
    province: pregnancy?.province ?? '',
    district: pregnancy?.district ?? '',
    hospital: pregnancy?.hospital ?? '',
    health_post: pregnancy?.health_post ?? '',
    full_name: pregnancy?.full_name ?? woman.full_name ?? '',
    age: pregnancy?.age ?? '',
    gravida: pregnancy?.gravida ?? 1,
    parity: pregnancy?.parity ?? 0,
    lmp_date: pregnancy?.lmp_date ?? '',
    is_lmp_estimated: pregnancy?.is_lmp_estimated ?? false,
    iron_folic_given: pregnancy?.iron_folic_given ?? false,
    iron_folic_date: pregnancy?.iron_folic_date ?? '',
    mebendazole_given: pregnancy?.mebendazole_given ?? false,
    mebendazole_date: pregnancy?.mebendazole_date ?? '',
    mms_given: pregnancy?.mms_given ?? false,
    mms_date: pregnancy?.mms_date ?? '',
    mosquito_net_given: pregnancy?.mosquito_net_given ?? false,
    mosquito_net_date: pregnancy?.mosquito_net_date ?? '',
  };
}

const inputCls =
  'w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-200 disabled:bg-gray-100 disabled:text-gray-400';

/** Section A — "Umwirondoro": personal + facility info + provisions. */
export default function SectionA({ woman, pregnancy, onSaved }) {
  const [form, setForm] = useState(() => initialForm(pregnancy, woman));
  const [saving, setSaving] = useState(false);

  const set = (key, value) => setForm((f) => ({ ...f, [key]: value }));

  const edd = calculateEdd(form.lmp_date);
  const week = weeksSince(form.lmp_date);

  function setProvince(value) {
    setForm((f) => ({ ...f, province: value, district: '', hospital: '' }));
  }

  function setDistrict(value) {
    setForm((f) => ({ ...f, district: value, hospital: '' }));
  }

  const districtOptions = form.province
    ? (districtsByProvince[form.province] ?? [])
    : [];
  const hospitalOptions = form.district
    ? [...(hospitalsByDistrict[form.district] ?? [])]
    : [];
  // A stored hospital missing from the hardcoded list must still render.
  if (form.hospital && !hospitalOptions.includes(form.hospital)) {
    hospitalOptions.push(form.hospital);
  }

  async function save() {
    if (!form.province || !form.district || !form.hospital) {
      toast.error("Hitamo intara, akarere n'ivuriro.");
      return;
    }
    if (Number(form.parity) >= Number(form.gravida)) {
      toast.error("Imbyaro zigomba kuba munsi y'inda utwite.");
      return;
    }
    if (!form.lmp_date) {
      toast.error('Hitamo itariki ya LMP.');
      return;
    }
    setSaving(true);
    try {
      const payload = { phone_number: woman.phone_number };
      for (const [key, value] of Object.entries(form)) {
        payload[key] = value === '' && key.endsWith('_date') ? null : value;
      }
      const { data } = await api.post(
        '/api/pregnancy/midwife/create-or-update/',
        payload,
      );
      toast.success('Umwirondoro wabitswe');
      onSaved(data);
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Collapsible title="Umwirondoro">
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-600">
            Intara
          </label>
          <select
            value={form.province}
            onChange={(e) => setProvince(e.target.value)}
            className={inputCls}
          >
            <option value="">— Hitamo —</option>
            {provinces.map((p) => (
              <option key={p}>{p}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-600">
            Akarere
          </label>
          <select
            value={form.district}
            onChange={(e) => setDistrict(e.target.value)}
            disabled={!form.province}
            className={inputCls}
          >
            <option value="">— Hitamo —</option>
            {districtOptions.map((d) => (
              <option key={d}>{d}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-600">
            Ibitaro / Ikigo nderabuzima
          </label>
          <select
            value={form.hospital}
            onChange={(e) => set('hospital', e.target.value)}
            disabled={!form.district}
            className={inputCls}
          >
            <option value="">— Hitamo —</option>
            {hospitalOptions.map((h) => (
              <option key={h}>{h}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-600">
            Ivuriro ry'ibanze (optional)
          </label>
          <input
            type="text"
            value={form.health_post}
            onChange={(e) => set('health_post', e.target.value)}
            className={inputCls}
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-600">
            Amazina yose
          </label>
          <input
            type="text"
            value={form.full_name}
            onChange={(e) => set('full_name', e.target.value)}
            className={inputCls}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-600">
            Imyaka
          </label>
          <input
            type="number"
            value={form.age}
            onChange={(e) => set('age', e.target.value)}
            className={inputCls}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-600">
            Inda ya (gravida)
          </label>
          <input
            type="number"
            min={1}
            value={form.gravida}
            onChange={(e) => set('gravida', e.target.value)}
            className={inputCls}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-600">
            Imbyaro ya (parity)
          </label>
          <input
            type="number"
            min={0}
            value={form.parity}
            onChange={(e) => set('parity', e.target.value)}
            className={inputCls}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-600">
            LMP (itariki y'imihango)
          </label>
          <input
            type="date"
            value={form.lmp_date}
            onChange={(e) => set('lmp_date', e.target.value)}
            className={inputCls}
          />
        </div>
        <label className="flex items-end gap-2 pb-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={form.is_lmp_estimated}
            onChange={(e) => set('is_lmp_estimated', e.target.checked)}
            className="h-4 w-4 accent-teal-600"
          />
          Itariki ntizi neza
        </label>
      </div>

      {form.lmp_date && (
        <div className="mt-4 rounded-xl bg-teal-50 p-4 text-sm text-gray-800">
          <p>
            <strong>EDD (itariki azabyara):</strong> {formatDdMmYyyy(edd)}
          </p>
          <p>
            <strong>Ibyumweru byo gutwita ubu:</strong> {week}
          </p>
        </div>
      )}

      <h3 className="mt-6 mb-2 font-semibold text-gray-700">Ibyo yahawe</h3>
      <div className="space-y-3">
        {PROVISIONS.map(({ key, emoji, label, minWeek }) => {
          if (minWeek != null && (week == null || week < minWeek)) return null;
          const given = form[`${key}_given`];
          return (
            <div
              key={key}
              className="flex flex-wrap items-center gap-3 rounded-xl border border-gray-200 px-4 py-3"
            >
              <span className="text-xl">{emoji}</span>
              <span className="flex-1 text-sm text-gray-800">{label}</span>
              <button
                type="button"
                role="switch"
                aria-checked={given}
                onClick={() => set(`${key}_given`, !given)}
                className={`relative h-6 w-11 rounded-full transition ${
                  given ? 'bg-teal-600' : 'bg-gray-300'
                }`}
              >
                <span
                  className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-all ${
                    given ? 'left-[22px]' : 'left-0.5'
                  }`}
                />
              </button>
              {given && (
                <input
                  type="date"
                  value={form[`${key}_date`] ?? ''}
                  onChange={(e) => set(`${key}_date`, e.target.value)}
                  className="rounded-lg border border-gray-300 px-2 py-1 text-sm"
                />
              )}
            </div>
          );
        })}
      </div>

      <button
        type="button"
        onClick={save}
        disabled={saving}
        className="mt-6 w-full rounded-lg bg-teal-600 py-2.5 font-semibold text-white hover:bg-teal-700 disabled:opacity-60"
      >
        {saving ? 'Tegereza...' : 'Bika Umwirondoro'}
      </button>
    </Collapsible>
  );
}
