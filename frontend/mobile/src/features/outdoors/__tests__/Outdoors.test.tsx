/**
 * Outdoors from the centre button: the sheet lists the places near campus, filters by kind, previews one (cost,
 * hours, where) and hands its public address to the phone's maps app, never guessing one; Close puts it away.
 */
import { beforeEach, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';
import { router } from 'expo-router';
import { Linking } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { moneyApi } from '@/features/money/api/moneyApi';
import { CheapThing } from '@/features/money/types';

import { mapsUrl } from '../places';
import OutdoorsSheet from '../screens/OutdoorsSheet';

const wrap = (ui: React.ReactElement) =>
  render(
    <SafeAreaProvider
      initialMetrics={{ insets: { top: 0, left: 0, right: 0, bottom: 0 }, frame: { x: 0, y: 0, width: 360, height: 800 } }}>
      {ui}
    </SafeAreaProvider>,
  );

jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));
jest.mock('expo-web-browser', () => ({ openBrowserAsync: jest.fn() }));
jest.mock('expo-router', () => ({
  router: { push: jest.fn(), back: jest.fn(), replace: jest.fn(), canGoBack: () => true },
}));

const PLACES: CheapThing[] = [
  { name: 'Freedom Park', category: 'heritage', cost_note: 'Students R60', address: 'Corner Koch and 7th Avenue, Salvokop, Pretoria',
    hours: 'Every day, 08:00–16:30', source_url: 'https://www.freedompark.co.za/', read_on: '2026-10-10', last_verified: null },
  { name: 'Pretoria National Botanical Garden', category: 'outdoors', cost_note: 'Students R50', address: null, hours: null,
    source_url: null, read_on: null, last_verified: null },
];

beforeEach(() => {
  jest.restoreAllMocks();
  jest.spyOn(moneyApi, 'cheapThings').mockResolvedValue({ cheap_things: PLACES, lines: [] } as never);
  (router.back as jest.Mock).mockClear();
  (router.replace as jest.Mock).mockClear();
});

test('the sheet lists the places near campus and filters by kind', async () => {
  wrap(<OutdoorsSheet />);
  expect(await screen.findByText('Freedom Park')).toBeTruthy();
  expect(screen.getByText('Pretoria National Botanical Garden')).toBeTruthy();
  fireEvent.press(screen.getByText('Heritage'));
  expect(screen.queryByText('Pretoria National Botanical Garden')).toBeNull();
  fireEvent.press(screen.getByText('See all places'));
  expect(router.replace).toHaveBeenCalledWith('/money/cheap-things');
});

test('a place previews what it costs, when it opens and where, and opens in maps', async () => {
  const open = jest.spyOn(Linking, 'openURL').mockResolvedValue(true);
  wrap(<OutdoorsSheet />);
  fireEvent.press(await screen.findByText('Freedom Park'));
  expect(screen.getByText('Students R60')).toBeTruthy();
  expect(screen.getByText('Every day, 08:00–16:30')).toBeTruthy();
  expect(screen.getByText('Corner Koch and 7th Avenue, Salvokop, Pretoria')).toBeTruthy();
  fireEvent.press(screen.getByText('Open in maps'));
  expect(open).toHaveBeenCalledWith(mapsUrl(PLACES[0]));
  fireEvent.press(screen.getByLabelText('Back to places'));
  expect(screen.getByText('Pretoria National Botanical Garden')).toBeTruthy();
});

test('a place without an address says so and offers no maps button', async () => {
  wrap(<OutdoorsSheet />);
  fireEvent.press(await screen.findByText('Pretoria National Botanical Garden'));
  expect(screen.getByText('No address published yet')).toBeTruthy();
  expect(screen.getByText('Hours not published: check before you go')).toBeTruthy();
  expect(screen.queryByText('Open in maps')).toBeNull();
});

test('Close puts the sheet away', async () => {
  wrap(<OutdoorsSheet />);
  await screen.findByText('Freedom Park');
  fireEvent.press(screen.getAllByLabelText('Close')[0]);
  // Without reduced motion the sheet slides down first, then goes back.
  await new Promise((r) => setTimeout(r, 400));
  expect(router.back).toHaveBeenCalled();
});

test('maps links carry only the place, in the right app for each phone', () => {
  const place = { name: 'Freedom Park', address: 'Corner Koch and 7th Avenue, Pretoria' };
  const q = encodeURIComponent('Freedom Park, Corner Koch and 7th Avenue, Pretoria');
  expect(mapsUrl(place, 'android')).toBe(`geo:0,0?q=${q}`);
  expect(mapsUrl(place, 'ios')).toBe(`maps:?q=${q}`);
  expect(mapsUrl(place, 'web')).toBe(`https://www.openstreetmap.org/search?query=${q}`);
  expect(mapsUrl({ name: 'Somewhere', address: null }, 'android')).toBeNull();
});
