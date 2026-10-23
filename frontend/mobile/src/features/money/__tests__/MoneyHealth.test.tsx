/**
 * Tests for Money Health Card (Task G5: Money health five checks).
 * Non-shaming checks, "Done" / "Not yet", tapping opens target screen.
 */
import { expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';
import { router } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { MoneyHealthCard } from '../components/MoneyHealthCard';
import MoneyScreen from '../screens/MoneyScreen';
import { moneyApi } from '../api/moneyApi';
import { MoneyHealth, MoneyPlan, SummaryReady } from '../types';

const safeWrap = (ui: React.ReactElement) =>
  render(
    <SafeAreaProvider
      initialMetrics={{
        insets: { top: 0, left: 0, right: 0, bottom: 0 },
        frame: { x: 0, y: 0, width: 360, height: 640 },
      }}>
      {ui}
    </SafeAreaProvider>,
  );

jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));
jest.mock('expo-router', () => ({
  router: { push: jest.fn(), back: jest.fn() },
  useFocusEffect: (cb: () => void) => cb(),
  useLocalSearchParams: () => ({}),
}));
jest.mock('@/features/profile/state', () => ({
  useProfile: () => ({ mock: false }),
}));

const mockSummary: SummaryReady = {
  today: '2026-10-12',
  late: false,
  late_days: 14,
  ready: true,
  balance: { cents: 100000, entered_cents: 100000, entered_on: '2026-10-12', lines: ['Balance entered on 12 Oct'] },
  pace: { daily_cents: 4000, low_cents: 3000, high_cents: 5000, days_logged: 10, from: 'spending', lines: ['About R40 a day'] },
  runway: {
    scenario: 'likely',
    runs_out_on: '2026-11-20',
    days: 39,
    earliest_on: null,
    latest_on: null,
    short_before_next: false,
    lines: ['Your money lasts about 39 days'],
  },
  safe_to_spend: { per_day_cents: 250, days_until_next: 20, essentials_cents: 80000, fixed_costs_cents: 0, reserve_cents: 10000, lines: ['R2.50 a day'] },
  life_fund: { state: 'green', reason: 'Essentials and life fund covered', resume_hint: null, reserve_cents: 10000 },
  this_week: null,
  next_payment: { label: 'Allowance', expected_on: '2026-11-01', lands_on: '2026-11-01', amount_cents: 150000 },
  notes: [],
};

const mockPlan: MoneyPlan = {
  payday: {
    lands_on: '2026-11-01',
    day: 'Sun 1 Nov 2026',
    amount_cents: 150000,
    pots: [{ label: 'Essentials', cents: 80000, why: 'R40 a day' }],
    free_cents: 70000,
  },
  goals: [],
  university_dates: [],
  lines: ['R700 free to spend.'],
};

const mockHealth: MoneyHealth = {
  checks: [
    {
      id: 'runway',
      title: 'Runway to payday',
      status: 'done',
      line: 'Money lasts until Sun 15 Nov, past your payment on Sun 1 Nov.',
      action: null,
      target: '/money',
    },
    {
      id: 'buffer',
      title: 'Emergency buffer',
      status: 'not yet',
      line: 'Your R500 buffer has R0 put aside so far.',
      action: 'Fund your buffer',
      target: '/money/goal',
    },
    {
      id: 'spending',
      title: 'Spending within safe limit',
      status: 'done',
      line: 'R150 spent this week, within your R280 weekly safe limit.',
      action: null,
      target: '/money',
    },
    {
      id: 'goals',
      title: 'Upcoming goals covered',
      status: 'done',
      line: 'No upcoming big purchase or fee deadlines to fund right now.',
      action: null,
      target: '/money',
    },
    {
      id: 'checkin',
      title: 'Weekly check-in',
      status: 'not yet',
      line: "You haven't checked in your spending for this week yet.",
      action: 'Check in now',
      target: '/money/checkin',
    },
  ],
  done_count: 3,
  total_count: 5,
  line: '3 of 5 checks done',
};

test('MoneyHealthCard displays check status and summary line', () => {
  safeWrap(<MoneyHealthCard health={mockHealth} />);

  expect(screen.getByText('Money health')).toBeTruthy();
  expect(screen.getByText('3 of 5 done')).toBeTruthy();

  // Check runway (done)
  expect(screen.getByText('Runway to payday')).toBeTruthy();
  expect(screen.getByText('Money lasts until Sun 15 Nov, past your payment on Sun 1 Nov.')).toBeTruthy();

  // Check buffer (not yet)
  expect(screen.getByText('Emergency buffer')).toBeTruthy();
  expect(screen.getByText('Your R500 buffer has R0 put aside so far.')).toBeTruthy();
  expect(screen.getByText('Fund your buffer')).toBeTruthy();

  // Check checkin (not yet)
  expect(screen.getByText('Weekly check-in')).toBeTruthy();
  expect(screen.getByText('Check in now')).toBeTruthy();
});

test('MoneyHealthCard navigates to action target when pressed', () => {
  safeWrap(<MoneyHealthCard health={mockHealth} />);

  const fundBufferAction = screen.getByText('Fund your buffer');
  fireEvent.press(fundBufferAction);
  expect(router.push).toHaveBeenCalledWith('/money/goal');

  const checkinAction = screen.getByText('Check in now');
  fireEvent.press(checkinAction);
  expect(router.push).toHaveBeenCalledWith('/money/checkin');
});

test('MoneyScreen loads and displays MoneyHealthCard', async () => {
  jest.spyOn(moneyApi, 'summary').mockResolvedValue(mockSummary);
  jest.spyOn(moneyApi, 'plan').mockResolvedValue(mockPlan);
  jest.spyOn(moneyApi, 'checkinStatus').mockResolvedValue(null as any);
  jest.spyOn(moneyApi, 'fixedCosts').mockResolvedValue([]);
  jest.spyOn(moneyApi, 'health').mockResolvedValue(mockHealth);

  safeWrap(<MoneyScreen />);

  expect(await screen.findByText('Money health')).toBeTruthy();
  expect(screen.getByText('3 of 5 done')).toBeTruthy();
  expect(screen.getByText('Runway to payday')).toBeTruthy();
  expect(screen.getByText('Emergency buffer')).toBeTruthy();
});

