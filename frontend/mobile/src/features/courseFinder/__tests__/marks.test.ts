/**
 * The marks screen sends only what the API takes: each subject once, with a
 * whole mark from 0 to 100. Empty rows are ignored; half-filled ones get a
 * message, never a guess. The backend's subject keys all have a name here.
 */
import { expect, test } from '@jest/globals';
import { readFileSync } from 'fs';
import { resolve } from 'path';

import { checkRows, cleanPercent, MarkRow } from '../marks';
import { ANOTHER_SUBJECT_KEYS, SUBJECT_KEYS, subjectName, subjectOptions } from '../subjects';
import { daysLeft, formatDay } from '../words';

const row = (key: number, subject: string | null, percent: string): MarkRow => ({ key, subject, percent });

test('complete rows become marks and empty rows are ignored', () => {
  const { marks, errors } = checkRows([row(1, 'english', '82'), row(2, null, ''), row(3, 'mathematics', '100'), row(4, 'life_orientation', '0')]);
  expect(errors).toEqual({});
  expect(marks).toEqual([
    { subject: 'english', percent: 82 },
    { subject: 'mathematics', percent: 100 },
    { subject: 'life_orientation', percent: 0 },
  ]);
});

test('half-filled rows say what is missing, and marks over 100 are refused', () => {
  const { marks, errors } = checkRows([row(1, 'english', ''), row(2, null, '70'), row(3, 'mathematics', '101')]);
  expect(marks).toEqual([]);
  expect(errors).toEqual({ 1: 'courseFinder.markMissing', 2: 'courseFinder.subjectMissing', 3: 'courseFinder.markRange' });
});

test('the mark box keeps digits only, at most three', () => {
  expect(cleanPercent('8a2')).toBe('82');
  expect(cleanPercent('1000')).toBe('100');
  expect(cleanPercent('-5.5')).toBe('55');
});

test('every subject the backend knows has a name, and nothing else is offered', () => {
  // backend/campus_engine/schemas.py, SUBJECTS: the keys admission rules use.
  const schemas = readFileSync(resolve(__dirname, '../../../../../../backend/campus_engine/schemas.py'), 'utf8');
  const block = /SUBJECTS = frozenset\(\s*\{([\s\S]*?)\}\s*\)/.exec(schemas);
  expect(block).not.toBeNull();
  const backend = [...block![1].matchAll(/"([a-z_]+)"/g)].map((m) => m[1]).sort();
  expect([...SUBJECT_KEYS].sort()).toEqual(backend);
  for (const key of SUBJECT_KEYS) expect(subjectName(key)).not.toMatch(/^subject\./);
  expect(subjectOptions().map((o) => o.value)).toEqual([...SUBJECT_KEYS, ...ANOTHER_SUBJECT_KEYS]);
  expect(subjectName('another_subject_2')).toBe('Another subject 2');
});

test('dates and day counts read as the app says them', () => {
  expect(formatDay('2026-10-31')).toBe('Sat 31 Oct 2026');
  expect(daysLeft(18)).toBe('18 days left');
  expect(daysLeft(1)).toBe('1 day left');
  expect(daysLeft(0)).toBe('Last day');
});
