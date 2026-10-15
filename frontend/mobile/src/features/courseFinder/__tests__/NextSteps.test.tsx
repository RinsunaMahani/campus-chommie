/**
 * Task 2 tests:
 * - The plan shows the "If you're accepted" card
 * - Next-steps screen lists step titles and labels from recorded fixture firstSteps.json
 * - Empty first_steps shows "Not published yet"
 * - Create account button navigates with university and no marks
 * - Onboarding (CampusScreen) preselects a listed university from parameter and ignores an unknown one
 */
import { beforeEach, describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';

import { profileApi } from '@/features/profile/api/profileApi';
import CampusScreen from '@/features/profile/screens/CampusScreen';
import { t } from '@/shared/i18n';

import { courseFinderApi } from '../api/courseFinderApi';
import NextStepsScreen from '../screens/NextStepsScreen';
import PlanScreen from '../screens/PlanScreen';
import { FirstStepsAnswer, Plan } from '../types';
import firstStepsFixture from './fixtures/firstSteps.json';
import planFixture from './fixtures/plan.json';

const mockPush = jest.fn();
const mockBack = jest.fn();
const mockDismissTo = jest.fn();
let mockParams: Record<string, string> = { id: 'up' };

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
    SafeAreaView: ({ children }: { children: unknown }) => children,
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

const mockSetProfile = jest.fn();
jest.mock('@/features/profile/state', () => ({
  useProfile: () => ({
    loading: false,
    profile: null,
    demo: false,
    mock: false,
    needsOnboarding: true,
    setProfile: mockSetProfile,
  }),
}));

const firstStepsData = (firstStepsFixture as unknown as { data: FirstStepsAnswer }).data;

beforeEach(() => {
  jest.clearAllMocks();
  mockParams = { id: 'up' };
  mockCourseFinderState = {
    plan: mockPlan,
    university: { id: 'smu', name: 'Sefako Makgatho Health Sciences University' },
    reset: mockReset,
  };
});

describe('Task 2: Accepted step & onboarding handoff', () => {
  test('the plan shows the "If you\'re accepted" card and navigates to next steps', () => {
    render(<PlanScreen />);

    expect(
      screen.getByText(
        t('courseFinder.acceptedCardTitle', { university: 'Sefako Makgatho Health Sciences University' }),
      ),
    ).toBeTruthy();
    expect(screen.getByText(t('courseFinder.acceptedCardSub'))).toBeTruthy();

    const button = screen.getByText(t('courseFinder.seeWhatHappensNext'));
    expect(button).toBeTruthy();
    fireEvent.press(button);

    expect(mockPush).toHaveBeenCalledWith('/course-finder/next/smu');
  });

  test('next-steps screen lists step titles and labels from recorded fixture', async () => {
    jest.spyOn(courseFinderApi, 'firstSteps').mockResolvedValue(firstStepsData);

    render(<NextStepsScreen />);

    await waitFor(() => {
      expect(
        screen.getByText(t('courseFinder.nextStepsTitle', { university: 'University of Pretoria' })),
      ).toBeTruthy();
    });

    // Check step titles and labels from fixture
    expect(screen.getByText('Accept your offer')).toBeTruthy();
    expect(screen.getByText('Not verified yet')).toBeTruthy();

    expect(screen.getByText('Register')).toBeTruthy();
    expect(screen.getAllByText('Coming up').length).toBeGreaterThanOrEqual(1);

    expect(screen.getByText('Orientation')).toBeTruthy();
    expect(screen.getByText('First lecture')).toBeTruthy();

    // Check dates and lines
    expect(screen.getByText('Fri 19 Feb 2027')).toBeTruthy();
    expect(screen.getByText(t('courseFinder.nextStepsSupportMoney'))).toBeTruthy();
  });

  test('empty first_steps shows "Not published yet"', async () => {
    jest.spyOn(courseFinderApi, 'firstSteps').mockResolvedValue({
      ...firstStepsData,
      first_steps: [],
    });

    render(<NextStepsScreen />);

    await waitFor(() => {
      expect(screen.getByText(t('courseFinder.nextStepsNotPublished'))).toBeTruthy();
    });

    expect(screen.getByText('University of Pretoria')).toBeTruthy();
  });

  test('create account button navigates with university and no marks', async () => {
    jest.spyOn(courseFinderApi, 'firstSteps').mockResolvedValue(firstStepsData);
    mockParams = { id: 'up' };

    render(<NextStepsScreen />);

    await waitFor(() => {
      expect(screen.getByText(t('courseFinder.createStudentAccount'))).toBeTruthy();
    });

    const createBtn = screen.getByText(t('courseFinder.createStudentAccount'));
    fireEvent.press(createBtn);

    expect(mockPush).toHaveBeenCalledWith({
      pathname: '/(auth)/create-account',
      params: { university: 'up' },
    });

    // Verify no marks or learner data were passed
    const callArgs = mockPush.mock.calls[0][0] as { pathname: string; params: Record<string, unknown> };
    expect(callArgs.params).toEqual({ university: 'up' });
    expect(callArgs.params).not.toHaveProperty('marks');
  });

  test('onboarding (CampusScreen) preselects a listed university from parameter and ignores an unknown one', async () => {
    const unis = [
      { id: 'up', name: 'University of Pretoria' },
      { id: 'smu', name: 'Sefako Makgatho Health Sciences University' },
    ];
    const campusesSpy = jest.spyOn(profileApi, 'campuses').mockResolvedValue([
      { id: 'hatfield', name: 'Hatfield Campus' },
    ]);
    jest.spyOn(profileApi, 'universities').mockResolvedValue(unis);

    // Case 1: Known university preselected
    mockParams = { university: 'up' };
    const { unmount } = render(<CampusScreen />);

    await waitFor(() => {
      expect(campusesSpy).toHaveBeenCalledWith('up');
      expect(screen.getByText('University of Pretoria')).toBeTruthy();
    });

    unmount();
    campusesSpy.mockClear();

    // Case 2: Unknown university ignored
    mockParams = { university: 'hogwarts' };
    render(<CampusScreen />);

    await waitFor(() => {
      expect(screen.getByText(t('onboarding.pickUniversity'))).toBeTruthy();
    });
    expect(campusesSpy).not.toHaveBeenCalledWith('hogwarts');
  });
});
