/**
 * Account security's "Where you're signed in": this phone first, then the most recently used, four in all; the
 * rest one tap away ("Show N more"), so a long list of old sign-ins doesn't bury the rest of the screen.
 */
import { expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import { securityApi, SignedInPhone } from '../api/securityApi';
import SecurityScreen, { phoneOrder } from '../screens/SecurityScreen';

jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));
jest.mock('expo-router', () => ({
  router: { push: jest.fn(), back: jest.fn(), canGoBack: () => true },
  useFocusEffect: (cb: () => void) => {
    const React = jest.requireActual<typeof import('react')>('react');
    React.useEffect(() => {
      cb();
    }, [cb]);
  },
}));
jest.mock('react-native-safe-area-context', () => {
  const actual = jest.requireActual<object>('react-native-safe-area-context');
  return { ...actual, useSafeAreaInsets: () => ({ top: 0, left: 0, right: 0, bottom: 0 }) };
});

let mockDemo = false;
jest.mock('@/features/profile/state', () => ({
  useProfile: () => ({ demo: mockDemo, mock: false, profile: null }),
}));

const phone = (n: number, extra: Partial<SignedInPhone> = {}): SignedInPhone => ({
  id: `p${n}`,
  this_phone: false,
  signed_in_at: '2026-10-01T08:00:00Z',
  last_used_at: `2026-10-${String(10 + n).padStart(2, '0')}T08:00:00Z`,
  platform: 'android',
  label: `Phone ${n}`,
  ...extra,
});

test('this phone comes first, then the most recently used', () => {
  const order = phoneOrder([phone(1), phone(5), phone(2, { this_phone: true }), phone(9)]).map((p) => p.id);
  expect(order).toEqual(['p2', 'p9', 'p5', 'p1']);
});

test('four phones show, the rest behind "Show N more", and it folds back', async () => {
  const phones = [phone(1), phone(2), phone(3, { this_phone: true }), phone(4), phone(5), phone(6), phone(7)];
  jest.spyOn(securityApi, 'phones').mockResolvedValue(phones);
  render(<SecurityScreen />);

  expect(await screen.findByText('Phone 3')).toBeTruthy();
  expect(screen.getByText('This phone')).toBeTruthy();
  for (const n of [7, 6, 5]) expect(screen.getByText(`Phone ${n}`)).toBeTruthy();
  for (const n of [4, 2, 1]) expect(screen.queryByText(`Phone ${n}`)).toBeNull();

  fireEvent.press(screen.getByText('Show 3 more'));
  for (const n of [4, 2, 1]) expect(screen.getByText(`Phone ${n}`)).toBeTruthy();
  fireEvent.press(screen.getByText('Show fewer'));
  expect(screen.queryByText('Phone 1')).toBeNull();
});

test('shows the demo banner on a demo account and omits it on a normal account', async () => {
  jest.spyOn(securityApi, 'phones').mockResolvedValue([]);

  mockDemo = true;
  const { unmount } = render(<SecurityScreen />);
  expect(screen.getByText('Demo data: fictional student')).toBeTruthy();
  await screen.findByText("Where you're signed in");
  unmount();

  mockDemo = false;
  render(<SecurityScreen />);
  expect(screen.queryByText('Demo data: fictional student')).toBeNull();
  await screen.findByText("Where you're signed in");
});
