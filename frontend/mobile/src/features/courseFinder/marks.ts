/**
 * The marks screen's rows, one per chosen subject, and turning them into what
 * the API takes. A subject without a mark gets a message instead of a guess.
 */
import { MessageKey } from '@/shared/i18n';

import { ANOTHER_SUBJECT_KEYS, inOrder, SUBJECTS } from './subjects';
import { Mark } from './types';

export type MarkRow = { subject: string; percent: string };

/** Two subjects most learners take, to start from; the picker changes them. */
export function startingRows(): MarkRow[] {
  return [
    { subject: 'english', percent: '' },
    { subject: 'life_orientation', percent: '' },
  ];
}

/** Rows for the chosen subjects, in the picker's order, keeping every mark already typed. */
export function rowsFor(chosen: string[], current: MarkRow[]): MarkRow[] {
  const typed = new Map(current.map((r) => [r.subject, r.percent]));
  return inOrder(chosen).map((subject) => ({ subject, percent: typed.get(subject) ?? '' }));
}

/** Digits only, at most three: what the mark box keeps of what was typed. */
export function cleanPercent(text: string): string {
  return text.replace(/[^0-9]/g, '').slice(0, 3);
}

type Entered = { subject: string; percent: number };

export type Sent = {
  marks: Mark[];
  /** The language that went as the other official language, when there were several to choose from. */
  otherLanguage: string | null;
  /** Points-only subjects beyond the three the API takes (the picker never allows them). */
  overflow: string[];
};

/**
 * The marks under the API's keys. Of the official languages besides English,
 * the best-marked goes as the other official language (on a tie, the first in
 * the picker); the rest, and every subject no rule names, count towards
 * points only.
 */
export function toApiMarks(entered: Entered[]): Sent {
  const languages = entered.filter((e) => SUBJECTS[e.subject]?.kind === 'language');
  const best = languages.reduce<Entered | null>((top, e) => (!top || e.percent > top.percent ? e : top), null);
  const marks: Mark[] = [];
  const pointsOnly: Entered[] = [];
  for (const e of entered) {
    if (SUBJECTS[e.subject]?.kind === 'rule') marks.push({ subject: e.subject, percent: e.percent });
    else if (e === best) marks.push({ subject: 'other_language', percent: e.percent });
    else pointsOnly.push(e);
  }
  pointsOnly.slice(0, ANOTHER_SUBJECT_KEYS.length).forEach((e, i) => marks.push({ subject: ANOTHER_SUBJECT_KEYS[i], percent: e.percent }));
  return {
    marks,
    otherLanguage: languages.length > 1 && best ? best.subject : null,
    overflow: pointsOnly.slice(ANOTHER_SUBJECT_KEYS.length).map((e) => e.subject),
  };
}

export type Checked = Sent & { errors: Record<string, MessageKey> };

/** Every row's mark checked, then the marks as the API takes them. Errors are keyed by subject. */
export function checkRows(rows: MarkRow[]): Checked {
  const entered: Entered[] = [];
  const errors: Record<string, MessageKey> = {};
  for (const row of rows) {
    const text = row.percent.trim();
    if (!text) errors[row.subject] = 'courseFinder.markMissing';
    else if (!/^\d{1,3}$/.test(text) || Number(text) > 100) errors[row.subject] = 'courseFinder.markRange';
    else entered.push({ subject: row.subject, percent: Number(text) });
  }
  const sent = toApiMarks(entered);
  for (const subject of sent.overflow) errors[subject] = 'courseFinder.pointsOnlyFull';
  return { ...sent, errors };
}
