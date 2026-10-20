/**
 * Small wording helpers: day counts as the app says them, and an error as one
 * plain sentence. Dates come from the shared helpers.
 */
import { errorText as sharedErrorText } from '@/shared/api/errors';
import { t } from '@/shared/i18n';

export { formatDay } from '@/shared/lib/dates';

/** "Bloemfontein and Welkom, Free State · University of technology": only the parts a source states. */
export function placeLine(u: { city?: string | null; province?: string | null; institution_type_label?: string | null }): string | undefined {
  const where = [u.city, u.province].filter(Boolean).join(', ');
  const line = [where, u.institution_type_label].filter(Boolean).join(' · ');
  return line || undefined;
}

/** "18 days left", "1 day left", "Last day". */
export function daysLeft(days: number): string {
  if (days <= 0) return t('courseFinder.lastDay');
  if (days === 1) return t('courseFinder.dayLeft');
  return t('courseFinder.daysLeft', { n: days });
}

/** "today", "tomorrow", "in 93 days": how far off a date is. */
export function inDays(days: number): string {
  if (days <= 0) return t('courseFinder.today');
  if (days === 1) return t('courseFinder.tomorrow');
  return t('courseFinder.inDays', { n: days });
}

/** What went wrong, in one sentence: the server's own words, or every field message on a 422. */
export function errorText(error: unknown): string {
  return sharedErrorText(error, t('courseFinder.errorGeneric'));
}
