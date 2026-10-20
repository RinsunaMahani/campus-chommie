/** What the timetable API answers (backend: domains/student/timetable). */
export type ClassKind = 'lecture' | 'tutorial' | 'practical' | 'other';
export const CLASS_KINDS: ClassKind[] = ['lecture', 'tutorial', 'practical', 'other'];

export type TimetableEntry = {
  id: string;
  module: string;
  title: string | null;
  kind: ClassKind;
  /** 0 = Monday. */
  weekday: number;
  day: string;
  /** "08:00" */
  starts: string;
  ends: string;
  venue: string | null;
  /** Overlaps another class on the same day. */
  clashes: boolean;
};

export type TimetableAnswer = { entries: TimetableEntry[]; lines: string[] };

export type EntryInput = {
  module: string;
  kind: ClassKind;
  weekday: number;
  starts: string;
  ends: string;
  title?: string | null;
  venue?: string | null;
};
