/**
 * Days as the app says them, in South African time. Africa/Johannesburg is
 * UTC+2 all year (no daylight saving), and the API sends plain days
 * ("2026-10-31"), so no time zone can move a date.
 */
import { t } from '@/shared/i18n';

const SAST_OFFSET_MS = 2 * 60 * 60 * 1000;

/** Today in South Africa: "2026-10-13". */
export function todaySast(now: Date = new Date()): string {
  return new Date(now.getTime() + SAST_OFFSET_MS).toISOString().slice(0, 10);
}

/** "2026-10-13" plus `n` days (negative goes back). */
export function addDays(iso: string, n: number): string {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(Date.UTC(y, m - 1, d + n)).toISOString().slice(0, 10);
}

/** "2026-10-31" -> "Sat 31 Oct 2026". */
export function formatDay(iso: string): string {
  const [y, m, d] = iso.split('-').map(Number);
  if (!y || !m || !d) return iso;
  const weekday = new Date(Date.UTC(y, m - 1, d)).getUTCDay();
  return `${t('date.weekdays').split(' ')[weekday]} ${d} ${t('date.months').split(' ')[m - 1]} ${y}`;
}

/** "2026-11" -> "Nov 2026". */
export function formatMonth(yearMonth: string): string {
  const [y, m] = yearMonth.split('-').map(Number);
  return `${t('date.months').split(' ')[m - 1]} ${y}`;
}
