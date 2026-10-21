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
import { funderMonogram, funderPhoto } from '../funderPhotos';

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
