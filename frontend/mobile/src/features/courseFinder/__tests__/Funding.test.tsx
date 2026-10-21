/**
 * Task 1 tests:
 * - the footer shows Funding and not "Change goal"
 * - NSFAS opens its page
 * - a funder without covers shows "Not published by the funder"
 * - a funder whose covers name no amount shows the "doesn't publish an amount" line
 * - fee formatting (15000 is "R150", null is "No fee published")
 * - the list filters by field
 * - "All" opens in groups (who offers it, and the missing middle) instead of one long list
 */
import { beforeEach, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';

import { updatesApi } from '@/features/updates/api/updatesApi';
import UpdatesScreen from '@/features/updates/screens/UpdatesScreen';

import { courseFinderApi } from '../api/courseFinderApi';
import FunderDetailScreen from '../screens/FunderDetailScreen';
import FundingScreen from '../screens/FundingScreen';
import PlanScreen from '../screens/PlanScreen';
import { FunderDetail, FundingListAnswer, Plan, SavedFundingCard, SavedFundingListAnswer } from '../types';
import fundingListFixture from './fixtures/fundingList.json';
import nsfasFixture from './fixtures/fundingFunder.json';
import planFixture from './fixtures/plan.json';

const mockPush = jest.fn();
const mockBack = jest.fn();
const mockDismissTo = jest.fn();
let mockParams: Record<string, string> = { id: 'nsfas' };

jest.mock('expo-router', () => ({
  router: {
    push: (...args: unknown[]) => mockPush(...args),
    back: (...args: unknown[]) => mockBack(...args),
    dismissTo: (...args: unknown[]) => mockDismissTo(...args),
  },
  Redirect: () => null,
  useLocalSearchParams: () => mockParams,
  useFocusEffect: (cb: () => void) => {
    const React = jest.requireActual<typeof import('react')>('react');
    React.useEffect(() => {
      cb();
    }, [cb]);
  },
}));

let mockSessionStatus: 'signedOut' | 'unverified' | 'active' = 'signedOut';

jest.mock('@/features/auth/session/SessionProvider', () => ({
  useSession: () => ({ status: mockSessionStatus }),
}));

jest.mock('react-native-safe-area-context', () => {
  const actual = jest.requireActual<object>('react-native-safe-area-context');
  return {
    ...actual,
    useSafeAreaInsets: () => ({ top: 0, left: 0, right: 0, bottom: 0 }),
  };
});

jest.mock('expo-web-browser', () => ({ openBrowserAsync: jest.fn() }));
jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));
jest.mock('@/shared/motion/motion', () => ({
  ...jest.requireActual<object>('@/shared/motion/motion'),
  motionOff: () => true,
}));

const mockPlan = (planFixture as unknown as { data: { plan: Plan } }).data.plan;
const mockReset = jest.fn();

let mockCourseFinderState = {
  plan: mockPlan,
  university: { id: 'smu', name: 'Sefako Makgatho Health Sciences University' },
  reset: mockReset,
};

jest.mock('../state', () => ({
  useCourseFinder: () => mockCourseFinderState,
}));

const fundingListData = (fundingListFixture as unknown as { data: FundingListAnswer }).data;
const nsfasData = (nsfasFixture as unknown as { data: { funder: FunderDetail } }).data.funder;

beforeEach(() => {
  jest.clearAllMocks();
  mockParams = { id: 'nsfas' };
  mockSessionStatus = 'signedOut';
  mockCourseFinderState = {
    plan: mockPlan,
    university: { id: 'smu', name: 'Sefako Makgatho Health Sciences University' },
    reset: mockReset,
  };
});

test('PlanScreen footer shows Funding and not "Change goal", and Start again is reachable near top', () => {
  render(<PlanScreen />);

  // Footer has Funding button
  const fundingBtn = screen.getByRole('button', { name: 'Funding' });
  expect(fundingBtn).toBeTruthy();

  // Footer does NOT have Change goal
  expect(screen.queryByRole('button', { name: 'Change goal' })).toBeNull();

  // Start again is reachable near top
  const startAgain = screen.getByRole('button', { name: 'Start again' });
  expect(startAgain).toBeTruthy();

  // Pressing Funding navigates to funding hub
  fireEvent.press(fundingBtn);
  expect(mockPush).toHaveBeenCalledWith('/course-finder/funding');

  // Pressing Start again resets and dismisses to course finder root
  fireEvent.press(startAgain);
  expect(mockReset).toHaveBeenCalled();
  expect(mockDismissTo).toHaveBeenCalledWith('/course-finder');
});

