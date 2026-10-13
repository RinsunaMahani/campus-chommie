/** My money's wording: when money comes in, and how reliable it is. */
import { MessageKey, t } from '@/shared/i18n';
import { formatDay } from '@/shared/lib/dates';

import { IncomeSource, Reliability } from './types';

export const RELIABILITY: Reliability[] = ['on_time', 'sometimes_late', 'often_late', 'not_sure'];

export function reliabilityLabel(r: Reliability): string {
  return t(`money.reliability.${r}` as MessageKey);
}

/** 1st, 2nd, 3rd, 4th ... 11th, 12th, 13th ... 21st, 22nd, 31st. */
export function ordinal(n: number): string {
  const teen = n % 100 >= 11 && n % 100 <= 13;
  const suffix = teen ? 'th' : ({ 1: 'st', 2: 'nd', 3: 'rd' } as Record<number, string>)[n % 10] ?? 'th';
  return `${n}${suffix}`;
}

/** "Every month on the 25th", or "Once, on Sat 31 Oct 2026". */
export function scheduleText(source: Pick<IncomeSource, 'day_of_month' | 'expected_on'>): string {
  if (source.day_of_month != null) return t('money.monthlyOn', { day: ordinal(source.day_of_month) });
  return source.expected_on ? t('money.onceOn', { date: formatDay(source.expected_on) }) : '';
}
