// Naegele's rule, identical to the backend and Flutter implementations:
// LMP + 7 days, then month +9 (same year) if the result falls in Jan-Mar,
// otherwise month -3 and year +1. Backend value stays authoritative.

/**
 * @param {string} lmpIso - LMP date as YYYY-MM-DD
 * @returns {Date|null}
 */
export function calculateEdd(lmpIso) {
  if (!lmpIso) return null;
  const lmp = new Date(`${lmpIso}T00:00:00`);
  if (Number.isNaN(lmp.getTime())) return null;

  const base = new Date(lmp);
  base.setDate(base.getDate() + 7);

  let month = base.getMonth() + 1; // 1-12
  let year = base.getFullYear();
  if (month <= 3) {
    month += 9;
  } else {
    month -= 3;
    year += 1;
  }
  // Clamp the day for shorter target months (e.g. 31 -> 30 Sep).
  const lastDay = new Date(year, month, 0).getDate();
  const day = Math.min(base.getDate(), lastDay);
  return new Date(year, month - 1, day);
}

/** Whole weeks elapsed since the given ISO date. */
export function weeksSince(lmpIso) {
  if (!lmpIso) return null;
  const lmp = new Date(`${lmpIso}T00:00:00`);
  if (Number.isNaN(lmp.getTime())) return null;
  return Math.floor((Date.now() - lmp.getTime()) / (7 * 24 * 60 * 60 * 1000));
}

export function formatDdMmYyyy(date) {
  if (!date) return '';
  const dd = String(date.getDate()).padStart(2, '0');
  const mm = String(date.getMonth() + 1).padStart(2, '0');
  return `${dd}/${mm}/${date.getFullYear()}`;
}
