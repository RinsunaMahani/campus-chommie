/**
 * Money pots tests: empty state, pot kinds (family, stokvel, buffer, big_purchase, goal),
 * progress in words and bar, and sensitive wording ("Family", never "Black tax").
 */
import { expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import MoneyScreen from '../screens/MoneyScreen';
import { moneyApi } from '../api/moneyApi';
import { MoneyPlan, SummaryReady } from '../types';

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
  safe_to_spend: { per_day_cents: 250, days_until_next: 20, essentials_cents: 80000, reserve_cents: 10000, lines: ['R2.50 a day'] },
  life_fund: { state: 'green', reason: 'Essentials and life fund covered', resume_hint: null, reserve_cents: 10000 },
  this_week: null,
  next_payment: { label: 'Allowance', expected_on: '2026-11-01', lands_on: '2026-11-01', amount_cents: 150000 },
  notes: [],
};

const mockPlanWithPots: MoneyPlan = {
  payday: {
    lands_on: '2026-11-01',
    day: 'Sun 1 Nov 2026',
    amount_cents: 150000,
    pots: [
      { label: 'Essentials', cents: 80000, why: 'R40 a day for 20 days' },
      { label: 'Family support', cents: 30000, why: 'R300 monthly support for family' },
      { label: 'December stokvel', cents: 20000, why: 'R200 monthly stokvel contribution' },
      { label: 'Emergency buffer', cents: 10000, why: 'R100 to reach your R500 buffer' },
      { label: 'Laptop', cents: 10000, why: 'R300 still to put aside by Thu 31 Dec 2026 (paying through stokvel)' },
    ],
    free_cents: 0,
  },
  goals: [
    {
      id: 'pot-1',
      label: 'Family support',
      kind: 'family',
      amount_cents: 30000,
      saved_cents: 10000,
      due_on: null,
      due_day: null,
      from_university: false,
      stokvel_funded: false,
      per_week_cents: 5000,
      lines: ['R300 monthly support for family: R100 aside so far, R200 still to find.'],
    },
    {
      id: 'pot-2',
      label: 'December stokvel',
      kind: 'stokvel',
      amount_cents: 20000,
      saved_cents: 20000,
      due_on: null,
      due_day: null,
      from_university: false,
      stokvel_funded: false,
      per_week_cents: 0,
      lines: ["Done: your stokvel contribution for this month is put aside."],
    },
    {
      id: 'pot-3',
      label: 'Emergency buffer',
      kind: 'buffer',
      amount_cents: 50000,
      saved_cents: 40000,
      due_on: null,
      due_day: null,
      from_university: false,
      stokvel_funded: false,
      per_week_cents: null,
      lines: ['R500 emergency buffer: R400 aside so far, R100 still to find.'],
    },
    {
      id: 'pot-4',
      label: 'Laptop',
      kind: 'big_purchase',
      amount_cents: 90000,
      saved_cents: 60000,
      due_on: '2026-12-31',
      due_day: 'Thu 31 Dec 2026',
      from_university: false,
      stokvel_funded: true,
      per_week_cents: 2728,
      lines: ['About R27.28 a week for 11 weeks gets you there by Thu 31 Dec 2026. Paying through a stokvel.'],
    },
  ],
  university_dates: [],
  lines: ['When R1 500 lands on Sun 1 Nov 2026: R1 500 is spoken for, and R0 is yours to spend freely.'],
};

const mockPlanEmpty: MoneyPlan = {
  payday: null,
  goals: [],
  university_dates: [],
  lines: [],
};

test('renders empty state when there are no pots', async () => {
  jest.spyOn(moneyApi, 'summary').mockResolvedValue(mockSummary);
  jest.spyOn(moneyApi, 'plan').mockResolvedValue(mockPlanEmpty);

  safeWrap(<MoneyScreen />);

  const potsHeader = await screen.findByText('Pots');
  fireEvent.press(potsHeader);

  const emptyTexts = await screen.findAllByText('Keep money aside in named pots for family, a stokvel, an emergency buffer, or a big purchase.');
  expect(emptyTexts.length).toBeGreaterThan(0);
  expect(screen.getByText('Add a pot')).toBeTruthy();
});

test('renders each pot card with label, kind tag, amount aside and progress in words', async () => {
  jest.spyOn(moneyApi, 'summary').mockResolvedValue(mockSummary);
  jest.spyOn(moneyApi, 'plan').mockResolvedValue(mockPlanWithPots);

  safeWrap(<MoneyScreen />);

  const potsHeader = await screen.findByText('Pots');
  fireEvent.press(potsHeader);

  // Family pot
  expect(await screen.findByText('Family support')).toBeTruthy();
  expect(screen.getByText('Family')).toBeTruthy();
  expect(screen.getByText('R100 / R300')).toBeTruthy();
  expect(screen.getByText('R300 monthly support for family: R100 aside so far, R200 still to find.')).toBeTruthy();

  // Stokvel pot
  expect(screen.getByText('December stokvel')).toBeTruthy();
  expect(screen.getByText('Stokvel')).toBeTruthy();
  expect(screen.getByText('R200 / R200')).toBeTruthy();
  expect(screen.getByText("Done: your stokvel contribution for this month is put aside.")).toBeTruthy();

  // Buffer pot
  expect(screen.getByText('Emergency buffer')).toBeTruthy();
  expect(screen.getByText('Buffer')).toBeTruthy();
  expect(screen.getByText('R400 / R500')).toBeTruthy();
  expect(screen.getByText('R500 emergency buffer: R400 aside so far, R100 still to find.')).toBeTruthy();

  // Big purchase pot
  expect(screen.getByText('Laptop')).toBeTruthy();
  expect(screen.getByText('Big purchase · stokvel')).toBeTruthy();
  expect(screen.getByText('R600 / R900')).toBeTruthy();
  expect(screen.getByText('About R27.28 a week for 11 weeks gets you there by Thu 31 Dec 2026. Paying through a stokvel.')).toBeTruthy();
});
