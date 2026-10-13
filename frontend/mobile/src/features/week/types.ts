/**
 * What the week, classes and events API answers (backend: domains/classes).
 * Only a rep's confirmation makes an event verified, and nobody is ever listed:
 * views give counts.
 */

export type EventKind = 'quiz' | 'assignment' | 'practical' | 'test' | 'exam';
export type FlagReason = 'wrong_date' | 'wrong_time' | 'wrong_venue' | 'not_happening' | 'duplicate' | 'other';

export const EVENT_KINDS: EventKind[] = ['test', 'quiz', 'practical', 'assignment', 'exam'];
export const FLAG_REASONS: FlagReason[] = ['wrong_date', 'wrong_time', 'wrong_venue', 'not_happening', 'duplicate', 'other'];

/** A verified test or deadline. */
export type ClassEvent = {
  id: string;
  class_id: string;
  module: string;
  kind: EventKind;
  title: string | null;
  on: string;
  at: string | null;
  venue: string | null;
  weighting: number | null;
  /** "Thu 15 Oct 2026 at 23:59" */
  when: string;
  cancelled: boolean;
  verified: boolean;
  version: number;
  your_flag: FlagReason | null;
  /** Each change a rep confirmed (from a class's own events list). */
  changes?: { field: string; old: string | null; new: string | null; changed_on: string; line: string }[];
  /** Reps only: how many flagged it and why, never who. */
  flags?: { count: number; reasons: Partial<Record<FlagReason, number>> };
};

export type CalendarEntry = {
  name: string;
  period: string;
  start: string;
  end: string;
  note: string | null;
  source_url: string | null;
  who: string;
};

export type Week = {
  week_start: string;
  week_end: string;
  this_week: boolean;
  /** "Manageable", "Busy" or "Heavy": the word is the load; colour only adds to it. */
  load: string;
  colour: 'green' | 'amber' | 'red';
  reason: string;
  score: number;
  events: ClassEvent[];
  calendar: CalendarEntry[];
};

export type WeekAnswer = {
  today: string;
  university: { id: string; name: string; confirmed: boolean; notice: string | null } | null;
  classes: number;
  notes: string[];
  weeks: Week[];
};
