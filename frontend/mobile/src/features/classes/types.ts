/** Classes, reps and announcements (backend: domains/classes). Members are never listed: only counts. */
import { ClassEvent, EventKind } from '@/features/week/types';

export type ClassSummary = {
  id: string;
  university: string;
  university_name: string | null;
  campus: string | null;
  campus_name: string | null;
  module_code: string;
  module_name: string | null;
  year: number;
  invite_code: string;
  role: 'rep' | 'student';
  members: number;
  reps: number;
};

export type Change = 'moved' | 'cancelled';

/** What the rep confirms: a new event, or a change to one ("moved": what's sent is what it becomes). */
export type ConfirmBody = {
  change: Change | null;
  event_id: string | null;
  kind: EventKind | null;
  title: string | null;
  on: string | null;
  at: string | null;
  venue: string | null;
  weighting: number | null;
};

/** An announcement as the engine read it, waiting for a rep. */
export type Candidate = {
  id: string;
  class_id: string;
  text: string;
  sent_on: string;
  read_as: Omit<ConfirmBody, 'event_id'> & { module: string | null };
  confidence: Partial<Record<string, number>>;
  /** Fields the rep should look at twice: highlighted in the form. */
  needs_check: string[];
  /** The confirm form's starting values. */
  proposed: ConfirmBody;
  lines: string[];
  /** For a "moved" or "cancelled" message: the event it most likely changes. */
  changes_event: Pick<ClassEvent, 'id' | 'kind' | 'title' | 'when'> | null;
  confirmable: boolean;
  from_rep: boolean;
  yours: boolean;
};

export type RepCode = { code: string; expires_at: string; lines: string[] };
