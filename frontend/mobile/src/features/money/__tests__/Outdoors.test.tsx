/**
 * Outdoors tab / Cheap things screen tests:
 * - renders fixture with all cards, details, hours, dates, and sources
 * - filter chips: All, Free, and only categories present in the response
 * - "Free" badge appears only when free is true
 * - empty state: "Nothing listed near your campus yet."
 */
import { beforeEach, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import { moneyApi } from '../api/moneyApi';
import CheapThingsScreen from '../screens/CheapThingsScreen';
import fixture from './fixtures/cheap_things.json';

jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));
jest.mock('react-native-safe-area-context', () => {
  const actual = jest.requireActual<object>('react-native-safe-area-context');
  return { ...actual, useSafeAreaInsets: () => ({ top: 0, left: 0, right: 0, bottom: 0 }) };
});
jest.mock('expo-router', () => ({
  router: { push: jest.fn(), back: jest.fn() },
  useFocusEffect: jest.fn(),
}));
jest.mock('expo-web-browser', () => ({ openBrowserAsync: jest.fn() }));
jest.mock('@/features/profile/state', () => ({
  useProfile: () => ({ mock: false, university: 'up', campus: 'hatfield' }),
}));

beforeEach(() => {
  jest.restoreAllMocks();
});

test('renders a fixture with cards, details, cost notes, hours, dates and source links', async () => {
  jest.spyOn(moneyApi, 'cheapThings').mockResolvedValue(fixture as never);

  render(<CheapThingsScreen />);

  // Title and subtitle
  expect(await screen.findByText('Cheap things nearby')).toBeTruthy();
  expect(screen.getByText('Places near your campus, each priced from its own page.')).toBeTruthy();

  // University and unconfirmed notice
  expect(screen.getByText('University of Pretoria · hatfield')).toBeTruthy();
  expect(screen.getByText('Not yet confirmed by the team.')).toBeTruthy();

  // All 3 places rendered
  expect(screen.getByText('Pretoria National Botanical Garden')).toBeTruthy();
  expect(screen.getByText('Freedom Park Grounds')).toBeTruthy();
  expect(screen.getByText('DITSONG National Museum of Natural History')).toBeTruthy();

  // Cost notes exactly as sent
  expect(
    screen.getByText('Students R50 in peak season (September to March); adults R100; children 6 to 17 R30; under 6 free.'),
  ).toBeTruthy();
  expect(screen.getByText('Free entry to the garden and sanctuary on public holidays.')).toBeTruthy();
  expect(screen.getByText('Adults R45, learners R25. No separate university student price.')).toBeTruthy();

  // Hours
  expect(screen.getByText('Hours: Every day, 08:00-18:00')).toBeTruthy();
  expect(screen.getByText('Hours: Every day, 08:00-16:30')).toBeTruthy();
  expect(screen.getByText('Hours: Daily 07:30-16:00')).toBeTruthy();

  // Price date formatted, and not verified when missing
  expect(screen.getByText('Price read on its page on Fri 9 Oct 2026')).toBeTruthy();
  expect(screen.getByText('Price read on its page on Sat 10 Oct 2026')).toBeTruthy();
  expect(screen.getByText('Not verified yet')).toBeTruthy();

  // Source links
  expect(screen.getByText('Source: sanbi.org')).toBeTruthy();
  expect(screen.getByText('Source: freedompark.co.za')).toBeTruthy();
  expect(screen.getByText('Source: ditsong.org.za')).toBeTruthy();
});

test('filter chips: All, Free, and only categories present in the response', async () => {
  jest.spyOn(moneyApi, 'cheapThings').mockResolvedValue(fixture as never);

  render(<CheapThingsScreen />);

  expect(await screen.findByText('Cheap things nearby')).toBeTruthy();

  // Filter chips present as buttons: "All", "Free", and present categories: "Outdoors", "Heritage", "Museum"
  expect(screen.getByRole('button', { name: 'All' })).toBeTruthy();
  expect(screen.getByRole('button', { name: 'Free' })).toBeTruthy();
  expect(screen.getByRole('button', { name: 'Outdoors' })).toBeTruthy();
  expect(screen.getByRole('button', { name: 'Heritage' })).toBeTruthy();
  expect(screen.getByRole('button', { name: 'Museum' })).toBeTruthy();

  // Unrepresented category (e.g. Sport) is NOT present as a chip
  expect(screen.queryByRole('button', { name: 'Sport' })).toBeNull();

  // Tap "Free" filter chip: only Freedom Park Grounds (free: true) remains
  fireEvent.press(screen.getByRole('button', { name: 'Free' }));
  expect(screen.getByText('Freedom Park Grounds')).toBeTruthy();
  expect(screen.queryByText('Pretoria National Botanical Garden')).toBeNull();
  expect(screen.queryByText('DITSONG National Museum of Natural History')).toBeNull();

  // Tap "Museum" filter chip: only DITSONG remains
  fireEvent.press(screen.getByRole('button', { name: 'Museum' }));
  expect(screen.getByText('DITSONG National Museum of Natural History')).toBeTruthy();
  expect(screen.queryByText('Pretoria National Botanical Garden')).toBeNull();
  expect(screen.queryByText('Freedom Park Grounds')).toBeNull();

  // Tap "All" filter chip: all 3 return
  fireEvent.press(screen.getByRole('button', { name: 'All' }));
  expect(screen.getByText('Pretoria National Botanical Garden')).toBeTruthy();
  expect(screen.getByText('Freedom Park Grounds')).toBeTruthy();
  expect(screen.getByText('DITSONG National Museum of Natural History')).toBeTruthy();
});

test('"Free" badge appears only when free is true', async () => {
  jest.spyOn(moneyApi, 'cheapThings').mockResolvedValue(fixture as never);

  render(<CheapThingsScreen />);

  expect(await screen.findByText('Cheap things nearby')).toBeTruthy();

  // The "Free" filter chip exists, but as a badge/tag on cards:
  // There is only 1 place with free: true, so "Free" as text appears once in the filter chip
  // and once as the card badge.
  const freeElements = screen.getAllByText('Free');
  // 1 for filter chip, 1 for Freedom Park Grounds card tag
  expect(freeElements).toHaveLength(2);

  // When filtered to Outdoors (which has free: false), "Free" appears only once (the filter chip)
  fireEvent.press(screen.getByRole('button', { name: 'Outdoors' }));
  expect(screen.getByText('Pretoria National Botanical Garden')).toBeTruthy();
  expect(screen.getAllByText('Free')).toHaveLength(1);
});

test('empty state: "Nothing listed near your campus yet."', async () => {
  jest.spyOn(moneyApi, 'cheapThings').mockResolvedValue({
    university: { id: 'up', name: 'University of Pretoria', confirmed: true },
    campus: 'gibs',
    cheap_things: [],
    lines: ['Nothing listed near your campus yet.'],
  } as never);

  render(<CheapThingsScreen />);

  expect(await screen.findByText('Nothing listed near your campus yet.')).toBeTruthy();
  // No places listed
  expect(screen.queryByText('Pretoria National Botanical Garden')).toBeNull();
});
