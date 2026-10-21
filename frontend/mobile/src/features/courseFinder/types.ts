/**
 * What the course-finder API answers (backend: domains/pathways/course_finder
 * and catalogue/universities). Field names stay as the server sends them.
 * Missing facts come as null, with a "not verified yet" line beside them.
 */

/** Words for a tier come from the server's `label`; this is only for icons and colour. */
export type Tier = 'reach' | 'meets_minimum' | 'competitive' | 'not_yet' | 'unverified';

export type Confirmation = {
  /** False until a person on the team has checked the pack. */
  confirmed: boolean;
  /** "Not yet confirmed by the team." when not confirmed. */
  notice: string | null;
};

export type UniversitySummary = Confirmation & {
  id: string;
  name: string;
  city: string | null;
  academic_year: number | null;
  programmes: number;
};

export type Match = Confirmation & {
  university: string;
  university_name: string;
  programme: string;
  programme_name: string;
  tier: Tier;
  label: string;
  selective: boolean;
  /** The faculty, school or college that offers it, as the university names it; null where the source doesn't say. */
  faculty: string | null;
  /** Field tags (backend FIELDS): they choose the faculty's picture. */
  fields: string[];
  points: number | null;
  min_points: number | null;
  gap: number | null;
  /** Requirements not met; each also appears in `explanation`. */
  failed: string[];
  /** The "why" lines. */
  explanation: string[];
  source_url: string | null;
};

/** One university's programmes for these marks, and how to apply there on today's date. */
export type AssessAnswer = {
  university: UniversitySummary;
  matches: Match[];
  apply: { today: string; test_date: boolean; guide: Guide };
};

/** One subject at one university: its level there and the points it adds (0 when not counted). */
export type SubjectPoints = { subject: string; level: number; points: number; counted: boolean };

/** Your points at one university, by its own rule, and how many of its programmes you meet. */
export type UniversityPoints = Confirmation & {
  university: string;
  university_name: string;
  /** Null when we don't hold the university's points rule yet. */
  points: number | null;
  counted: string[];
  /** In the order the marks were sent; together they make `points`. */
  subjects: SubjectPoints[];
  tiers: Record<Tier, number>;
  summary: string;
  lines: string[];
  source_url: string | null;
};

export type PointsAnswer = { universities: UniversityPoints[] };

/** A funder on the funding list, as much of it as the course finder shows. */
export type FundingCard = {
  id: string;
  name: string;
  short_name: string | null;
  status: string;
  label: string;
  heading: string | null;
  opens: string | null;
  days: number | null;
  url: string | null;
  source_url: string | null;
};

export type WindowStatus =
  | 'open'
  | 'closing_soon'
  | 'check'
  | 'opens_later'
  | 'late_open'
  | 'late_ahead'
  | 'closed'
  | 'not_published';

export type ApplyWindow = {
  intake: number;
  heading: string;
  status: WindowStatus;
  label: string;
  opens: string | null;
  closes: string | null;
  closes_one_of: string[];
  late_opens: string | null;
  late_closes: string | null;
  next_date: string | null;
  days: number | null;
  lines: string[];
  source_url: string | null;
};

export type SlotFunder = {
  id: string;
  name: string;
  short_name: string | null;
  label: string;
  status: string;
  days: number | null;
  lines: string[];
  kind_label: string;
  url: string | null;
  source_url: string | null;
  checked: string | null;
};

export type SlotFunding = {
  count: number;
  open_now: number;
  fields: string[];
  funders: SlotFunder[];
  lines: string[];
};

export type Bridge = {
  to: string;
  guarantee: 'by_rule' | 'considered';
  guarantee_label: string;
  conditions: string | null;
  max_places: number | null;
  added_years: number | null;
  eligibility_note: string | null;
  source_url: string | null;
};

export type Slot = {
  number: number;
  role: string;
  match: Match;
  notes: string[];
  apply: ApplyWindow[];
  funding: SlotFunding | null;
  bridge?: Bridge;
};

export type Group = { items: string[]; source_url: string | null } | null;

/** One university's or funder's "how to apply". */
export type Guide = Confirmation & {
  id: string;
  name: string;
  kind: 'university' | 'funder';
  url: string | null;
  how: string | null;
  fee_cents: number | null;
  fee_note: string | null;
  contact: string | null;
  max_choices: number | null;
  documents: Group;
  after: { text: string; source_url: string | null }[];
  who_can_apply: Group;
  tips: Group;
  warnings: Group;
  windows: ApplyWindow[];
  lines: string[];
  source_url: string | null;
};

export type Deadline = {
  date: string;
  days: number;
  text: string;
  intake: number | null;
  who: string;
  programme: string | null;
  source_url: string | null;
};

export type PlanApply = {
  today: string;
  /** True when `today` is a preview's test date (CAMPUS_PREVIEW_TODAY), never in production. */
  test_date: boolean;
  universities: Guide[];
  funding: Guide[];
  deadlines: Deadline[];
  notes: string[];
};

export type Plan = {
  goal: Slot | null;
  bridge: Slot | null;
  safe: Slot | null;
  other_routes: Slot[];
  notes: string[];
  apply: PlanApply;
};

/** One row the learner sends. Subject keys are in subjects.ts. */
export type Mark = { subject: string; percent: number };

