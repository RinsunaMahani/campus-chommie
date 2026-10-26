/**
 * The marks screen sends only what the API takes: each subject once, under a
 * key the backend knows, with a whole mark from 0 to 100. English goes as
 * itself, the best-marked other official language as the other official
 * language, and the rest count towards points. A subject without a mark gets
 * a message, never a guess. The picker's subjects all have names, and the
 * backend's keys and limits match the app's.
 */
import { expect, test } from '@jest/globals';
import { readFileSync } from 'fs';
import { resolve } from 'path';

import { checkRows, cleanPercent, MarkRow, rowsFor, toApiMarks } from '../marks';
import { ANOTHER_SUBJECT_KEYS, blocked, FOLDERS, folderName, MAX_SUBJECTS, pointsOnlyCount, SUBJECTS, subjectName } from '../subjects';
import { daysLeft, formatDay, placeLine } from '../words';

const BACKEND = resolve(__dirname, '../../../../../../backend');
const row = (subject: string, percent: string): MarkRow => ({ subject, percent });

test('English language level survives subject selection and is sent without duplicating the mark', () => {
  const english: MarkRow = { subject: 'english', percent: '55', language_level: 'home' };
  const rows = rowsFor(['english', 'mathematics'], [english]);
  expect(rows.find((r) => r.subject === 'english')).toEqual(english);
  expect(checkRows([english]).marks).toEqual([{ subject: 'english', percent: 55, language_level: 'home' }]);
});

test('every mark goes under a key the API takes, and a missing or out-of-range mark gets a message', () => {
  const { marks, errors } = checkRows([row('english', '82'), row('mathematics', '100'), row('life_orientation', '0')]);
  expect(errors).toEqual({});
  expect(marks).toEqual([
    { subject: 'english', percent: 82 },
    { subject: 'mathematics', percent: 100 },
    { subject: 'life_orientation', percent: 0 },
  ]);
  expect(checkRows([row('english', ''), row('mathematics', '101')]).errors).toEqual({
    english: 'courseFinder.markMissing',
    mathematics: 'courseFinder.markRange',
  });
});

test('one language besides English goes as the other official language', () => {
  const { marks, otherLanguage } = toApiMarks([
    { subject: 'english', percent: 70 },
    { subject: 'sepedi', percent: 81 },
  ]);
  expect(marks).toEqual([
    { subject: 'english', percent: 70 },
    { subject: 'other_language', percent: 81, language_name: 'sepedi' },
  ]);
  expect(otherLanguage).toBeNull();
});

test('with several, the best-marked goes as the other official language and the rest count towards points', () => {
  const { marks, otherLanguage } = toApiMarks([
    { subject: 'english', percent: 70 },
    { subject: 'afrikaans', percent: 64 },
    { subject: 'isizulu', percent: 77 },
    { subject: 'sal_french', percent: 90 },
    { subject: 'religion_studies', percent: 58 },
  ]);
  expect(otherLanguage).toBe('isizulu');
  expect(marks).toEqual([
    { subject: 'english', percent: 70 },
    { subject: 'other_language', percent: 77, language_name: 'isizulu' },
    { subject: 'another_subject_1', percent: 64, language_name: 'afrikaans' },
    { subject: 'another_subject_2', percent: 90 },
    { subject: 'another_subject_3', percent: 58 },
  ]);
  // On a tie, the language first in the picker.
  expect(toApiMarks([{ subject: 'afrikaans', percent: 70 }, { subject: 'sepedi', percent: 70 }]).otherLanguage).toBe('afrikaans');
});

test('a second additional language counts towards points only, even with the best mark', () => {
  expect(toApiMarks([{ subject: 'english', percent: 60 }, { subject: 'sal_isizulu', percent: 95 }]).marks).toEqual([
    { subject: 'english', percent: 60 },
    { subject: 'another_subject_1', percent: 95 },
  ]);
});

test('more than three points-only subjects are refused with a message, never dropped', () => {
  const rows = [row('sal_french', '60'), row('sal_mandarin', '61'), row('religion_studies', '62'), row('equine_studies', '63')];
  expect(checkRows(rows).errors).toEqual({ equine_studies: 'courseFinder.pointsOnlyFull' });
});

test("rows follow the picker's order and keep the marks already typed", () => {
  expect(rowsFor(['life_orientation', 'mathematics', 'sepedi', 'english'], [row('english', '72'), row('history', '50')])).toEqual([
    row('english', '72'),
    row('sepedi', ''),
    row('mathematics', ''),
    row('life_orientation', ''),
  ]);
});

