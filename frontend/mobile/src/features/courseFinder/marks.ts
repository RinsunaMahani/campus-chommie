/**
 * The marks screen's rows, and turning them into what the API takes. A row
 * left completely empty is ignored; anything half-filled gets a message
 * instead of a guess.
 */
import { MessageKey } from '@/shared/i18n';

import { Mark } from './types';

export type MarkRow = { key: number; subject: string | null; percent: string };

let nextKey = 1;

export function newRow(subject: string | null = null): MarkRow {
  return { key: nextKey++, subject, percent: '' };
}

/** The four subjects nearly every learner takes, then room for three more. */
export function startingRows(): MarkRow[] {
  return [newRow('english'), newRow('other_language'), newRow('mathematics'), newRow('life_orientation'), newRow(), newRow(), newRow()];
}

/** Digits only, at most three: what the mark box keeps of what was typed. */
export function cleanPercent(text: string): string {
  return text.replace(/[^0-9]/g, '').slice(0, 3);
}

export function checkRows(rows: MarkRow[]): { marks: Mark[]; errors: Record<number, MessageKey> } {
  const marks: Mark[] = [];
  const errors: Record<number, MessageKey> = {};
  for (const row of rows) {
    const text = row.percent.trim();
    if (!row.subject && !text) continue;
    if (!row.subject) errors[row.key] = 'courseFinder.subjectMissing';
    else if (!text) errors[row.key] = 'courseFinder.markMissing';
    else if (!/^\d{1,3}$/.test(text) || Number(text) > 100) errors[row.key] = 'courseFinder.markRange';
    else marks.push({ subject: row.subject, percent: Number(text) });
  }
  return { marks, errors };
}
