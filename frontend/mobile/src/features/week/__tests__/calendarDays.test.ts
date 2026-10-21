/**
 * The calendar's day logic: month grids start on a Monday and hold six weeks; classes skip the university's
 * recess; a day lists classes, tests, exams and plans in time order; a month cell gets one dot per kind.
 */
import { expect, test } from '@jest/globals';

import { Activity, ExamEntry, TimetableEntry } from '@/features/timetable/types';

import { addMonths, dotsOn, itemsOn, mondayOf, monthGrid, offDays, Sources } from '../calendarDays';
import { ClassEvent } from '../types';

const cls: TimetableEntry = {
  id: 'c', module: 'ANA201', title: null, kind: 'lecture', weekday: 0, day: 'Monday', starts: '08:00', ends: '09:40',
  venue: null, clashes: false,
};
const test2: ClassEvent = {
  id: 'e', class_id: 'k', module: 'PHY121', kind: 'test', title: 'Test 2', on: '2026-10-26', at: '10:00', venue: null,
  weighting: 20, when: '', cancelled: false, verified: true, version: 1, your_flag: null,
};
const exam: ExamEntry = {
  id: 'x', module: 'BCH111', title: null, paper: 'PAPER 1', on: '2026-10-28', day: '', starts: '09:00', minutes: 180,
  venue: null, clashes: false,
};
const gym: Activity = {
  id: 'p', title: 'Gym', kind: 'exercise', weekday: 0, on: null, day: 'Monday', starts: '17:00', ends: '18:00',
  place: null, clashes: false,
};

const sources = (off: string[] = []): Sources => ({ classes: [cls], events: [test2], exams: [exam], plans: [gym], off: new Set(off) });

test('a month grid starts on the Monday before the 1st and holds six weeks', () => {
  const days = monthGrid('2026-10-21');
  expect(days[0]).toBe('2026-09-28');
  expect(days).toHaveLength(42);
  expect(mondayOf('2026-10-25')).toBe('2026-10-19');
  expect(addMonths('2026-12-15', 1)).toBe('2027-01-01');
});

test('a day lists its classes, tests and plans in time order', () => {
  const items = itemsOn('2026-10-26', sources());
  expect(items.map((i) => i.type)).toEqual(['class', 'event', 'plan']);
  expect(dotsOn('2026-10-26', sources())).toEqual(['test', 'class', 'plan']);
  expect(dotsOn('2026-10-28', sources())).toEqual(['exam']);
});

test("classes don't show in the university's recess, but tests and plans still do", () => {
  const off = offDays([{ name: 'Recess', period: 'recess', start: '2026-10-24', end: '2026-10-27', note: null, source_url: null, who: 'everyone' }]);
  expect(off.has('2026-10-26')).toBe(true);
  expect(itemsOn('2026-10-26', { ...sources(), off }).map((i) => i.type)).toEqual(['event', 'plan']);
});
