/**
 * Timetable and calendar: times are typed forgivingly and checked as the server does; the timetable lists
 * classes by day with clashes flagged; the calendar places classes on their weekday in their module colour,
 * timed tests in the grid and 23:59 deadlines in the "Due" row.
 */
import { beforeEach, expect, jest, test } from '@jest/globals';
import { render, screen, waitFor } from '@testing-library/react-native';

import { CalendarGrid, Day } from '@/features/week/components/CalendarGrid';
import { ClassEvent } from '@/features/week/types';

import { timetableApi } from '../api/timetableApi';
import { cleanTime, timeProblem } from '../screens/ClassEditScreen';
import TimetableScreen from '../screens/TimetableScreen';
import { TimetableEntry } from '../types';

jest.mock('expo-router', () => {
  const React = jest.requireActual<typeof import('react')>('react');
  return {
    router: { push: jest.fn(), back: jest.fn(), canGoBack: () => true, replace: jest.fn() },
    useLocalSearchParams: () => ({}),
    useFocusEffect: (cb: () => void) => React.useEffect(() => cb(), [cb]),
  };
});
jest.mock('react-native-safe-area-context', () => {
  const actual = jest.requireActual<object>('react-native-safe-area-context');
  return { ...actual, useSafeAreaInsets: () => ({ top: 0, left: 0, right: 0, bottom: 0 }) };
});
jest.mock('@expo/vector-icons', () => ({ Feather: () => null }));

const entry = (over: Partial<TimetableEntry>): TimetableEntry => ({
  id: 'a', module: 'ANA201', title: null, kind: 'lecture', weekday: 0, day: 'Monday', starts: '08:00', ends: '09:40',
  venue: 'Hall A', clashes: false, ...over,
});

beforeEach(() => {
  jest.restoreAllMocks();
});

test('times are typed forgivingly and checked like the server does', () => {
  expect(cleanTime('830')).toBe('08:30');
  expect(cleanTime('0830')).toBe('08:30');
  expect(cleanTime('8:30')).toBe('08:30');
  expect(timeProblem('08:30')).toBeNull();
  expect(timeProblem('08:33')).toBe('Use 5-minute steps, like 08:30 or 08:35.');
  expect(timeProblem('05:00')).toBe('Classes run between 06:00 and 22:00.');
  expect(timeProblem('8.30')).toBe('Use 24-hour time, like 08:30.');
});

test('the timetable lists classes by day, says the week in words and flags clashes', async () => {
  jest.spyOn(timetableApi, 'mine').mockResolvedValue({
    entries: [
      entry({ id: 'a', clashes: true }),
      entry({ id: 'b', module: 'PHY121', kind: 'practical', starts: '09:00', ends: '11:00', clashes: true }),
      entry({ id: 'c', module: 'BCH111', weekday: 2, day: 'Wednesday', kind: 'tutorial' }),
    ],
    lines: ['3 classes a week, 5 hours in all, on Monday and Wednesday.'],
  });
  render(<TimetableScreen />);
  expect(await screen.findByText('3 classes a week, 5 hours in all, on Monday and Wednesday.')).toBeTruthy();
  expect(screen.getByText('Monday')).toBeTruthy();
  expect(screen.getByText('Wednesday')).toBeTruthy();
  expect(screen.getAllByText('Clashes')).toHaveLength(2);
  expect(screen.getByText('Practical')).toBeTruthy();
});

test('the calendar places classes on their weekday, timed tests in the grid and late deadlines in Due', async () => {
  const days: Day[] = [{ date: '2026-10-19', weekday: 0, label: 'Mon 19', today: false }];
  const event = (over: Partial<ClassEvent>): ClassEvent => ({
    id: 'e', class_id: 'c', module: 'ANA201', kind: 'test', title: 'Test 2', on: '2026-10-19', at: '10:00', venue: null,
    weighting: 20, when: 'Mon 19 Oct 2026 at 10:00', cancelled: false, verified: true, version: 1, your_flag: null, ...over,
  });
  render(
    <CalendarGrid
      days={days}
      classes={[entry({}), entry({ id: 'x', weekday: 1, module: 'NOTMONDAY' })]}
      events={[event({}), event({ id: 'd', kind: 'assignment', title: 'Assignment 3', at: '23:59', module: 'PHY121' }), event({ id: 'z', on: '2026-10-20' })]}
      nowMinutes={null}
    />,
  );
  await waitFor(() => expect(screen.getAllByText('ANA201')).toHaveLength(2)); // the class, and its test's module line
  expect(screen.queryByText('NOTMONDAY')).toBeNull();
  expect(screen.getByText('10:00 Test 2')).toBeTruthy();
  expect(screen.getByText('Due 23:59 · PHY121 Assignment 3')).toBeTruthy();
  expect(screen.getAllByText(/Test 2/)).toHaveLength(1); // Tuesday's test isn't on Monday
});
