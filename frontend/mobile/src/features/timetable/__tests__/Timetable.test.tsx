/**
 * Timetable and calendar: times are typed forgivingly and checked as the server does; the timetable lists
 * classes by day with clashes flagged, then exams; the calendar places classes on their weekday in their module
 * colour, timed tests in the grid, 23:59 deadlines in the "Due" row and exams on their dates. Importing a PDF
 * shows only the student's modules, lets them leave rows out, and saves the rest in one go.
 */
import { beforeEach, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import * as DocumentPicker from 'expo-document-picker';

import { CalendarGrid, Day } from '@/features/week/components/CalendarGrid';
import { ClassEvent } from '@/features/week/types';

import { examsApi, timetableApi } from '../api/timetableApi';
import { cleanTime, timeProblem } from '../screens/ClassEditScreen';
import ImportScreen, { matching, parseCodes } from '../screens/ImportScreen';
import TimetableScreen from '../screens/TimetableScreen';
import { Activity, ExamEntry, ImportAnswer, TimetableEntry } from '../types';

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
jest.mock('expo-document-picker', () => ({ getDocumentAsync: jest.fn() }));
jest.mock('@/features/profile/state', () => ({ useProfile: () => ({ demo: false, mock: false, profile: null }) }));

const entry = (over: Partial<TimetableEntry>): TimetableEntry => ({
  id: 'a', module: 'ANA201', title: null, kind: 'lecture', weekday: 0, day: 'Monday', starts: '08:00', ends: '09:40',
  venue: 'Hall A', clashes: false, ...over,
});

const exam = (over: Partial<ExamEntry>): ExamEntry => ({
  id: 'x', module: 'ANA201', title: 'ANATOMY II', paper: 'PAPER 1', on: '2026-10-19', day: 'Mon 19 Oct 2026',
  starts: '09:00', minutes: 180, venue: null, clashes: false, ...over,
});

beforeEach(() => {
  jest.restoreAllMocks();
  jest.spyOn(examsApi, 'mine').mockResolvedValue({ exams: [], lines: ['No exams yet.'] });
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

test('the timetable lists exams under the classes', async () => {
  jest.spyOn(timetableApi, 'mine').mockResolvedValue({ entries: [], lines: ['Your timetable is empty.'] });
  jest.spyOn(examsApi, 'mine').mockResolvedValue({
    exams: [exam({})], lines: ['1 exam, Mon 19 Oct 2026.'],
  });
  render(<TimetableScreen />);
  expect(await screen.findByText('1 exam, Mon 19 Oct 2026.')).toBeTruthy();
  expect(screen.getByText('PAPER 1')).toBeTruthy();
  expect(screen.getByText('Mon 19 Oct 2026 · 09:00 · 3 h')).toBeTruthy();
});

test('an exam sits on its date in the calendar, as long as the paper', async () => {
  const days: Day[] = [{ date: '2026-10-19', weekday: 0, label: 'Mon 19', today: false }];
  render(<CalendarGrid days={days} classes={[]} events={[]} exams={[exam({}), exam({ id: 'y', on: '2026-10-20', module: 'NOTMONDAY' })]} nowMinutes={null} />);
  expect(await screen.findByText('Exam · ANA201')).toBeTruthy();
  expect(screen.queryByText('Exam · NOTMONDAY')).toBeNull();
});

test('module codes are typed forgivingly and a code the PDF lacks is named', () => {
  expect(parseCodes('mchm000, MPHS 000\nmchm000; abc101 def202')).toEqual(['MCHM000', 'MPHS000', 'ABC101', 'DEF202']);
  const rows = [{ module: 'MCHM000' }, { module: 'MPHS000' }, { module: 'MBIO000' }];
  expect(matching(rows, ['MCHM000', 'XYZ999'], ['MCHM000', 'MPHS000', 'MBIO000'])).toEqual({
    rows: [{ module: 'MCHM000' }], missing: ['XYZ999'],
  });
});

test('importing a PDF shows only your modules and saves the rows you keep', async () => {
  const read: ImportAnswer = {
    layout: 'classes',
    modules: ['MCHM000', 'MPHS000'],
    classes: [
      { module: 'MCHM000', kind: 'lecture', weekday: 0, day: 'Monday', starts: '07:45', ends: '09:10', venue: 'CP4L001' },
      { module: 'MCHM000', kind: 'practical', weekday: 2, day: 'Wednesday', starts: '14:00', ends: '16:55', venue: null },
      { module: 'MPHS000', kind: 'lecture', weekday: 3, day: 'Thursday', starts: '09:15', ends: '10:40', venue: null },
    ],
    exams: [],
    lines: ['Found 3 classes for 2 modules, on Monday, Wednesday and Thursday.'],
  };
  (DocumentPicker.getDocumentAsync as jest.Mock<typeof DocumentPicker.getDocumentAsync>).mockResolvedValue({
    canceled: false, assets: [{ uri: 'file:///tt.pdf', name: 'tt.pdf', mimeType: 'application/pdf', lastModified: 0 }],
  });
  const importPdf = jest.spyOn(timetableApi, 'importPdf').mockResolvedValue(read);
  const addMany = jest.spyOn(timetableApi, 'addMany').mockResolvedValue({ entries: [], lines: [] });
  render(<ImportScreen />);
  fireEvent.press(screen.getByText('Choose a PDF'));
  expect(await screen.findByText(read.lines[0])).toBeTruthy();
  expect(importPdf).toHaveBeenCalledWith(expect.objectContaining({ uri: 'file:///tt.pdf', name: 'tt.pdf' }), 'classes');
  expect(screen.queryByText('Monday · 07:45 to 09:10 · CP4L001')).toBeNull(); // nothing until codes are chosen

  fireEvent.press(screen.getByText('MCHM000'));
  expect(screen.getByText('Monday · 07:45 to 09:10 · CP4L001')).toBeTruthy();
  expect(screen.queryByText('Thursday · 09:15 to 10:40')).toBeNull();
  fireEvent.press(screen.getByLabelText('Leave out MCHM000 Wednesday 14:00'));
  fireEvent.press(screen.getByText('Save 1 classes'));
  await waitFor(() =>
    expect(addMany).toHaveBeenCalledWith(
      [{ module: 'MCHM000', kind: 'lecture', weekday: 0, starts: '07:45', ends: '09:10', venue: 'CP4L001' }],
      false,
    ),
  );
});

test("plans of the student's own sit on their weekday or date, late ones in the row above", async () => {
  const { dayTimeProblem } = jest.requireActual<typeof import('../screens/ActivityEditScreen')>('../screens/ActivityEditScreen');
  expect(dayTimeProblem('22:30')).toBeNull();
  expect(dayTimeProblem('22:33')).toBe('Use 5-minute steps, like 08:30 or 08:35.');
  const days: Day[] = [{ date: '2026-10-31', weekday: 5, label: 'Sat 31', today: false }];
  const plan = (over: Partial<Activity>): Activity => ({
    id: 'p', title: 'Groceries', kind: 'errands', weekday: 5, on: null, day: 'Saturday', starts: '09:00', ends: '10:00',
    place: null, clashes: false, ...over,
  });
  render(
    <CalendarGrid
      days={days}
      classes={[]}
      events={[]}
      activities={[plan({}), plan({ id: 'late', title: 'Night out', weekday: null, on: '2026-10-31', starts: '22:30', ends: '23:30' }), plan({ id: 'tue', title: 'Gym', weekday: 1 })]}
      nowMinutes={null}
    />,
  );
  expect(await screen.findByText('Groceries')).toBeTruthy();
  expect(screen.getByText('22:30 Night out')).toBeTruthy();
  expect(screen.queryByText('Gym')).toBeNull();
});
