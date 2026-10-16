/**
 * Campus map screen tests (#22):
 * - Campus picker from `campuses`; one not mapped yet shows its line.
 * - Draws `outline` and each place's `outline` (or a pin when it has none).
 * - Labels the named ones; unnamed stay plain shapes, never guessed.
 * - A tap shows the place's name, or "No name yet".
 * - Shows `attribution` linked to `attribution_url` and `licence` linked to `licence_url`.
 * - While `confirmed` is false, shows `notice`.
 * - Each `support` entry's `place` lets the Support screen offer "Show on map".
 */
import { beforeEach, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import * as WebBrowser from 'expo-web-browser';

import { SupportSections } from '@/features/support/components/SupportSections';
import { SupportKind } from '@/features/support/types';

import { courseFinderApi } from '../api/courseFinderApi';
import CampusMapScreen from '../screens/CampusMapScreen';
import { UniversityMapAnswer } from '../types';
import mapFixture from './fixtures/universityMap.json';

const mockPush = jest.fn();
const mockBack = jest.fn();
let mockParams: Record<string, string | undefined> = { id: 'up' };

jest.mock('expo-router', () => ({
  router: {
    push: (...args: unknown[]) => mockPush(...args),
    back: (...args: unknown[]) => mockBack(...args),
  },
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

const mapData = (mapFixture as unknown as { data: UniversityMapAnswer }).data;

beforeEach(() => {
  jest.clearAllMocks();
  mockParams = { id: 'up' };
});

test('CampusMapScreen renders mapped campus, named places, attribution, ODbL licence and unconfirmed notice', async () => {
  jest.spyOn(courseFinderApi, 'universityMap').mockResolvedValue(mapData);

  render(<CampusMapScreen />);

  await waitFor(() => {
    expect(screen.getByText('University of Pretoria')).toBeTruthy();
  });

  // Unconfirmed notice
  expect(screen.getByText('Not yet confirmed by the team.')).toBeTruthy();

  // Campus summary lines
  expect(screen.getByText('4 buildings and places from OpenStreetMap, 3 with a name.')).toBeTruthy();
  expect(
    screen.getByText('Buildings without a name show as shapes only: we never guess what they are.'),
  ).toBeTruthy();

  // Named places are listed
  expect(screen.getAllByText('Merensky Library').length).toBeGreaterThan(0);
  expect(screen.getAllByText('Student Health services').length).toBeGreaterThan(0);
  expect(screen.getAllByText('Artisan Coffee').length).toBeGreaterThan(0);

  // Attribution and licence links
  const attrLink = screen.getByLabelText('© OpenStreetMap contributors');
  fireEvent.press(attrLink);
  expect(WebBrowser.openBrowserAsync).toHaveBeenCalledWith('https://www.openstreetmap.org/copyright');

  const licenceLink = screen.getByLabelText('Open Database License (ODbL) 1.0');
  fireEvent.press(licenceLink);
  expect(WebBrowser.openBrowserAsync).toHaveBeenCalledWith(
    'https://opendatacommons.org/licenses/odbl/1-0/',
  );
});

test('CampusMapScreen: tapping a named place shows its name and support service; tapping an unnamed place shows "No name yet"', async () => {
  jest.spyOn(courseFinderApi, 'universityMap').mockResolvedValue(mapData);

  render(<CampusMapScreen />);

  await waitFor(() => {
    expect(screen.getByText('University of Pretoria')).toBeTruthy();
  });

  // Tap named place "Student Health services"
  fireEvent.press(screen.getByLabelText('Student Health services'));
  expect(screen.getByText('Student Health Services clinic')).toBeTruthy();

  // Tap unnamed building shape on SVG map (testID map-place-w1116385700)
  fireEvent.press(screen.getByTestId('map-place-w1116385700'));
  expect(screen.getAllByText('No name yet').length).toBeGreaterThan(0);
});

test('CampusMapScreen: switching to an unmapped campus shows its plain-words line', async () => {
  jest.spyOn(courseFinderApi, 'universityMap').mockResolvedValue(mapData);

  render(<CampusMapScreen />);

  await waitFor(() => {
    expect(screen.getByText('University of Pretoria')).toBeTruthy();
  });

  // Switch campus picker to Groenkloof campus
  fireEvent.press(screen.getByLabelText('Groenkloof campus'));

  expect(screen.getByText("Groenkloof campus isn't mapped yet.")).toBeTruthy();
});

test('SupportSections offers "Show on map" when a support service has a place on the map', () => {
  const kinds: SupportKind[] = [
    {
      kind: 'health',
      line: null,
      services: [
        {
          name: 'Student Health Services clinic',
          contact: 'Student Health services building, Hatfield',
          hours: '08:00 to 16:00',
          note: null,
          source_url: 'https://www.up.ac.za/health',
          read_on: '2026-10-09',
          last_verified: null,
        },
      ],
    },
  ];
  const onShowOnMap = jest.fn();

  render(
    <SupportSections
      kinds={kinds}
      placeByService={{ 'Student Health Services clinic': 'w484352680' }}
      onShowOnMap={onShowOnMap}
    />,
  );

  const showBtn = screen.getByRole('button', { name: 'Show on map' });
  expect(showBtn).toBeTruthy();
  fireEvent.press(showBtn);
  expect(onShowOnMap).toHaveBeenCalledWith('w484352680');
});
