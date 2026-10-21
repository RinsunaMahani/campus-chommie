/**
 * A university's programmes grouped by the faculty that offers them, as the
 * university names it. Programmes whose source names no faculty go last,
 * under "Other programmes". Groups with more programmes the learner meets
 * come first; inside a group the server's order (best tiers first) stays.
 */
import { Match, Tier } from './types';

export type Art =
  | 'health'
  | 'engineering'
  | 'computing'
  | 'commerce'
  | 'law'
  | 'education'
  | 'science'
  | 'agriculture'
  | 'arts'
  | 'humanities'
  | 'hospitality'
  | 'sport'
  | 'other';

export type FacultyGroup = {
  /** The faculty's name, or null for programmes whose source names none. */
  faculty: string | null;
  matches: Match[];
  /** Competitive or meets the minimum. */
  meets: number;
  reach: number;
  art: Art;
};

const MEETS: Tier[] = ['competitive', 'meets_minimum'];

// Each programme field (backend FIELDS) to the picture its faculty gets.
const ART_OF_FIELD: Record<string, Art> = {
  health_sciences: 'health',
  medicine: 'health',
  medical_sciences: 'health',
  nursing: 'health',
  pharmacy: 'health',
  radiography: 'health',
  rehabilitation: 'health',
  emergency_care: 'health',
  dentistry: 'health',
  nutrition: 'health',
  environmental_health: 'health',
  engineering: 'engineering',
  built_environment: 'engineering',
  disaster_and_fire: 'engineering',
  computing: 'computing',
  commerce: 'commerce',
  accounting: 'commerce',
  finance: 'commerce',
  economics: 'commerce',
  management: 'commerce',
  public_administration: 'commerce',
  law: 'law',
  safety_and_justice: 'law',
  education: 'education',
  natural_sciences: 'science',
  physical_sciences: 'science',
  life_sciences: 'science',
  mathematical_sciences: 'science',
  earth_sciences: 'science',
  agriculture: 'agriculture',
  food_science: 'agriculture',
  consumer_sciences: 'agriculture',
  arts_and_design: 'arts',
  performing_arts: 'arts',
  music: 'arts',
  humanities: 'humanities',
  languages_and_communication: 'humanities',
  theology: 'humanities',
  tourism_and_hospitality: 'hospitality',
  sport_science: 'sport',
};

/** The picture for a set of programmes: the art most of their fields share. */
export function artFor(matches: Match[]): Art {
  const votes = new Map<Art, number>();
  for (const m of matches) {
    for (const f of m.fields ?? []) {
      const art = ART_OF_FIELD[f];
      if (art) votes.set(art, (votes.get(art) ?? 0) + 1);
    }
  }
  let best: Art = 'other';
  let most = 0;
  for (const [art, n] of votes) {
    if (n > most) [best, most] = [art, n];
  }
  return best;
}

export function groupByFaculty(matches: Match[]): FacultyGroup[] {
  const byName = new Map<string | null, Match[]>();
  for (const m of matches) {
    const key = m.faculty ?? null;
    byName.set(key, [...(byName.get(key) ?? []), m]);
  }
  const groups = [...byName.entries()].map(([faculty, ms]) => ({
    faculty,
    matches: ms,
    meets: ms.filter((m) => MEETS.includes(m.tier)).length,
    reach: ms.filter((m) => m.tier === 'reach').length,
    art: artFor(ms),
  }));
  return groups.sort((a, b) => {
    if ((a.faculty === null) !== (b.faculty === null)) return a.faculty === null ? 1 : -1;
    return b.meets - a.meets || b.reach - a.reach || (a.faculty ?? '').localeCompare(b.faculty ?? '');
  });
}

/** Whether grouping helps: at least one programme names its faculty. */
export function hasFaculties(matches: Match[]): boolean {
  return matches.some((m) => m.faculty);
}
