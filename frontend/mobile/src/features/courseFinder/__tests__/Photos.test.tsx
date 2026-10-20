/**
 * Campus and faculty photos: every one is credited and links to its Commons
 * page; the campus card shows what the photo is and opens that page; a
 * university without a photo shows nothing (its monogram stays in the lists).
 */
import { expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';
import { Linking } from 'react-native';

import { CAMPUS_PHOTOS } from '../campusPhotos';
import { CampusPhotoCard } from '../components/CampusPhotoCard';
import { PHOTOS } from '../facultyPhotos';
import { funderPhoto } from '../funderPhotos';

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

test('the campus card shows what the photo is, and its credit opens the Commons page', () => {
  const open = jest.spyOn(Linking, 'openURL').mockResolvedValue(true);
  render(<CampusPhotoCard university="up" />);
  expect(screen.getByText('The Old Arts Building, Hatfield campus, at dusk')).toBeTruthy();
  fireEvent.press(screen.getByText('Photo: Sian Tiley-Nel, CC BY-SA 4.0, Wikimedia Commons (cropped)'));
  expect(open).toHaveBeenCalledWith(
    'https://commons.wikimedia.org/wiki/File:Old_Arts_Building_of_the_University_of_Pretoria_Museums,_South_Africa.jpg',
  );
});

test('a university without a photo shows no card', () => {
  render(<CampusPhotoCard university="smu" />);
  expect(screen.toJSON()).toBeNull();
});

test("a funder's picture is its field's photo, the library for any field, never a logo", () => {
  expect(funderPhoto({ any_field: false, fields: [{ id: 'engineering' }, { id: 'built_environment' }, { id: 'commerce' }] })).toBe(
    PHOTOS.engineering,
  );
  expect(funderPhoto({ any_field: true, fields: [] })).toBe(PHOTOS.humanities);
  expect(funderPhoto({ fields: [{ id: 'no_such_field' }] })).toBe(PHOTOS.humanities);
});
