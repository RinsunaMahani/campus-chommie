/**
 * Outdoors from the centre button: the sheet lists the places near campus, filters by kind, previews one (cost,
 * hours, where) and hands its public address to the phone's maps app, never guessing one; Close puts it away.
 */
import { beforeEach, expect, jest, test } from '@jest/globals';
import { act, fireEvent, render, screen } from '@testing-library/react-native';
import { router } from 'expo-router';
import { Linking } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { moneyApi } from '@/features/money/api/moneyApi';
import { CheapThing } from '@/features/money/types';

import { MAX_PHOTOS, PlacePhoto, placeKey } from '../placePhotos';
import { mapsUrl } from '../places';
import OutdoorsSheet from '../screens/OutdoorsSheet';

// The real rule, not the stand-in below.
const { photosFor } = jest.requireActual<typeof import('../placePhotos')>('../placePhotos');

const wrap = (ui: React.ReactElement) =>
  render(
    <SafeAreaProvider
      initialMetrics={{ insets: { top: 0, left: 0, right: 0, bottom: 0 }, frame: { x: 0, y: 0, width: 360, height: 800 } }}>
      {ui}
    </SafeAreaProvider>,
  );

jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));
jest.mock('expo-web-browser', () => ({ openBrowserAsync: jest.fn() }));
// A stand-in photo list (no real images in tests): Freedom Park has four photos, Voortrekker Monument only two.
const photo = (n: number) => ({ image: { uri: `https://example.test/${n}.jpg` }, caption: `View ${n}`, credit: `Author ${n}, CC BY 4.0`,
  source: `https://commons.wikimedia.org/wiki/File:${n}.jpg` });
jest.mock('../placePhotos', () => {
  const actual = jest.requireActual<typeof import('../placePhotos')>('../placePhotos');
  const list = { 'freedom-park': [1, 2, 3, 4].map(photo), 'voortrekker-monument': [1, 2].map(photo) };
  return { ...actual, PLACE_PHOTOS: list, photosFor: (name: string) => actual.photosFor(name, list) };
});
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


// ---------------------------------------------------------------- the slideshow


const ONE = { image: { uri: 'x' }, caption: 'c', credit: 'a', source: 's' } as PlacePhoto;

test('a slideshow needs at least 3 photos and shows at most 5', () => {
  const many = { garden: Array.from({ length: 7 }, (_, i) => ({ ...ONE, source: `s${i}` })), two: [ONE, ONE] };
  expect(photosFor('Garden', many)).toHaveLength(MAX_PHOTOS);
  expect(photosFor('Two', many)).toEqual([]);
  expect(placeKey('Wonderboom Nature Reserve: a fig tree over 1 000 years old')).toBe('wonderboom-nature-reserve');
  expect(placeKey('DITSONG: Tswaing Meteorite Crater')).toBe('ditsong-tswaing-meteorite-crater');
});

test('a place with enough photos opens on a slideshow that moves on by itself, with each credit', async () => {
  jest.useFakeTimers();
  try {
    wrap(<OutdoorsSheet />);
    await act(async () => {
      await Promise.resolve();
    });
    fireEvent.press(screen.getByText('Freedom Park'));
    fireEvent(screen.getByTestId('slideshow-frame'), 'layout', { nativeEvent: { layout: { width: 320, height: 180 } } });
    expect(screen.getByText('1 / 4', { includeHiddenElements: true })).toBeTruthy();
    expect(screen.getByText('View 1')).toBeTruthy();
    expect(screen.queryByText('Photo: Author 1, CC BY 4.0')).toBeNull(); // credits are on the Photo credits page
    expect(screen.getByLabelText('Photo 1 of 4: View 1')).toBeTruthy();
    act(() => {
      jest.advanceTimersByTime(4000);
    });
    expect(screen.getByText('2 / 4', { includeHiddenElements: true })).toBeTruthy();
    expect(screen.getByText('View 2')).toBeTruthy();

    // Once the student swipes, it stays where they put it.
    fireEvent(screen.getByLabelText('Photos of Freedom Park'), 'scrollBeginDrag');
    act(() => {
      jest.advanceTimersByTime(12000);
    });
    expect(screen.getByText('2 / 4', { includeHiddenElements: true })).toBeTruthy();
  } finally {
    jest.useRealTimers();
  }
});

test('a place with fewer than 3 photos keeps its icon, never a short slideshow', async () => {
  const monument: CheapThing = { name: 'Voortrekker Monument', category: 'heritage', cost_note: 'Students R60', address: 'Eeufees Road, Pretoria',
    hours: null, source_url: null, read_on: null, last_verified: null };
  jest.spyOn(moneyApi, 'cheapThings').mockResolvedValue({ cheap_things: [...PLACES, monument], lines: [] } as never);
  wrap(<OutdoorsSheet />);
  fireEvent.press(await screen.findByText('Voortrekker Monument'));
  expect(screen.getByText('Eeufees Road, Pretoria')).toBeTruthy();
  expect(screen.queryByLabelText('Photos of Voortrekker Monument')).toBeNull();
  expect(screen.queryByText(/ \/ /)).toBeNull();
});
