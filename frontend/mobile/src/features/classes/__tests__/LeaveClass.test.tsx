/**
 * Leaving a class: asked first, then gone back to the list; the only rep is warned that nobody else can confirm;
 * a failure stays on the screen and says so.
 */
import { beforeEach, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { router } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { ApiError } from '@/shared/api/client';

import { classesApi } from '../api/classesApi';
import ClassScreen from '../screens/ClassScreen';
import { ClassSummary } from '../types';

jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));
jest.mock('expo-router', () => ({
  router: { push: jest.fn(), back: jest.fn() },
  // Like the real one: runs when the screen gains focus (once here), not on every render.
  useFocusEffect: (cb: () => void) => jest.requireActual<typeof import('react')>('react').useEffect(cb, [cb]),
  useLocalSearchParams: () => ({ id: 'c1' }),
}));

const CLASS: ClassSummary = {
  id: 'c1', university: 'up', university_name: 'University of Pretoria', campus: null, campus_name: null,
  module_code: 'STK110', module_name: 'Statistics', year: 2026, invite_code: 'ABC123', role: 'student', members: 30, reps: 2,
};

const wrap = () =>
  render(
    <SafeAreaProvider initialMetrics={{ insets: { top: 0, left: 0, right: 0, bottom: 0 }, frame: { x: 0, y: 0, width: 360, height: 640 } }}>
      <ClassScreen />
    </SafeAreaProvider>,
  );

function given(cls: ClassSummary) {
  jest.spyOn(classesApi, 'mine').mockResolvedValue([cls]);
  jest.spyOn(classesApi, 'events').mockResolvedValue([]);
  jest.spyOn(classesApi, 'candidates').mockResolvedValue([]);
}

beforeEach(() => {
  jest.restoreAllMocks();
  (router.back as jest.Mock).mockClear();
});

test('leaving asks first, then leaves and goes back', async () => {
  given(CLASS);
  const leave = jest.spyOn(classesApi, 'leave').mockResolvedValue({});
  wrap();
  fireEvent.press(await screen.findByText('Leave this class'));
  expect(screen.getByText('Leave STK110?')).toBeTruthy();
  expect(screen.getByText(/leave your week/)).toBeTruthy();
  expect(leave).not.toHaveBeenCalled();
  fireEvent.press(screen.getAllByText('Leave this class')[1]);
  await waitFor(() => expect(router.back).toHaveBeenCalled());
  expect(leave).toHaveBeenCalledWith('c1');
});

test('cancel leaves nothing', async () => {
  given(CLASS);
  const leave = jest.spyOn(classesApi, 'leave').mockResolvedValue({});
  wrap();
  fireEvent.press(await screen.findByText('Leave this class'));
  fireEvent.press(screen.getByText('Cancel'));
  expect(leave).not.toHaveBeenCalled();
});

test('the only rep is told nobody else can confirm', async () => {
  given({ ...CLASS, role: 'rep', reps: 1 });
  wrap();
  fireEvent.press(await screen.findByText('Leave this class'));
  expect(screen.getByText(/only class rep/)).toBeTruthy();
});

test('a failure stays on the screen and says so', async () => {
  given(CLASS);
  jest.spyOn(classesApi, 'leave').mockRejectedValue(new ApiError(404, 'CLASS_NOT_FOUND', "We couldn't find that class."));
  wrap();
  fireEvent.press(await screen.findByText('Leave this class'));
  fireEvent.press(screen.getAllByText('Leave this class')[1]);
  expect(await screen.findByText("We couldn't find that class.")).toBeTruthy();
  expect(screen.getByText('Leave this class')).toBeTruthy(); // still on the class, able to try again
  expect(router.back).not.toHaveBeenCalled();
});