test('the picker allows nine subjects, three of them points-only, and each language at one level', () => {
  const nine = ['english', 'sepedi', 'mathematics', 'physical_sciences', 'life_sciences', 'geography', 'accounting', 'tourism', 'life_orientation'];
  expect(blocked(nine, 'history')).toEqual({ why: 'full' });
  expect(blocked(nine, 'sepedi')).toBeNull();
  expect(blocked(['sal_french', 'religion_studies', 'marine_sciences'], 'equine_studies')).toEqual({ why: 'points_full' });
  // A second language besides English counts towards points only, so it takes one of the three.
  expect(pointsOnlyCount(['sepedi', 'isizulu'])).toBe(1);
  expect(blocked(['sepedi', 'sal_french', 'religion_studies', 'marine_sciences'], 'isizulu')).toEqual({ why: 'points_full' });
  expect(blocked(['sepedi'], 'sal_sepedi')).toEqual({ why: 'chosen_in', folder: 'languages' });
  expect(blocked(['sal_english'], 'english')).toEqual({ why: 'chosen_in', folder: 'more_languages' });
  expect(blocked(['english'], 'mathematics')).toBeNull();
});

test('the mark box keeps digits only, at most three', () => {
  expect(cleanPercent('8a2')).toBe('82');
  expect(cleanPercent('1000')).toBe('100');
  expect(cleanPercent('-5.5')).toBe('55');
});

test("the backend's subject keys all have a subject that sends them, and the limits match", () => {
  // backend/campus_engine/schemas.py, SUBJECTS: the keys admission rules use.
  const schemas = readFileSync(resolve(BACKEND, 'campus_engine/schemas.py'), 'utf8');
  const block = /SUBJECTS = frozenset\(\s*\{([\s\S]*?)\}\s*\)/.exec(schemas);
  expect(block).not.toBeNull();
  const backend = [...block![1].matchAll(/"([a-z_]+)"/g)].map((m) => m[1]).sort();
  const sent = Object.values(SUBJECTS)
    .filter((s) => s.kind === 'rule')
    .map((s) => s.id);
  expect([...sent, 'other_language'].sort()).toEqual(backend);

  // backend/src/domains/pathways/course_finder/constants.py: the points-only keys and the most subjects.
  const constants = readFileSync(resolve(BACKEND, 'src/domains/pathways/course_finder/constants.py'), 'utf8');
  expect(/MAX_SUBJECTS = (\d+)/.exec(constants)?.[1]).toBe(String(MAX_SUBJECTS));
  const another = /ANOTHER_SUBJECTS = \(([^)]*)\)/.exec(constants);
  expect(another).not.toBeNull();
  expect([...another![1].matchAll(/"([a-z_0-9]+)"/g)].map((m) => m[1])).toEqual([...ANOTHER_SUBJECT_KEYS]);
});

test('every subject sits in one folder, and every subject and folder has a name', () => {
  const ids = FOLDERS.flatMap((f) => f.subjects.map((s) => s.id));
  expect(new Set(ids).size).toBe(ids.length);
  for (const id of ids) expect(subjectName(id)).toEqual(expect.any(String));
  for (const f of FOLDERS) expect(folderName(f.id)).toEqual(expect.any(String));
  expect(subjectName('sal_isizulu')).toBe('isiZulu');
  expect(subjectName('sign_language')).toBe('South African Sign Language');
});

test('dates and day counts read as the app says them', () => {
  expect(formatDay('2026-10-31')).toBe('Sat 31 Oct 2026');
  expect(daysLeft(18)).toBe('18 days left');
  expect(daysLeft(1)).toBe('1 day left');
  expect(daysLeft(0)).toBe('Last day');
});

test('the place line shows only what a source states', () => {
  expect(placeLine({ city: 'Bloemfontein and Welkom', province: 'Free State', institution_type_label: 'University of technology' })).toBe(
    'Bloemfontein and Welkom, Free State · University of technology',
  );
  expect(placeLine({ city: 'Pretoria', province: null, institution_type_label: null })).toBe('Pretoria');
  expect(placeLine({ city: null })).toBeUndefined();
});

 test('a lower-scored language retains its name and role without an extra mark', () => {
  expect(toApiMarks([
    { subject: 'sepedi', percent: 80 },
    { subject: 'afrikaans', percent: 55, language_level: 'home' },
  ]).marks).toEqual([
    { subject: 'other_language', percent: 80, language_name: 'sepedi' },
    { subject: 'another_subject_1', percent: 55, language_name: 'afrikaans', language_level: 'home' },
  ]);
});
