/** Your week in review, as GET /me/week-review sends it: everything already in words, with its numbers. */
export type ReviewLine = { text: string; kind: string };

export type MarkMove = {
  code: string;
  before: number | null;
  after: number | null;
  direction: 'up' | 'down' | 'same' | 'first';
  text: string;
};

export type ReviewSpending = {
  spent_cents: number | null;
  usual_cents: number | null;
  days: number;
  weeks_compared: number;
  direction: 'less' | 'same' | 'more' | 'unknown';
  text: string;
  /** Oldest first, this week last; null for a week with nothing logged. */
  weeks: (number | null)[];
};

export type WeekReview = {
  today: string;
  week: 'this' | 'last';
  week_start: string;
  week_end: string;
  finished: boolean;
  /** Today is the check-in day (this week) or one of the two days after it (last week). */
  ready: boolean;
  headline: string;
  done: ReviewLine[];
  coming: ReviewLine[];
  marks: MarkMove[];
  spending: ReviewSpending;
  /** Shown when a mark went down or a target is out of reach. */
  support: string | null;
};

export type WhichWeek = 'auto' | 'this' | 'last';
