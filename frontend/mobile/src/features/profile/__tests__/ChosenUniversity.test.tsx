/**
 * The real path from the course finder to onboarding: sign-up and email
 * verification don't pass the university on, so the course finder remembers
 * it in memory and onboarding preselects it, once, with no route parameter.
 */
import { expect, jest, test } from '@jest/globals';
import { render, screen, waitFor } from '@testing-library/react-native';

import { profileApi } from '@/features/profile/api/profileApi';
import CampusScreen from '@/features/profile/screens/CampusScreen';
import { t } from '@/shared/i18n';
import { rememberUniversity, takeUniversity } from '@/shared/lib/chosenUniversity';

jest.mock('expo-router', () => ({
  router: { push: jest.fn(), back: jest.fn(), replace: jest.fn() },
  Redirect: () => null,
  useLocalSearchParams: () => ({}),
}));
jest.mock('react-native-safe-area-context', () => {
  const actual = jest.requireActual<object>('react-native-safe-area-context');
  return {
    ...actual,
    useSafeAreaInsets: () => ({ top: 0, left: 0, right: 0, bottom: 0 }),
    SafeAreaView: ({ children }: { children: unknown }) => children,
  };
});
jest.mock('@/features/profile/state', () => ({
  useProfile: () => ({ loading: false, profile: null, demo: false, mock: false, needsOnboarding: true, setProfile: jest.fn() }),
}));
jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));
jest.mock('@/shared/motion/motion', () => ({ ...jest.requireActual<object>('@/shared/motion/motion'), motionOff: () => true }));

test('a remembered university is read once', () => {
  rememberUniversity('smu');
  expect(takeUniversity()).toBe('smu');
  expect(takeUniversity()).toBeNull();
});

test('onboarding preselects the university remembered before sign-up, with no route parameter', async () => {
  jest.spyOn(profileApi, 'universities').mockResolvedValue([
    { id: 'up', name: 'University of Pretoria' },
    { id: 'smu', name: 'Sefako Makgatho Health Sciences University' },
  ]);
  const campuses = jest.spyOn(profileApi, 'campuses').mockResolvedValue([{ id: 'ga-rankuwa', name: 'Ga-Rankuwa' }]);

  rememberUniversity('smu');
  const { unmount } = render(<CampusScreen />);
  await waitFor(() => expect(campuses).toHaveBeenCalledWith('smu'), { timeout: 10000 });
  unmount();

  // Read once: opening onboarding again starts with no choice.
  campuses.mockClear();
  render(<CampusScreen />);
  await waitFor(() => expect(screen.getByText(t('onboarding.pickUniversity'))).toBeTruthy(), { timeout: 10000 });
  expect(campuses).not.toHaveBeenCalled();
});
