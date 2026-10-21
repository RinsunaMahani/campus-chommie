/**
 * Empty lists teach the next step: a title, what goes here, and (when no other button is in sight) the one button
 * that fills the list. Payments has no add button of its own, so its empty state sends the student to add income.
 */
import { expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';
import { router } from 'expo-router';

import { moneyApi } from '@/features/money/api/moneyApi';
import PaymentsScreen from '@/features/money/screens/PaymentsScreen';
import { EmptyState } from '@/shared/components/EmptyState';
import { t } from '@/shared/i18n';

jest.mock('expo-router', () => {
  const React = jest.requireActual<typeof import('react')>('react');
  return {
    router: { push: jest.fn(), back: jest.fn(), canGoBack: () => true, replace: jest.fn() },
    useLocalSearchParams: () => ({}),
    useFocusEffect: (cb: () => void) => React.useEffect(() => cb(), [cb]),
  };
});
jest.mock('react-native-safe-area-context', () => {
  const actual = jest.requireActual<object>('react-native-safe-area-context');
  return { ...actual, useSafeAreaInsets: () => ({ top: 0, left: 0, right: 0, bottom: 0 }) };
});
jest.mock('@expo/vector-icons', () => ({ Feather: () => null }));
jest.mock('@/features/profile/state', () => ({ useProfile: () => ({ demo: false, mock: false, profile: null }) }));

test('an empty state shows its title and line, and its one button does the next step', () => {
  const onPress = jest.fn();
  render(<EmptyState icon="credit-card" title="No cards yet" body="Add your store cards." action={{ label: 'Add a card', onPress }} />);
  expect(screen.getByText('No cards yet')).toBeTruthy();
  expect(screen.getByText('Add your store cards.')).toBeTruthy();
  fireEvent.press(screen.getByText('Add a card'));
  expect(onPress).toHaveBeenCalledTimes(1);
});

test('without an action there is no button', () => {
  render(<EmptyState icon="bell" title="No updates yet" body="You hear it here." />);
  expect(screen.queryByRole('button')).toBeNull();
});

test('no payments expected: the empty state sends the student to add income', async () => {
  jest.spyOn(moneyApi, 'payments').mockResolvedValue([]);
  render(<PaymentsScreen />);
  expect(await screen.findByText(t('money.paymentsEmptyTitle'))).toBeTruthy();
  fireEvent.press(screen.getByText(t('money.incomeAdd')));
  expect(router.push).toHaveBeenCalledWith('/money/income-edit');
});
