/**
 * Task 1 tests:
 * - the footer shows Funding and not "Change goal"
 * - NSFAS opens its page
 * - a funder without covers shows "Not published by the funder"
 * - a funder whose covers name no amount shows the "doesn't publish an amount" line
 * - fee formatting (15000 is "R150", null is "No fee published")
 * - the list filters by field
 */
import { beforeEach, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';

import { courseFinderApi } from '../api/courseFinderApi';
import FunderDetailScreen from '../screens/FunderDetailScreen';
import FundingScreen from '../screens/FundingScreen';
import PlanScreen from '../screens/PlanScreen';
import { FunderDetail, FundingListAnswer, Plan } from '../types';
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

  // Initially shows other funders, including pharmacy-only Clicks Foundation
  expect(screen.getByText('Clicks Foundation Bursary Fund')).toBeTruthy();

  // Filter by Agriculture (which has Sasol Foundation)
  const agriChip = screen.getByText('Agriculture');
  fireEvent.press(agriChip);

  // Sasol Foundation is shown
  expect(screen.getByText('Sasol Foundation Bursary Programme')).toBeTruthy();
  // Clicks Foundation (pharmacy only) is NOT shown
  expect(screen.queryByText('Clicks Foundation Bursary Fund')).toBeNull();
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
