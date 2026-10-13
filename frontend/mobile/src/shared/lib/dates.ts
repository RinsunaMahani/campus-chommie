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

/** "2026-10", "2026-11", ... : `count` months starting `offset` months from this month (SAST). */
export function monthsFrom(offset: number, count: number, today: string = todaySast()): string[] {
  const [y, m] = today.split('-').map(Number);
  return Array.from({ length: count }, (_, i) => {
    const d = new Date(Date.UTC(y, m - 1 + offset + i, 1));
    return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}`;
  });
}

/** A day that exists in that month ("2026-02-30" doesn't) as "2026-02-28" style text, or null. */
export function dayInMonth(yearMonth: string, day: number): string | null {
  const [y, m] = yearMonth.split('-').map(Number);
  const d = new Date(Date.UTC(y, m - 1, day));
  if (d.getUTCMonth() !== m - 1 || day < 1) return null;
  return `${yearMonth}-${String(day).padStart(2, '0')}`;
}

/** "2026-10-12" -> "Mon 12 Oct": for dates the reader knows the year of. */
export function formatShortDay(iso: string): string {
  return formatDay(iso).split(' ').slice(0, 3).join(' ');
}

/** A percentage as people say it: 10, 63.1 (never 10.0). */
export function percent(n: number): string {
  return String(Math.round(n * 10) / 10);
}
