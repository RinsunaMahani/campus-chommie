/** What the colleges routes answer (backend domains/catalogue/colleges). */
export type CollegeKind = 'tvet' | 'private_higher_education' | 'private_college';
export type CollegeStatus = 'public' | 'registered' | 'provisionally_registered' | 'cancelled';
export type Verdict = CollegeStatus | 'bogus' | 'not_found' | 'several';

export type CollegeCard = {
  id: string;
  name: string;
  kind: CollegeKind;
  kind_label: string;
  status: CollegeStatus;
  label: string;
  registration_number: string | null;
  provinces: string[];
  /** As DHET prints it ("www.example.co.za"), only when it opened as the college's own site. */
  website: string | null;
  /** DHET's listed address when it doesn't work (gone, parked, suspended): never a link. */
  website_problem: { listed: string; note: string; checked: string } | null;
  lines: string[];
};

export type Source = { url: string; publisher: string; title: string | null; retrieved: string | null };
export type WarningSigns = { items: string[]; source_url: string | null };

/** One province's share of a list ("not_listed": DHET gives no province). */
export type ProvinceGroup = { id: string; title: string; total: number; line: string };

export type CollegeListAnswer = {
  summary: string;
  total: number;
  page: number;
  pages: number;
  colleges: CollegeCard[];
  /** Absent from an API older than 22 Oct 2026: the screen then shows one list. */
  provinces?: ProvinceGroup[];
  confirmed: boolean;
  notice: string | null;
};

export type Occupational = { saqa_id: string; name: string; nsfas_allowances: boolean; centre_of_specialisation: boolean };

export type CollegeDetail = CollegeCard & {
  phone: string | null;
  head_office: [number, number] | null;
  sites: string[];
  qualifications: string[];
  notes: string[];
  occupational: Occupational[];
  sources: Source[];
};

export type CollegeAnswer = { college: CollegeDetail; warning_signs: WarningSigns | null; confirmed: boolean; notice: string | null };

export type CheckAnswer = {
  verdict: Verdict;
  label: string;
  lines: string[];
  colleges: CollegeCard[];
  unregistered: { id: string; name: string; where: string | null; label: string }[];
  warning_signs: WarningSigns | null;
  sources: Source[];
  confirmed: boolean;
  notice: string | null;
};

export type CollegeFilters = { q?: string; kind?: CollegeKind; province?: string; page?: number };
