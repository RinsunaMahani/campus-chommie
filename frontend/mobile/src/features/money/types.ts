/**
 * What the money API answers (backend: domains/student/money). Amounts are
 * integer cents; days are plain dates in SAST. Field names stay as sent.
 */

export type Reliability = 'on_time' | 'sometimes_late' | 'often_late' | 'not_sure';

export type CheckinDay =
  | 'monday'
  | 'tuesday'
  | 'wednesday'
  | 'thursday'
  | 'friday'
  | 'saturday'
  | 'sunday';

export type Settings = {
  balance_cents: number;
  /** The day the balance was true. */
  balance_on: string;
  essentials_per_day_cents: number;
  life_fund_reserve_cents: number;
  checkin_day?: CheckinDay;
};

/** Money the student expects: monthly on `day_of_month`, or once on `expected_on`. */
export type IncomeSource = {
  id: string;
  label: string;
  amount_cents: number;
  day_of_month: number | null;
  expected_on: string | null;
  reliability: Reliability;
};

export type IncomeInput = Omit<IncomeSource, 'id'>;

export type Payment = {
  id: string;
  income_source_id: string;
  label: string;
  amount_cents: number;
  expected_on: string;
  scheduled_on: string;
  received: boolean;
  received_on: string | null;
  overdue: boolean;
};

export type SpendingDay = { spent_on: string; amount_cents: number };

export type LifeFundState = 'green' | 'amber' | 'paused';

type SummaryBase = { today: string; late: boolean; late_days: number };

/** Before the student enters a balance: one line saying what to add. */
export type SummaryNotReady = SummaryBase & { ready: false; lines: string[] };

export type SummaryReady = SummaryBase & {
  ready: true;
  balance: { cents: number; entered_cents: number; entered_on: string; lines: string[] };
  pace: { daily_cents: number; low_cents: number; high_cents: number; days_logged: number; from: string; lines: string[] } | null;
  runway: {
    scenario: string;
    runs_out_on: string | null;
    days: number | null;
    earliest_on: string | null;
    latest_on: string | null;
    short_before_next: boolean;
    lines: string[];
  };
  safe_to_spend: {
    per_day_cents: number;
    days_until_next: number | null;
    essentials_cents: number;
    fixed_costs_cents?: number;
    reserve_cents: number;
    lines: string[];
  };
  life_fund: { state: LifeFundState; reason: string; resume_hint: string | null; reserve_cents: number };
  /** This week's load (My week): null until the student has classes. */
  this_week: { colour: 'green' | 'amber' | 'red'; reason: string } | null;
  next_payment: { label: string; expected_on: string; lands_on: string | null; amount_cents: number } | null;
  notes: string[];
};

export type Summary = SummaryNotReady | SummaryReady;

/** A cheap thing to do near the student's campus, priced from the place's own page. */
export type CheapThing = {
  name: string;
  category: string;
  cost_note: string | null;
  address: string | null;
  hours: string | null;
  source_url: string | null;
  read_on: string | null;
  last_verified: string | null;
};

/** "Can I afford this?": nothing is stored. */
export type AffordAnswer = {
  verdict: 'yes' | 'tight' | 'not_now';
  /** How many days the money lasts without it, and with it (null: past the horizon). */
  days_before: number | null;
  days_after: number | null;
  /** A payday it would be fine to buy on instead. */
  wait_until: string | null;
  lines: string[];
};

export type PotKind = 'goal' | 'family' | 'stokvel' | 'buffer' | 'big_purchase';

export type MoneyGoal = {
  id: string;
  label: string;
  kind: PotKind;
  amount_cents: number;
  saved_cents: number;
  due_on: string | null;
  due_day: string | null;
  from_university: boolean;
  stokvel_funded: boolean;
  per_week_cents: number | null;
  lines: string[];
};

export type GoalInput = {
  label: string;
  kind?: PotKind;
  amount_cents: number;
  saved_cents?: number;
  due_on?: string | null;
  from_university?: boolean;
  stokvel_funded?: boolean;
};

/** A fee date from the student's university's own page: never an amount. */
export type UniversityDate = { name: string; kind: string; on: string; day: string; source_url: string | null };

export type FixedCost = {
  id: string;
  label: string;
  amount_cents: number;
  day_of_month: number;
};

export type FixedCostInput = Omit<FixedCost, 'id'>;

export type WeeklyCheckinEntry = {
  id: string;
  week_end: string;
  amount_cents: number | null;
  skipped: boolean;
};

export type CheckinStreak = {
  weeks: number;
  line: string;
};

export type CheckinStatus = {
  checkin_day: CheckinDay;
  is_checkin_day: boolean;
  checked_in_this_week: boolean;
  week_start: string;
  week_end: string;
  this_week: WeeklyCheckinEntry | null;
  streak: CheckinStreak;
  recent_checkins: WeeklyCheckinEntry[];
};

export type CheckinInput = {
  amount_cents?: number | null;
  skipped?: boolean;
  week_end?: string | null;
};

export type MoneyPlan = {
  payday: { lands_on: string; day: string; amount_cents: number; pots: { label: string; cents: number; why: string }[]; free_cents: number } | null;
  goals: MoneyGoal[];
  fixed_costs?: FixedCost[];
  university_dates: UniversityDate[];
  lines: string[];
};

export type HealthCheckStatus = 'done' | 'not yet' | "can't tell";

export type HealthCheck = {
  id: 'runway' | 'buffer' | 'spending' | 'goals' | 'checkin' | string;
  title: string;
  status: HealthCheckStatus;
  line: string;
  action: string | null;
  target: string | null;
};

export type MoneyHealth = {
  checks: HealthCheck[];
  done_count: number;
  total_count: number;
  line: string;
};
