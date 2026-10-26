/**
 * Campus and faculty photos: every one is credited and links to its Commons
 * page; the campus card shows what the photo is and opens that page; a
 * university without a photo shows nothing (its monogram stays in the lists).
 * A page opening on a photo shows what it is and its credit on it, opening the
 * Commons page; without a photo it opens on the wallpaper band, with no credit.
 */
import { expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';
import { Linking, Text } from 'react-native';

import { PhotoHero } from '@/shared/components/PhotoHero';

import PhotoCreditsScreen, { photoCredits } from '@/features/legal/screens/PhotoCreditsScreen';
import { CAMPUS_PHOTOS } from '../campusPhotos';
import { CampusPhotoCard } from '../components/CampusPhotoCard';
import { PHOTOS } from '../facultyPhotos';
import { funderMonogram, funderPhoto } from '../funderPhotos';

jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));
jest.mock('expo-router', () => ({ router: { back: jest.fn(), canGoBack: () => true, replace: jest.fn() } }));
jest.mock('react-native-safe-area-context', () => {
  const actual = jest.requireActual<object>('react-native-safe-area-context');
  return { ...actual, useSafeAreaInsets: () => ({ top: 0, left: 0, right: 0, bottom: 0 }) };
});

const COMMONS = /^https:\/\/commons\.wikimedia\.org\/wiki\/File:/;
const LICENCE = /, (CC0|Public domain|CC BY(-SA)? \d\.\d), Wikimedia Commons \(cropped\)$/;

test('every photo names its author and licence and links its Commons page', () => {
  const all = [...Object.values(CAMPUS_PHOTOS), ...Object.values(PHOTOS)];
  expect(all).toHaveLength(37);
  for (const p of all) {
    expect(p!.credit).toMatch(LICENCE);
    expect(p!.source).toMatch(COMMONS);
  }
});

test('SMU, with no logo-free photo on Commons, keeps its monogram; the other 25 have one', () => {
  expect(CAMPUS_PHOTOS.smu).toBeUndefined();
  expect(Object.keys(CAMPUS_PHOTOS)).toHaveLength(25);
});

test('the campus card shows what the photo is, with no credit under it (credits are on the Photo credits page)', () => {
  render(<CampusPhotoCard university="up" />);
  expect(screen.getByText('The Old Arts Building, Hatfield campus, at dusk')).toBeTruthy();
  expect(screen.queryByText('Photo: Sian Tiley-Nel, CC BY-SA 4.0, Wikimedia Commons (cropped)')).toBeNull();
});

test('the Photo credits page lists every campus photo with its credit, opening its Commons page', () => {
  const open = jest.spyOn(Linking, 'openURL').mockResolvedValue(true);
  render(<PhotoCreditsScreen />);
  const credits = photoCredits().flatMap((s) => s.items);
  expect(credits.length).toBeGreaterThanOrEqual(Object.keys(CAMPUS_PHOTOS).length);
  fireEvent.press(screen.getByText('UP: The Old Arts Building, Hatfield campus, at dusk'));
  expect(open).toHaveBeenCalledWith(CAMPUS_PHOTOS.up!.source);
});

test('a page opening on a photo says what it shows, with no credit on the photo', () => {
  const onSave = jest.fn();
  render(
    <PhotoHero
      photo={CAMPUS_PHOTOS.up}
      action={{ icon: 'bookmark', label: 'Save this', on: false, onPress: onSave }}
      head={<Text>University of Pretoria</Text>}>
      <Text>Body</Text>
    </PhotoHero>,
  );
  expect(screen.getByLabelText('The Old Arts Building, Hatfield campus, at dusk')).toBeTruthy();
  expect(screen.queryByText(/Photo: Sian Tiley-Nel/)).toBeNull();
  fireEvent.press(screen.getByRole('button', { name: 'Save this' }));
  expect(onSave).toHaveBeenCalled();
  expect(screen.getByRole('button', { name: 'Back' })).toBeTruthy();
});

test('a page without a photo has no credit to show', () => {
  render(
    <PhotoHero photo={undefined} head={<Text>Sefako Makgatho Health Sciences University</Text>}>
      <Text>Body</Text>
    </PhotoHero>,
  );
  expect(screen.getByText('Sefako Makgatho Health Sciences University')).toBeTruthy();
  expect(screen.queryByText(/Photo:/)).toBeNull();
});

test('a university without a photo shows no card', () => {
  render(<CampusPhotoCard university="smu" />);
  expect(screen.toJSON()).toBeNull();
});

test("a funder's picture is its field's photo, none for any field, never a logo", () => {
  expect(funderPhoto({ any_field: false, fields: [{ id: 'engineering' }, { id: 'built_environment' }, { id: 'commerce' }] })).toBe(
    PHOTOS.engineering,
  );
  expect(funderPhoto({ any_field: true, fields: [] })).toBeNull();
  expect(funderPhoto({ fields: [{ id: 'no_such_field' }] })).toBeNull();
});

test("a funder's tile shows letters from its own names, never a logo", () => {
  const tile = (name: string, short_name: string | null) => funderMonogram({ name, short_name });
  expect(tile('National Student Financial Aid Scheme (NSFAS)', 'NSFAS')).toBe('NSFAS');
  expect(tile('NSFAS loan scheme for the missing middle', 'NSFAS loans')).toBe('NSFAS');
  expect(tile('Thuthuka Bursary Fund (SAICA)', 'Thuthuka')).toBe('SAICA');
  expect(tile('Nedbank External Bursary Programme', 'Nedbank')).toBe('NEDBANK');
  expect(tile('Clicks Foundation Bursary Fund', 'Clicks Foundation')).toBe('CLICKS');
  expect(tile('Old Mutual bursaries for accountants and actuaries', 'Old Mutual')).toBe('OM');
  expect(tile('FirstRand Empowerment Foundation postgraduate bursary (through Feenix)', 'FirstRand Foundation')).toBe('FR');
  expect(tile('UP FLY@UP Assist First-Year Awards', 'FLY@UP Assist')).toBe('FLY@UP');
  expect(tile('Limpopo Department of Public Works, Roads and Infrastructure bursary', 'Limpopo Public Works')).toBe('LPW');
  expect(tile('Example Mining Bursary', null)).toBe('EM');
});
