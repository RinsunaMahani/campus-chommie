/**
 * Tests for Weekly money check-in and Fixed costs (Task G4).
 * Non-shaming weekly streaks, fixed costs section, check-in flow.
 */
import { expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import MoneyScreen from '../screens/MoneyScreen';
import FixedCostEditScreen from '../screens/FixedCostEditScreen';
import WeeklyCheckinScreen from '../screens/WeeklyCheckinScreen';
import { moneyApi } from '../api/moneyApi';
import { CheckinStatus, FixedCost, MoneyPlan, SummaryReady } from '../types';

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
  today: '2026-10-18',
  late: false,
  late_days: 14,
  ready: true,
  balance: { cents: 100000, entered_cents: 100000, entered_on: '2026-10-18', lines: ['Balance entered on 18 Oct'] },
  pace: { daily_cents: 4000, low_cents: 3000, high_cents: 5000, days_logged: 10, from: 'spending', lines: ['About R40 a day'] },
  runway: {
    scenario: 'likely',
    runs_out_on: '2026-11-20',
    days: 33,
    earliest_on: null,
    latest_on: null,
    short_before_next: false,
    lines: ['Your money lasts about 33 days'],
  },
  safe_to_spend: { per_day_cents: 250, days_until_next: 12, essentials_cents: 48000, fixed_costs_cents: 25000, reserve_cents: 10000, lines: ['R2.50 a day'] },
  life_fund: { state: 'green', reason: 'Essentials and life fund covered', resume_hint: null, reserve_cents: 10000 },
  this_week: null,
  next_payment: { label: 'Allowance', expected_on: '2026-10-30', lands_on: '2026-10-30', amount_cents: 150000 },
  notes: [],
};

const mockPlan: MoneyPlan = {
  payday: {
    lands_on: '2026-10-30',
    day: 'Fri 30 Oct 2026',
    amount_cents: 150000,
    pots: [{ label: 'Rent', cents: 250000, why: 'Fixed cost due on the 1st' }],
    free_cents: 50000,
  },
  goals: [],
  university_dates: [],
  lines: ['Payday plan for 30 Oct'],
};

const mockFixedCosts: FixedCost[] = [
  { id: 'fc-1', label: 'Rent', amount_cents: 250000, day_of_month: 1 },
  { id: 'fc-2', label: 'Train pass', amount_cents: 45000, day_of_month: 15 },
];

const mockCheckinStatus: CheckinStatus = {
  checkin_day: 'sunday',
  is_checkin_day: true,
  checked_in_this_week: false,
  week_start: '2026-10-12',
  week_end: '2026-10-18',
  this_week: null,
  streak: {
    weeks: 3,
    line: '3 weeks in a row.',
  },
  recent_checkins: [],
};

test('MoneyScreen displays weekly check-in card with streak and fixed costs', async () => {
  jest.spyOn(moneyApi, 'summary').mockResolvedValue(mockSummary);
  jest.spyOn(moneyApi, 'plan').mockResolvedValue(mockPlan);
  jest.spyOn(moneyApi, 'checkinStatus').mockResolvedValue(mockCheckinStatus);
  jest.spyOn(moneyApi, 'fixedCosts').mockResolvedValue(mockFixedCosts);

  safeWrap(<MoneyScreen />);

  // Check check-in card
  const streaks = await screen.findAllByText('3 weeks in a row.');
  expect(streaks.length).toBeGreaterThan(0);

  // Check fixed costs
  const fixedCostsHeaders = screen.getAllByText('Fixed monthly costs');
  expect(fixedCostsHeaders.length).toBeGreaterThan(0);
  fireEvent.press(fixedCostsHeaders[0]);

  expect(await screen.findByText('Rent')).toBeTruthy();
  expect(screen.getByText('R2,500')).toBeTruthy();
  expect(screen.getByText('Train pass')).toBeTruthy();
  expect(screen.getByText('R450')).toBeTruthy();
});

test('WeeklyCheckinScreen allows entering spending or skipping', async () => {
  jest.spyOn(moneyApi, 'checkinStatus').mockResolvedValue(mockCheckinStatus);
  const submitSpy = jest.spyOn(moneyApi, 'submitCheckin').mockResolvedValue({
    ...mockCheckinStatus,
    checked_in_this_week: true,
  });

  safeWrap(<WeeklyCheckinScreen />);

  expect(await screen.findByText('3 weeks in a row.')).toBeTruthy();

  // Enter amount R700 and submit
  const input = screen.getByDisplayValue('');
  fireEvent.changeText(input, '700');

  const submitBtn = screen.getByText('Check in');
  fireEvent.press(submitBtn);

  expect(submitSpy).toHaveBeenCalledWith({ amount_cents: 70000, skipped: false });
});

test('FixedCostEditScreen allows saving a new fixed cost', async () => {
  const addSpy = jest.spyOn(moneyApi, 'addFixedCost').mockResolvedValue({
    id: 'fc-new',
    label: 'Data bundle',
    amount_cents: 15000,
    day_of_month: 25,
  });

  safeWrap(<FixedCostEditScreen />);

  const labelInput = screen.getByPlaceholderText('For example: Rent, train pass, data bundle, phone');
  fireEvent.changeText(labelInput, 'Data bundle');

  const amountInputs = screen.getAllByDisplayValue('');
  fireEvent.changeText(amountInputs[0], '150'); // amount

  const dayInput = screen.getByPlaceholderText('1');
  fireEvent.changeText(dayInput, '25'); // day 25

  const saveBtn = screen.getByText('Save');
  fireEvent.press(saveBtn);

  expect(addSpy).toHaveBeenCalledWith({
    label: 'Data bundle',
    amount_cents: 15000,
    day_of_month: 25,
  });
});
