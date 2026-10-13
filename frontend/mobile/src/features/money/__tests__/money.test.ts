/**
 * Rand as students type it becomes integer cents (CLAUDE.md: money is integer
 * cents everywhere), never through a float; and the words for when money comes in.
 */
import { expect, jest, test } from '@jest/globals';

import { addDays, formatMonth, todaySast } from '@/shared/lib/dates';
import { centsToInput, formatRand, MAX_CENTS, parseRand } from '@/shared/lib/money';

import { dayInMonth } from '../screens/IncomeEditScreen';
import { ordinal, scheduleText } from '../words';

// The edit screen's module imports the router and the API; only its date helper is under test here.
jest.mock('expo-router', () => ({ router: { back: jest.fn() }, useLocalSearchParams: () => ({}) }));

test('rand as typed becomes whole cents', () => {
  expect(parseRand('1500')).toBe(150000);
  expect(parseRand('R1 500')).toBe(150000);
  expect(parseRand('1,500.50')).toBe(150050);
  expect(parseRand('48,50')).toBe(4850); // a decimal comma
  expect(parseRand('48.5')).toBe(4850);
  expect(parseRand('0.07')).toBe(7);
  expect(parseRand('0')).toBe(0);
});

test('anything that is not an amount is refused, never guessed', () => {
  for (const text of ['', ' ', '-5', '12.345', 'abc', '1.2.3', '1e3', 'R']) expect(parseRand(text)).toBeNull();
  expect(parseRand(String(MAX_CENTS / 100))).toBe(MAX_CENTS);
  expect(parseRand(String(MAX_CENTS / 100 + 1))).toBeNull();
});

test('cents go back into the box as the student would type them', () => {
  expect(centsToInput(150000)).toBe('1500');
  expect(centsToInput(4850)).toBe('48.50');
  expect(centsToInput(7)).toBe('0.07');
  expect(formatRand(150050)).toBe('R1,500.50');
});

test('when money comes in, in words', () => {
  expect([1, 2, 3, 4, 11, 12, 13, 21, 22, 23, 31].map(ordinal)).toEqual([
    '1st', '2nd', '3rd', '4th', '11th', '12th', '13th', '21st', '22nd', '23rd', '31st',
  ]);
  expect(scheduleText({ day_of_month: 25, expected_on: null })).toBe('Every month on the 25th');
  expect(scheduleText({ day_of_month: null, expected_on: '2026-10-31' })).toBe('Once, on Sat 31 Oct 2026');
});

test('a once-off payment needs a day that exists in its month', () => {
  expect(dayInMonth('2026-10', 31)).toBe('2026-10-31');
  expect(dayInMonth('2027-02', 28)).toBe('2027-02-28');
  expect(dayInMonth('2027-02', 29)).toBeNull();
  expect(dayInMonth('2026-11', 31)).toBeNull();
});

test('days are South African days', () => {
  // 23:30 UTC on 12 Oct is already 13 Oct in South Africa (UTC+2).
  expect(todaySast(new Date('2026-10-12T23:30:00Z'))).toBe('2026-10-13');
  expect(addDays('2026-10-31', 1)).toBe('2026-11-01');
  expect(addDays('2026-03-01', -1)).toBe('2026-02-28');
  expect(formatMonth('2026-11')).toBe('Nov 2026');
});
