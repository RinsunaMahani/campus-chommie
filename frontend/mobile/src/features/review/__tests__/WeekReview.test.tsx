/**
 * Your week in review: the server's lines shown as sent, the tabs asking for the other week, spending bars that
 * never show a week without logs as R0, Support offered when a mark went down, and Home's card only on review days.
 */
import { beforeEach, expect, jest, test } from '@jest/globals';
import { act, fireEvent, render, screen } from '@testing-library/react-native';
import { router } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { reviewApi } from '../api/reviewApi';
import { HomeReviewCard } from '../components/HomeReviewCard';
import WeekReviewScreen from '../screens/WeekReviewScreen';
import { WeekReview } from '../types';

const wrap = (ui: React.ReactElement) =>
  render(
    <SafeAreaProvider
      initialMetrics={{ insets: { top: 0, left: 0, right: 0, bottom: 0 }, frame: { x: 0, y: 0, width: 360, height: 640 } }}>
      {ui}
    </SafeAreaProvider>,
  );

jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));
jest.mock('expo-router', () => ({
  router: { push: jest.fn(), back: jest.fn() },
  useFocusEffect: (cb: () => void) => cb(),
  useLocalSearchParams: () => ({}),
}));

const WEEK: WeekReview = {
  today: '2026-10-25',
  week: 'this',
  week_start: '2026-10-19',
  week_end: '2026-10-25',
  finished: true,
  ready: true,
  headline: '3 things done and 1 date in the next 7 days.',
  done: [
    { text: 'STK110 Semester test (Wed 21 Oct at 09:00)', kind: 'exam' },
    { text: 'You entered 1 mark: STK110 Test 2 (70%).', kind: 'marks' },
  ],
  coming: [{ text: 'STK110 Exam, in 4 days (Thu 29 Oct at 08:30)', kind: 'exam' }],
  marks: [{ code: 'STK110', before: 50, after: 60, direction: 'up', text: "STK110: your average went up from 50% to 60% with this week's marks." }],
  spending: {
    spent_cents: 50000,
    usual_cents: 80000,
    days: 7,
    weeks_compared: 2,
    direction: 'less',
    text: 'You spent R500 this week, R300 less than your usual of about R800 (from the last 2 weeks).',
    weeks: [null, null, 80000, 80000, 50000],
  },
  support: null,
};

beforeEach(() => {
  jest.restoreAllMocks();
  (router.push as jest.Mock).mockClear();
});

test('the review shows every line as the server wrote it', async () => {
  jest.spyOn(reviewApi, 'mine').mockResolvedValue(WEEK);
  wrap(<WeekReviewScreen />);
  expect(await screen.findByText(WEEK.headline)).toBeTruthy();
  for (const line of [...WEEK.done, ...WEEK.coming, ...WEEK.marks]) expect(screen.getByText(line.text)).toBeTruthy();
  expect(screen.getByText(WEEK.spending.text)).toBeTruthy();
  expect(screen.getByText('Mon 19 Oct 2026 to Sun 25 Oct 2026')).toBeTruthy();
  expect(screen.queryByText('Open Support')).toBeNull();
});

test('weeks with nothing logged say so, never R0', async () => {
  jest.spyOn(reviewApi, 'mine').mockResolvedValue(WEEK);
  wrap(<WeekReviewScreen />);
  await screen.findByText(WEEK.headline);
  expect(screen.getAllByText('no log')).toHaveLength(2);
  expect(screen.getByLabelText(/4 wk ago: nothing logged, 3 wk ago: nothing logged, 2 wk ago: R800, 1 wk ago: R800, This week: R500/)).toBeTruthy();
});

test('the other tab asks for last week', async () => {
  const mine = jest.spyOn(reviewApi, 'mine').mockResolvedValue(WEEK);
  wrap(<WeekReviewScreen />);
  await screen.findByText(WEEK.headline);
  mine.mockResolvedValue({ ...WEEK, week: 'last', headline: '1 thing done.' });
  fireEvent.press(screen.getByText('Last week'));
  expect(await screen.findByText('1 thing done.')).toBeTruthy();
  expect(mine).toHaveBeenLastCalledWith('last');
});

test('a mark that went down offers Support, and an empty week offers the check-in', async () => {
  jest.spyOn(reviewApi, 'mine').mockResolvedValue({
    ...WEEK,
    support: "If a mark knocked you this week, your campus's tutoring and counselling are there to help.",
    spending: { ...WEEK.spending, spent_cents: null, usual_cents: null, direction: 'unknown', text: 'No spending logged this week.', weeks: [null, null, null, null, null] },
  });
  wrap(<WeekReviewScreen />);
  fireEvent.press(await screen.findByText('Open Support'));
  expect(router.push).toHaveBeenCalledWith('/support');
  fireEvent.press(screen.getByText('Weekly money check-in'));
  expect(router.push).toHaveBeenCalledWith('/money/checkin');
});

test("Home's card shows only on review days, and opens the week it names", async () => {
  jest.spyOn(reviewApi, 'mine').mockResolvedValue({ ...WEEK, week: 'last' });
  const { unmount } = wrap(<HomeReviewCard />);
  fireEvent.press(await screen.findByText('Last week in review'));
  expect(router.push).toHaveBeenCalledWith({ pathname: '/review', params: { week: 'last' } });
  unmount();

  const notReady = jest.spyOn(reviewApi, 'mine').mockResolvedValue({ ...WEEK, ready: false });
  wrap(<HomeReviewCard />);
  await act(async () => {
    await notReady.mock.results[0]?.value;
  });
  expect(notReady).toHaveBeenCalledWith('auto');
  expect(screen.queryByText('Your week in review')).toBeNull();
});
