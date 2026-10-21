/**
 * The subjects a learner can enter: the keys admission rules use
 * (backend/campus_engine/schemas.py, SUBJECTS; a test keeps the two lists in
 * step), with the names the app shows, plus three "another subject" rows for
 * subjects no rule names, which count towards points only.
 */
import { MessageKey, t } from '@/shared/i18n';
import { SelectOption } from '@/shared/components/SelectField';

/** The most common first, then the rest as the NSC lists them. */
export const SUBJECT_KEYS = [
  'english',
  'other_language',
  'mathematics',
  'mathematical_literacy',
  'technical_mathematics',
  'life_orientation',
  'physical_sciences',
  'life_sciences',
  'technical_sciences',
  'accounting',
  'business_studies',
  'economics',
  'geography',
  'history',
  'agricultural_sciences',
  'agricultural_technology',
  'information_technology',
  'computer_applications_technology',
  'engineering_graphics_and_design',
  'civil_technology',
  'electrical_technology',
  'mechanical_technology',
  'consumer_studies',
  'hospitality_studies',
  'tourism',
  'dance_studies',
  'design',
  'dramatic_arts',
  'music',
  'visual_arts',
] as const;

export const ANOTHER_SUBJECT_KEYS = ['another_subject_1', 'another_subject_2', 'another_subject_3'] as const;

/** The API takes 1 to 9 subjects (brief, M2). */
export const MAX_SUBJECTS = 9;

export function subjectName(key: string): string {
  const another = ANOTHER_SUBJECT_KEYS.indexOf(key as (typeof ANOTHER_SUBJECT_KEYS)[number]);
  if (another >= 0) return t('courseFinder.anotherSubject', { n: another + 1 });
  return t(`subject.${key}` as MessageKey);
}

/** Every subject as a choice, with a hint where the name needs one. */
export function subjectOptions(): SelectOption<string>[] {
  return [
    ...SUBJECT_KEYS.map((key) => ({
      value: key,
      label: subjectName(key),
      subtitle: key === 'other_language' ? t('courseFinder.otherLanguageHint') : undefined,
    })),
    ...ANOTHER_SUBJECT_KEYS.map((key) => ({ value: key, label: subjectName(key), subtitle: t('courseFinder.anotherSubjectHint') })),
  ];
}
