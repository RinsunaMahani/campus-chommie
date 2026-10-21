/**
 * Home's Today tiles: the class on now or next (wrapping round the week), the next test or deadline not yet
 * past, and "now" in SAST whatever the phone's own time zone.
 */
import { expect, test } from '@jest/globals';

import { TimetableEntry } from '@/features/timetable/types';
import { ClassEvent } from '@/features/week/types';

import { nextClass, nextDeadline, nowInSast } from '../today';

const cls = (over: Partial<TimetableEntry>): TimetableEntry => ({
  id: 'a', module: 'ANA201', title: null, kind: 'lecture', weekday: 0, day: 'Monday', starts: '08:00', ends: '09:40',
  venue: null, clashes: false, ...over,
});
const ev = (over: Partial<ClassEvent>): ClassEvent => ({
  id: 'e', class_id: 'c', module: 'PHY121', kind: 'test', title: 'Test 2', on: '2026-10-21', at: '10:00', venue: null,
  weighting: 20, when: '', cancelled: false, verified: true, version: 1, your_flag: null, ...over,
});

test('now is read in South African time', () => {
  // 23:30 UTC on Tue 20 Oct is 01:30 on Wed 21 Oct in SAST.
  expect(nowInSast(new Date('2026-10-20T23:30:00Z'))).toEqual({ date: '2026-10-21', weekday: 2, minutes: 90 });
});

test('the class on now, the next one later today, or the first one on a later day', () => {
  const week = [cls({ id: 'mon' }), cls({ id: 'wed', weekday: 2, starts: '14:00', ends: '15:00' })];
  expect(nextClass(week, { weekday: 0, minutes: 8 * 60 + 30 })).toMatchObject({ entry: { id: 'mon' }, daysAhead: 0, now: true });
  expect(nextClass(week, { weekday: 0, minutes: 10 * 60 })).toMatchObject({ entry: { id: 'wed' }, daysAhead: 2, now: false });
  expect(nextClass(week, { weekday: 3, minutes: 0 })).toMatchObject({ entry: { id: 'mon' }, daysAhead: 4 });
  expect(nextClass([], { weekday: 0, minutes: 0 })).toBeNull();
});

test('the next deadline skips cancelled ones and those already past today', () => {
  const events = [
    ev({ id: 'past', at: '08:00' }),
    ev({ id: 'gone', on: '2026-10-22', cancelled: true }),
    ev({ id: 'friday', on: '2026-10-23', at: null }),
  ];
  expect(nextDeadline(events, '2026-10-21', 9 * 60)).toMatchObject({ event: { id: 'friday' }, days: 2 });
  expect(nextDeadline([], '2026-10-21', 0)).toBeNull();
});