test('FundingScreen: NSFAS opens its page', async () => {
  jest.spyOn(courseFinderApi, 'fundingList').mockResolvedValue(fundingListData);

  render(<FundingScreen />);

  await waitFor(() => {
    expect(screen.getByText('24 funding options: 5 open now.')).toBeTruthy();
  });

  // Tap NSFAS card
  const nsfasCard = screen.getByText('National Student Financial Aid Scheme (NSFAS)');
  expect(nsfasCard).toBeTruthy();
  fireEvent.press(nsfasCard);

  expect(mockPush).toHaveBeenCalledWith('/course-finder/funding/nsfas');
});

test('FundingScreen: the list filters by field', async () => {
  jest.spyOn(courseFinderApi, 'fundingList').mockResolvedValue(fundingListData);

  render(<FundingScreen />);

  await waitFor(() => {
    expect(screen.getByText('24 funding options: 5 open now.')).toBeTruthy();
  });

  // Initially the other funders sit in closed groups; Companies opens to pharmacy-only Clicks Foundation
  expect(screen.queryByText('Clicks Foundation Bursary Fund')).toBeNull();
  fireEvent.press(screen.getByRole('button', { name: 'Companies. 6 funders: 1 open now.' }));
  expect(screen.getByText('Clicks Foundation Bursary Fund')).toBeTruthy();

  // Filter by Agriculture (which has Sasol Foundation)
  const agriChip = screen.getByText('Agriculture');
  fireEvent.press(agriChip);

  // Sasol Foundation is shown
  expect(screen.getByText('Sasol Foundation Bursary Programme')).toBeTruthy();
  // Clicks Foundation (pharmacy only) is NOT shown
  expect(screen.queryByText('Clicks Foundation Bursary Fund')).toBeNull();
});

