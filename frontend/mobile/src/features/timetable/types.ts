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

export type ExamEntry = {
  id: string;
  module: string;
  title: string | null;
  paper: string | null;
  /** "2026-10-26" */
  on: string;
  /** "Mon 26 Oct 2026" */
  day: string;
  starts: string;
  /** Null where the exam list doesn't say. */
  minutes: number | null;
  venue: string | null;
  /** At the same time as another exam. */
  clashes: boolean;
};

export type ExamsAnswer = { exams: ExamEntry[]; lines: string[] };

export type ExamInput = {
  module: string;
  on: string;
  starts: string;
  minutes?: number | null;
  title?: string | null;
  paper?: string | null;
  venue?: string | null;
};

/** What an imported PDF lists. Nothing is saved until the student checks it and saves. */
export type FoundClass = Omit<TimetableEntry, 'id' | 'title' | 'clashes'>;
export type FoundExam = Omit<ExamEntry, 'id' | 'venue' | 'clashes'>;
export type ImportLayout = 'classes' | 'exams';
export type ImportAnswer = { layout: ImportLayout; modules: string[]; classes: FoundClass[]; exams: FoundExam[]; lines: string[] };

/** A file the student picked: a uri on a phone, a File in a browser. */
export type PickedPdf = { uri: string; name: string; mimeType?: string; file?: Blob };

/** Something in the student's own week besides classes: weekly on `weekday`, or once `on`. */
export type ActivityKind = 'personal' | 'social' | 'errands' | 'exercise' | 'work' | 'other';
export const ACTIVITY_KINDS: ActivityKind[] = ['personal', 'social', 'errands', 'exercise', 'work', 'other'];

export type Activity = {
  id: string;
  title: string;
  kind: ActivityKind;
  weekday: number | null;
  on: string | null;
  /** "Saturday" for a weekly one, "Fri 30 Oct 2026" for a one-off. */
  day: string;
  starts: string;
  ends: string;
  place: string | null;
  clashes: boolean;
};

export type ActivitiesAnswer = { activities: Activity[]; lines: string[] };

export type ActivityInput = {
  title: string;
  kind: ActivityKind;
  weekday: number | null;
  on: string | null;
  starts: string;
  ends: string;
  place?: string | null;
};

export type FreeSlot = { on: string; weekday: number; day: string; starts: string; ends: string };
export type FindTimeAnswer = { minutes: number; slots: FreeSlot[]; lines: string[] };
