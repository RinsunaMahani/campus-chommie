/**
 * Find my course's tabs: marks are remembered on the phone only when the learner switches it on (and
 * forgotten when switched off); Home says what to do next and what closes soon; Explore lists universities
 * with their fee and status, and colleges behind a toggle; Courses groups a university's programmes by
 * faculty without marks; a university's overview leads to Courses and How to apply on their own screens.
 */
import { beforeEach, expect, jest, test } from '@jest/globals';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import * as SecureStore from 'expo-secure-store';
import { ReactNode } from 'react';
import { Text } from 'react-native';

import { collegesApi } from '@/features/colleges/api/collegesApi';

import { courseFinderApi } from '../api/courseFinderApi';
import CoursesScreen from '../screens/CoursesScreen';
import ExploreScreen from '../screens/ExploreScreen';
import FinderHomeScreen from '../screens/FinderHomeScreen';
import UniversityScreen from '../screens/UniversityScreen';
import { CourseFinderProvider, useCourseFinder } from '../state';
import { ApplyInfoAnswer, ProgrammeRow, UniversityCardInfo } from '../types';

const mockPush = jest.fn();
jest.mock('expo-router', () => ({
  router: { push: (...args: unknown[]) => mockPush(...args), back: jest.fn(), canGoBack: () => true, replace: jest.fn() },
  useLocalSearchParams: () => ({ id: 'uj' }),
  Redirect: () => null,
}));
jest.mock('react-native-safe-area-context', () => {
  const actual = jest.requireActual<object>('react-native-safe-area-context');
  return { ...actual, useSafeAreaInsets: () => ({ top: 0, left: 0, right: 0, bottom: 0 }) };
});
jest.mock('expo-web-browser', () => ({ openBrowserAsync: jest.fn() }));
jest.mock('@expo/vector-icons', () => ({ Feather: () => null }));
const mockStore: Record<string, string> = {};
jest.mock('expo-secure-store', () => ({
  getItemAsync: jest.fn(async (k: string) => mockStore[k] ?? null),
  setItemAsync: jest.fn(async (k: string, v: string) => {
    mockStore[k] = v;
  }),
  deleteItemAsync: jest.fn(async (k: string) => {
    delete mockStore[k];
  }),
}));

const KEY = 'campus-chommie.marks.v1';
const wrap = (ui: ReactNode) => render(<CourseFinderProvider>{ui}</CourseFinderProvider>);

const uj: UniversityCardInfo = {
  id: 'uj', name: 'University of Johannesburg', city: 'Johannesburg', academic_year: 2027, programmes: 52,
  confirmed: false, notice: 'Not yet confirmed by the team.', fee_cents: 0,
  applications: { intake: 2027, status: 'closing_soon', label: 'Closing soon', opens: '2026-04-01', closes: '2026-10-31', days: 11, lines: [] },
};
const smu: UniversityCardInfo = { ...uj, id: 'smu', name: 'Sefako Makgatho Health Sciences University', city: 'Ga-Rankuwa', fee_cents: null, applications: null };
const row = (over: Partial<ProgrammeRow>): ProgrammeRow => ({
  university: 'uj', university_name: 'University of Johannesburg', programme: 'p', name: 'BA', faculty: 'Humanities',
  fields: ['humanities'], min_points: 28, selective: false, verified: true, ...over,
});

beforeEach(() => {
  jest.restoreAllMocks();
  mockPush.mockClear();
  for (const k of Object.keys(mockStore)) delete mockStore[k];
});

function RememberProbe() {
  const cf = useCourseFinder();
  return (
    <>
      <Text>{cf.remember ? 'on' : 'off'}</Text>
      <Text>{cf.rows.map((r) => `${r.subject}=${r.percent}`).join(',')}</Text>
      <Text onPress={() => cf.setRemember(!cf.remember)}>toggle</Text>
      <Text onPress={() => cf.setRows([{ subject: 'mathematics', percent: '71' }])}>type</Text>
    </>
  );
}

test('marks stay on the phone only while remembering is on', async () => {
  wrap(<RememberProbe />);
  expect(await screen.findByText('off')).toBeTruthy();
  fireEvent.press(screen.getByText('type'));
  expect(SecureStore.setItemAsync).not.toHaveBeenCalled(); // off by default: nothing kept

  await act(async () => fireEvent.press(screen.getByText('toggle')));
  expect(JSON.parse(mockStore[KEY])).toEqual([{ subject: 'mathematics', percent: '71' }]);

  await act(async () => fireEvent.press(screen.getByText('toggle')));
  expect(mockStore[KEY]).toBeUndefined(); // switching off deletes them
});

test('remembered marks come back on the next visit', async () => {
  mockStore[KEY] = JSON.stringify([{ subject: 'english', percent: '65' }]);
  wrap(<RememberProbe />);
  expect(await screen.findByText('on')).toBeTruthy();
  expect(screen.getByText('english=65')).toBeTruthy();
});

