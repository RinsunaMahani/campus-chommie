/**
 * Every subject on the Department of Basic Education's Grade 10 to 12 list
 * (docs/research/nsc-subjects.md), in folders of related subjects, and how
 * each one reaches the API.
 *
 * Admission rules name only the keys in backend/campus_engine/schemas.py
 * (SUBJECTS; a test keeps the two in step). So English goes as `english`; the
 * best-marked of the learner's other official languages (home or first
 * additional level) goes as `other_language`; and every subject no rule names,
 * further languages included, goes as `another_subject_1` to `_3`, which count
 * towards points only.
 */
import { MessageKey, t } from '@/shared/i18n';

/** How a subject reaches the API. */
export type SubjectKind =
  /** Admission rules name it: it goes under its own key. */
  | 'rule'
  /** An official language besides English, at home or first additional level. */
  | 'language'
  /** No rule names it: it counts towards points only. */
  | 'points';

export type FolderId =
  | 'languages'
  | 'mathematics'
  | 'sciences'
  | 'business'
  | 'humanities'
  | 'computers'
  | 'technology'
  | 'agriculture'
  | 'arts'
  | 'services'
  | 'life'
  | 'more_languages';

export type Subject = { id: string; kind: SubjectKind; folder: FolderId };
export type Folder = { id: FolderId; subjects: Subject[] };

/** The official languages besides English, at home or first additional level, as the DBE lists them. */
const OFFICIAL_LANGUAGES = ['afrikaans', 'isindebele', 'isixhosa', 'isizulu', 'sepedi', 'sesotho', 'setswana', 'siswati', 'tshivenda', 'xitsonga'];

/** The languages offered at second additional level, as the DBE lists them. */
const SECOND_ADDITIONAL = [
  'afrikaans',
  'english',
  'french',
  'isindebele',
  'isixhosa',
  'isizulu',
  'mandarin',
  'sepedi',
  'sesotho',
  'setswana',
  'siswati',
  'tshivenda',
  'xitsonga',
];

function folder(id: FolderId, subjects: [string, SubjectKind][]): Folder {
  return { id, subjects: subjects.map(([subject, kind]) => ({ id: subject, kind, folder: id })) };
}

const rule = (id: string): [string, SubjectKind] => [id, 'rule'];
const language = (id: string): [string, SubjectKind] => [id, 'language'];
const points = (id: string): [string, SubjectKind] => [id, 'points'];

/** The picker's folders and their subjects, in the order the picker shows them. */
export const FOLDERS: Folder[] = [
  folder('languages', [rule('english'), ...OFFICIAL_LANGUAGES.map((l) => language(l)), language('sign_language')]),
  folder('mathematics', [rule('mathematics'), rule('mathematical_literacy'), rule('technical_mathematics')]),
  folder('sciences', [rule('physical_sciences'), rule('life_sciences'), rule('technical_sciences'), points('marine_sciences')]),
  folder('business', [rule('accounting'), rule('business_studies'), rule('economics'), points('maritime_economics')]),
  folder('humanities', [rule('geography'), rule('history'), points('religion_studies')]),
  folder('computers', [rule('computer_applications_technology'), rule('information_technology')]),
  folder('technology', [
    rule('engineering_graphics_and_design'),
    rule('civil_technology'),
    rule('electrical_technology'),
    rule('mechanical_technology'),
    points('nautical_science'),
  ]),
  folder('agriculture', [
    rule('agricultural_sciences'),
    rule('agricultural_technology'),
    points('agricultural_management_practices'),
    points('equine_studies'),
  ]),
  folder('arts', [rule('dance_studies'), rule('design'), rule('dramatic_arts'), rule('music'), rule('visual_arts')]),
  folder('services', [rule('consumer_studies'), rule('hospitality_studies'), rule('tourism')]),
  folder('life', [rule('life_orientation'), points('sport_and_exercise_science')]),
  folder('more_languages', SECOND_ADDITIONAL.map((l) => points(`sal_${l}`))),
];

export const SUBJECTS: Record<string, Subject> = Object.fromEntries(FOLDERS.flatMap((f) => f.subjects).map((s) => [s.id, s]));

const ORDER = FOLDERS.flatMap((f) => f.subjects.map((s) => s.id));

/** The API's keys for subjects no rule names (backend: course_finder/constants.py). */
export const ANOTHER_SUBJECT_KEYS = ['another_subject_1', 'another_subject_2', 'another_subject_3'] as const;

/** The API takes 1 to 9 subjects (brief, M2), and at most three of them points-only. */
export const MAX_SUBJECTS = 9;
export const MAX_POINTS_ONLY = ANOTHER_SUBJECT_KEYS.length;

/** A second additional language is named as the language itself; the picker's folder says the level. */
export function subjectName(id: string): string {
  return t(`subject.${id.replace(/^sal_/, '')}` as MessageKey);
}

export function folderName(id: FolderId): string {
  return t(`subjectFolder.${id}` as MessageKey);
}

/** The level a language folder holds, said under its name. */
export function folderHint(id: FolderId): string | null {
  if (id === 'languages') return t('subjectFolder.languagesHint');
  if (id === 'more_languages') return t('subjectFolder.moreLanguagesHint');
  return null;
}

/** These subjects in the picker's order, which is also the order of the marks rows. */
export function inOrder(ids: string[]): string[] {
  return ORDER.filter((id) => ids.includes(id));
}

/** How many of these subjects would reach the API as points-only marks. */
export function pointsOnlyCount(ids: string[]): number {
  const kinds = ids.map((id) => SUBJECTS[id]?.kind);
  const languages = kinds.filter((k) => k === 'language').length;
  return kinds.filter((k) => k === 'points').length + Math.max(0, languages - 1);
}

/** The same language at the other level, if the DBE offers it there: a language is taken at one level only. */
export function sameLanguage(id: string): string | null {
  const twin = id.startsWith('sal_') ? id.slice(4) : `sal_${id}`;
  return SUBJECTS[twin] ? twin : null;
}

/** Why a subject can't join the ones already chosen. */
export type Blocked = { why: 'full' } | { why: 'points_full' } | { why: 'chosen_in'; folder: FolderId };

export function blocked(chosen: string[], id: string): Blocked | null {
  if (chosen.includes(id)) return null;
  const twin = sameLanguage(id);
  if (twin && chosen.includes(twin)) return { why: 'chosen_in', folder: SUBJECTS[twin].folder };
  if (chosen.length >= MAX_SUBJECTS) return { why: 'full' };
  if (pointsOnlyCount([...chosen, id]) > MAX_POINTS_ONLY) return { why: 'points_full' };
  return null;
}
