/**
 * Small wording helpers: dates and day counts as the app says them, and an
 * error as one plain sentence.
 */
import { ApiError } from '@/shared/api/client';
import { t } from '@/shared/i18n';

import { fieldMessages } from './api/courseFinderApi';

/** "2026-10-31" -> "Sat 31 Oct 2026". The server sends plain days (SAST), so no time zone can move them. */
export function formatDay(iso: string): string {
  const [y, m, d] = iso.split('-').map(Number);
  if (!y || !m || !d) return iso;
  const weekday = new Date(Date.UTC(y, m - 1, d)).getUTCDay();
  return `${t('date.weekdays').split(' ')[weekday]} ${d} ${t('date.months').split(' ')[m - 1]} ${y}`;
}

/** "18 days left", "1 day left", "Last day". */
export function daysLeft(days: number): string {
  if (days <= 0) return t('courseFinder.lastDay');
  if (days === 1) return t('courseFinder.dayLeft');
  return t('courseFinder.daysLeft', { n: days });
}

/** What went wrong, in one sentence: the server's own words, or every field message on a 422. */
export function errorText(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.code === 'VALIDATION_ERROR') {
      const messages = [...new Set(fieldMessages(error.errors))];
      if (messages.length) return messages.join(' ');
    }
    return error.message;
  }
  return t('courseFinder.errorGeneric');
}
