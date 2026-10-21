/**
 * What's on each day of the calendar, worked out once for every view (month, week, 3 days, day): the student's
 * classes on their weekday (except in their university's recess or closure, from its own calendar), their
 * classes' tests and deadlines, their exams, and their own plans. Dates are SAST "YYYY-MM-DD".
 */
import { Activity, ExamEntry, TimetableEntry } from '@/features/timetable/types';

import { CalendarEntry, ClassEvent } from './types';

export function addDays(iso: string, n: number): string {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(Date.UTC(y, m - 1, d + n)).toISOString().slice(0, 10);
}

export function weekdayOf(iso: string): number {
  const [y, m, d] = iso.split('-').map(Number);
  return (new Date(Date.UTC(y, m - 1, d)).getUTCDay() + 6) % 7;
}

export function mondayOf(iso: string): string {
  return addDays(iso, -weekdayOf(iso));
}

export function addMonths(iso: string, n: number): string {
  const [y, m] = iso.split('-').map(Number);
  return new Date(Date.UTC(y, m - 1 + n, 1)).toISOString().slice(0, 10);
}

/** The 42 days (6 weeks from a Monday) a month grid shows for the month containing `iso`. */
export function monthGrid(iso: string): string[] {
  const first = `${iso.slice(0, 7)}-01`;
  const start = mondayOf(first);
  return Array.from({ length: 42 }, (_, i) => addDays(start, i));
}

/** Every date inside the university's recess or closure periods. */
export function offDays(entries: CalendarEntry[]): Set<string> {
  const off = new Set<string>();
  for (const e of entries) {
    if (e.period !== 'recess' && e.period !== 'closed') continue;
    for (let d = e.start; d <= (e.end || e.start); d = addDays(d, 1)) off.add(d);
  }
  return off;
}

export type DayItem =
  | { type: 'class'; at: string; ends: string; entry: TimetableEntry }
  | { type: 'event'; at: string | null; event: ClassEvent }
  | { type: 'exam'; at: string; exam: ExamEntry }
  | { type: 'plan'; at: string; ends: string; plan: Activity };

export type Sources = {
  classes: TimetableEntry[];
  events: ClassEvent[];
  exams: ExamEntry[];
  plans: Activity[];
  off: Set<string>;
};

/** Everything on `date`, in time order (undated deadlines last). */
export function itemsOn(date: string, s: Sources): DayItem[] {
  const wd = weekdayOf(date);
  const items: DayItem[] = [];
  if (!s.off.has(date)) {
    for (const c of s.classes) if (c.weekday === wd) items.push({ type: 'class', at: c.starts, ends: c.ends, entry: c });
  }
  for (const e of s.events) if (e.on === date && !e.cancelled) items.push({ type: 'event', at: e.at, event: e });
  for (const x of s.exams) if (x.on === date) items.push({ type: 'exam', at: x.starts, exam: x });
  for (const p of s.plans) {
    if (p.weekday != null ? p.weekday === wd : p.on === date) items.push({ type: 'plan', at: p.starts, ends: p.ends, plan: p });
  }
  return items.sort((a, b) => (a.at ?? '99:99').localeCompare(b.at ?? '99:99'));
}

/** Which kinds of thing a day holds, for a month cell's dots (at most one dot per kind). */
export function dotsOn(date: string, s: Sources): ('class' | 'test' | 'deadline' | 'exam' | 'plan')[] {
  const kinds = new Set<'class' | 'test' | 'deadline' | 'exam' | 'plan'>();
  for (const it of itemsOn(date, s)) {
    if (it.type === 'class') kinds.add('class');
    else if (it.type === 'exam') kinds.add('exam');
    else if (it.type === 'plan') kinds.add('plan');
    else if (it.event.kind === 'assignment') kinds.add('deadline');
    else kinds.add(it.event.kind === 'exam' ? 'exam' : 'test');
  }
  return (['exam', 'test', 'deadline', 'class', 'plan'] as const).filter((k) => kinds.has(k));
}
