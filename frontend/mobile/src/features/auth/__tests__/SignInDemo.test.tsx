/**
 * The demo-student buttons on sign-in fill in the email only: the password
 * is never in the app (anything in the app ships inside the APK).
 */
import { expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import SignIn from '../screens/SignInScreen';

jest.mock('expo-router', () => ({ router: { push: jest.fn(), replace: jest.fn() } }));
jest.mock('react-native-safe-area-context', () => {
  const actual = jest.requireActual<object>('react-native-safe-area-context');
  return {
    ...actual,
    useSafeAreaInsets: () => ({ top: 0, left: 0, right: 0, bottom: 0 }),
    SafeAreaView: ({ children }: { children: unknown }) => children,
  };
});
jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));
jest.mock('@/features/auth/session/SessionProvider', () => ({
  useSession: () => ({ signedIn: jest.fn(), startEmailSignUp: jest.fn() }),
}));

test('a demo student fills in the email and never the password', () => {
  render(<SignIn />);
  fireEvent.press(screen.getByLabelText("Fill in Naledi's demo email: short money, heavy week"));
  expect(screen.getByDisplayValue('naledi.demo@example.com')).toBeTruthy();
  // The password field stays empty: nothing but the email is filled.
  expect(screen.queryAllByDisplayValue(/.+/)).toHaveLength(1);
  expect(screen.getByText("Then type the demo password from the judges' notes.")).toBeTruthy();
});