test('stored junk is ignored, never trusted', async () => {
  mockStore[KEY] = JSON.stringify([{ subject: 42, percent: { evil: true } }]);
  wrap(<RememberProbe />);
  await waitFor(() => expect(SecureStore.getItemAsync).toHaveBeenCalled());
  expect(screen.getByText('off')).toBeTruthy();
});

test('home says to add marks first and shows what closes soon', async () => {
  jest.spyOn(courseFinderApi, 'deadlines').mockResolvedValue({
    today: '2026-10-20',
    deadlines: [{ kind: 'university', id: 'uj', name: 'University of Johannesburg', status: 'closing_soon', label: 'Closing soon', closes: '2026-10-31', days: 11, line: 'Applications for 2027 close in 11 days.' }],
  });
  wrap(<FinderHomeScreen />);
  expect(await screen.findByText('Applications for 2027 close in 11 days.')).toBeTruthy();
  fireEvent.press(screen.getByText('Add my marks'));
  expect(mockPush).toHaveBeenCalledWith('/course-finder/marks');
  fireEvent.press(screen.getByText('University of Johannesburg'));
  expect(mockPush).toHaveBeenCalledWith('/course-finder/university/uj');
});

test('explore lists universities with fee and status, searches, and switches to colleges', async () => {
  jest.spyOn(courseFinderApi, 'universities').mockResolvedValue([smu, uj]);
  const colleges = jest.spyOn(collegesApi, 'list').mockResolvedValue({ summary: '357 colleges.', total: 0, page: 1, pages: 1, colleges: [], confirmed: false, notice: null });
  wrap(<ExploreScreen />);
  expect(await screen.findByText('Free to apply')).toBeTruthy();
  expect(screen.getByText('Fee not verified yet')).toBeTruthy();
  expect(screen.getByText('Closing soon')).toBeTruthy();

  fireEvent.changeText(screen.getByLabelText('Search universities'), 'ga-rank');
  expect(screen.queryByText('University of Johannesburg')).toBeNull();
  expect(screen.getByText('Sefako Makgatho Health Sciences University')).toBeTruthy();

  fireEvent.press(screen.getByRole('tab', { name: 'Colleges' }));
  expect(await screen.findByText('357 colleges.')).toBeTruthy();
  expect(colleges).toHaveBeenCalled();
});

test('courses without marks: a university by faculty, with minimum points as published', async () => {
  jest.spyOn(courseFinderApi, 'universities').mockResolvedValue([uj]);
  const programmes = jest.spyOn(courseFinderApi, 'programmes').mockResolvedValue({
    summary: '2 programmes at 1 university.', total: 2, page: 1, pages: 1,
    programmes: [row({ programme: 'ba', name: 'BA Psychology' }), row({ programme: 'bsc', name: 'BSc Nursing', faculty: 'Health Sciences', fields: ['nursing'], min_points: null, verified: false })],
  });
  wrap(<CoursesScreen />);
  expect(await screen.findByText('Pick a university above, or search every programme.')).toBeTruthy();
  fireEvent.press(await screen.findByLabelText('University of Johannesburg'));
  expect(await screen.findByText('Humanities')).toBeTruthy();
  expect(programmes).toHaveBeenCalledWith({ university: 'uj' });
  expect(screen.getByText('Health Sciences')).toBeTruthy();
  expect(screen.getByText('Minimum 28 points')).toBeTruthy(); // the first faculty starts open
  expect(screen.getByText('Add your marks to see which of these you meet.')).toBeTruthy();
});

test('a university overview leads to courses and how to apply, without marks', async () => {
  const info = {
    university: { id: 'uj', name: 'University of Johannesburg', city: 'Johannesburg', academic_year: 2027, programmes: 52, confirmed: true, notice: null },
    apply: { today: '2026-10-20', test_date: false, guide: { fee_cents: 0, windows: [{ intake: 2027, heading: 'Applications for 2027', status: 'closing_soon', label: 'Closing soon', opens: null, closes: '2026-10-31', closes_one_of: [], late_opens: null, late_closes: null, next_date: '2026-10-31', days: 11, lines: ['Closes on Sat 31 Oct 2026 (in 11 days).'], source_url: null }] } },
  } as unknown as ApplyInfoAnswer;
  jest.spyOn(courseFinderApi, 'applyInfo').mockResolvedValue(info);
  wrap(<UniversityScreen />);
  expect(await screen.findByText('Closes on Sat 31 Oct 2026 (in 11 days).')).toBeTruthy();
  expect(screen.getByText('Free to apply')).toBeTruthy();
  expect(screen.getByText('52 programmes, by faculty')).toBeTruthy();
  fireEvent.press(screen.getByText('Courses'));
  expect(mockPush).toHaveBeenCalledWith('/course-finder/university/uj/courses');
  fireEvent.press(screen.getByText('How to apply'));
  expect(mockPush).toHaveBeenCalledWith('/course-finder/university/uj/apply');
});