test("FundingScreen: the missing middle has its own group, in the funders' own words", async () => {
  jest.spyOn(courseFinderApi, 'fundingList').mockResolvedValue(fundingListData);

  render(<FundingScreen />);

  const group = await screen.findByRole('button', { name: 'If your family earns too much for NSFAS. 5 funders: 0 open now.' });
  expect(screen.getByRole('button', { name: 'Government. 11 funders: 3 open now.' })).toBeTruthy();
  expect(screen.getByRole('button', { name: 'Through your university. 3 funders: 0 open now.' })).toBeTruthy();
  fireEvent.press(group);

  expect(screen.getByText(/we never ask what your family earns/)).toBeTruthy();
  expect(screen.getByText('Sasol Foundation Bursary Programme')).toBeTruthy();
  expect(
    screen.getByText('In their words: "A combined household income under R800 000 a year, and under 25 when you apply"'),
  ).toBeTruthy();
  // NSFAS's own limit is on its card, never in this group
  expect(screen.queryByText(/In their words: "Students from households/)).toBeNull();
});

test('FunderDetailScreen: a funder without covers shows "Not published by the funder."', async () => {
  mockParams = { id: 'nsfas' };
  jest.spyOn(courseFinderApi, 'funder').mockResolvedValue(nsfasData);

  render(<FunderDetailScreen />);

  await waitFor(() => {
    expect(screen.getByText('National Student Financial Aid Scheme (NSFAS)')).toBeTruthy();
  });

  // Covers is null on NSFAS -> shows "Not published by the funder."
  expect(screen.getByText('Not published by the funder.')).toBeTruthy();
  // Obligations is null -> section heading is hidden
  expect(screen.queryByText('What you owe back')).toBeNull();
  // Sources is present
  expect(screen.getByText('Sources')).toBeTruthy();
});

test('FunderDetailScreen: a funder whose covers name no amount shows the "doesn\'t publish an amount" line', async () => {
  mockParams = { id: 'clicks_foundation' };
  const clicksFunder: FunderDetail = {
    ...nsfasData,
    id: 'clicks_foundation',
    name: 'Clicks Foundation Bursary Fund',
    covers: {
      items: ['Registration fees', 'Tuition fees', 'Prescribed textbooks'],
      source_url: 'https://careers.clicksgroup.co.za/',
    },
    apply: {
      ...nsfasData.apply,
      fee_cents: null,
    },
  };
  jest.spyOn(courseFinderApi, 'funder').mockResolvedValue(clicksFunder);

  render(<FunderDetailScreen />);

  await waitFor(() => {
    expect(screen.getByText('Clicks Foundation Bursary Fund')).toBeTruthy();
  });

  expect(screen.getByText('Registration fees')).toBeTruthy();
  expect(screen.getByText("The funder doesn't publish an amount.")).toBeTruthy();
});

test('FunderDetailScreen: a funder whose covers name an amount does not show "doesn\'t publish an amount"', async () => {
  mockParams = { id: 'up_flyup_awards' };
  const flyupFunder: FunderDetail = {
    ...nsfasData,
    id: 'up_flyup_awards',
    name: 'UP Fly@UP Awards',
    covers: {
      items: ['In 2026: R18 000 for an average of 80% to 89.99%, or R45 000 for 90% to 100%'],
      source_url: 'https://www.up.ac.za/',
    },
  };
  jest.spyOn(courseFinderApi, 'funder').mockResolvedValue(flyupFunder);

  render(<FunderDetailScreen />);

  await waitFor(() => {
    expect(screen.getByText('UP Fly@UP Awards')).toBeTruthy();
  });

  expect(screen.queryByText("The funder doesn't publish an amount.")).toBeNull();
});

test('FunderDetailScreen: fee formatting (15000 is "R150", null is "No fee published")', async () => {
  // Test with fee_cents: 15000
  mockParams = { id: 'fee_test' };
  const funderWithFee: FunderDetail = {
    ...nsfasData,
    id: 'fee_test',
    apply: {
      ...nsfasData.apply,
      fee_cents: 15000,
    },
  };
  jest.spyOn(courseFinderApi, 'funder').mockResolvedValue(funderWithFee);

  const { unmount } = render(<FunderDetailScreen />);

  await waitFor(() => {
    expect(screen.getByText('R150')).toBeTruthy();
  });

  unmount();

  // Test with fee_cents: null
  mockParams = { id: 'no_fee_test' };
  const funderNoFee: FunderDetail = {
    ...nsfasData,
    id: 'no_fee_test',
    apply: {
      ...nsfasData.apply,
      fee_cents: null,
    },
  };
  jest.spyOn(courseFinderApi, 'funder').mockResolvedValue(funderNoFee);

  render(<FunderDetailScreen />);

  await waitFor(() => {
    expect(screen.getByText('No fee published')).toBeTruthy();
  });
});

test('Saved funding (signed out): tapping Save asks the learner to sign in', async () => {
  mockSessionStatus = 'signedOut';
  jest.spyOn(courseFinderApi, 'fundingList').mockResolvedValue(fundingListData);

  render(<FundingScreen />);

  await waitFor(() => {
    expect(screen.getByText('24 funding options: 5 open now.')).toBeTruthy();
  });

  const saveNsfasBtn = screen.getByRole('button', {
    name: 'Save National Student Financial Aid Scheme (NSFAS)',
  });
  fireEvent.press(saveNsfasBtn);

  expect(
    screen.getByText('Sign in to save funding and get reminders when it opens and before it closes.'),
  ).toBeTruthy();

  const signInBtn = screen.getByRole('button', { name: 'Sign in' });
  fireEvent.press(signInBtn);
  expect(mockPush).toHaveBeenCalledWith('/(auth)/sign-in');
});

test('Saved funding (signed in): saves, unsaves, and shows the Saved list with saved_on date', async () => {
  mockSessionStatus = 'active';
  const clicksCard = fundingListData.funders.find((f) => f.id === 'clicks_foundation')!;
  const savedClicks: SavedFundingCard = {
    ...clicksCard,
    saved_on: '2026-10-15',
  };
  const savedListAnswer: SavedFundingListAnswer = {
    today: '2026-10-15',
    summary: '1 funding option: 0 open now.',
    counts: { total: 1, open_now: 0, closing_soon: 0 },
    funders: [savedClicks],
    confirmed: false,
    notice: fundingListData.notice,
  };

  jest.spyOn(courseFinderApi, 'fundingList').mockResolvedValue(fundingListData);
  jest.spyOn(courseFinderApi, 'savedFundingList').mockResolvedValue(savedListAnswer);
  const saveSpy = jest.spyOn(courseFinderApi, 'saveFunder').mockImplementation(async (id) => ({
    ...fundingListData.funders.find((f) => f.id === id)!,
    saved_on: '2026-10-16',
  }));
  const unsaveSpy = jest.spyOn(courseFinderApi, 'unsaveFunder').mockResolvedValue({} as Record<string, never>);

  render(<FundingScreen />);

  // Clicks Foundation sits in the Companies group, closed until opened
  fireEvent.press(await screen.findByRole('button', { name: 'Companies. 6 funders: 1 open now.' }));
  await waitFor(() => {
    expect(screen.getByText('Saved on Thu 15 Oct 2026')).toBeTruthy();
  });

  // Filter by "Saved" chip
  const savedChip = screen.getByLabelText('Saved');
  fireEvent.press(savedChip);

  // Shows saved Clicks Foundation, not Sasol
  expect(screen.getByText('Clicks Foundation Bursary Fund')).toBeTruthy();
  expect(screen.queryByText('Sasol Foundation Bursary Programme')).toBeNull();

  // Save NSFAS via its bookmark button
  const saveNsfasBtn = screen.getByRole('button', {
    name: 'Save National Student Financial Aid Scheme (NSFAS)',
  });
  fireEvent.press(saveNsfasBtn);

  await waitFor(() => {
    expect(saveSpy).toHaveBeenCalledWith('nsfas');
    expect(screen.getAllByText('Saved on Fri 16 Oct 2026').length).toBeGreaterThan(0);
  });

  // Unsave Clicks Foundation
  const unsaveClicksBtn = screen.getByRole('button', {
    name: 'Remove Clicks Foundation Bursary Fund from saved',
  });
  fireEvent.press(unsaveClicksBtn);

  await waitFor(() => {
    expect(unsaveSpy).toHaveBeenCalledWith('clicks_foundation');
  });
});

test('FunderDetailScreen (signed in): bookmark saves and unsaves the funder', async () => {
  mockSessionStatus = 'active';
  mockParams = { id: 'nsfas' };
  jest.spyOn(courseFinderApi, 'funder').mockResolvedValue(nsfasData);
  jest.spyOn(courseFinderApi, 'savedFundingList').mockResolvedValue({
    today: '2026-10-15',
    summary: '0 funding options: 0 open now.',
    counts: { total: 0, open_now: 0, closing_soon: 0 },
    funders: [],
    confirmed: false,
    notice: null,
  });
  const saveSpy = jest.spyOn(courseFinderApi, 'saveFunder').mockResolvedValue({
    ...nsfasData,
    saved_on: '2026-10-16',
  });
  const unsaveSpy = jest.spyOn(courseFinderApi, 'unsaveFunder').mockResolvedValue({} as Record<string, never>);

  render(<FunderDetailScreen />);

  await waitFor(() => {
    expect(screen.getByText('National Student Financial Aid Scheme (NSFAS)')).toBeTruthy();
  });

  const saveBtn = screen.getByRole('button', {
    name: 'Save National Student Financial Aid Scheme (NSFAS)',
  });
  fireEvent.press(saveBtn);

  await waitFor(() => {
    expect(saveSpy).toHaveBeenCalledWith('nsfas');
    expect(screen.getByText('Saved on Fri 16 Oct 2026')).toBeTruthy();
  });

  const unsaveBtn = screen.getByRole('button', {
    name: 'Remove National Student Financial Aid Scheme (NSFAS) from saved',
  });
  fireEvent.press(unsaveBtn);

  await waitFor(() => {
    expect(unsaveSpy).toHaveBeenCalledWith('nsfas');
  });
});

test('UpdatesScreen: tapping a funding reminder opens that funder detail screen', async () => {
  jest.spyOn(updatesApi, 'list').mockResolvedValue([
    {
      id: 'u1',
      kind: 'funding.closing',
      title: 'NSFAS closes in 7 days',
      body: 'Applications for 2027 close on Sat 31 Oct 2026.',
      icon: 'bell',
      link: { type: 'funding', id: 'nsfas' },
      created_at: '2026-10-15T08:00:00Z',
      read_at: null,
    },
  ]);
  jest.spyOn(updatesApi, 'switches').mockResolvedValue([
    {
      topic: 'funding_reminders',
      label: 'Funding you saved: when it opens, and before it closes',
      on: true,
    },
  ]);
  jest.spyOn(updatesApi, 'read').mockResolvedValue(undefined);

  render(<UpdatesScreen />);

  await waitFor(() => {
    expect(screen.getByText('NSFAS closes in 7 days')).toBeTruthy();
  });

  expect(screen.getByText('Funding you saved: when it opens, and before it closes')).toBeTruthy();

  fireEvent.press(screen.getByText('NSFAS closes in 7 days'));

  expect(mockPush).toHaveBeenCalledWith({
    pathname: '/course-finder/funding/[id]',
    params: { id: 'nsfas' },
  });
});

