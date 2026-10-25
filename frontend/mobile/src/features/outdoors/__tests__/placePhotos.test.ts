/**
 * The real photo list: each place near campus, named as the data packs name it, gets a slideshow of 3 to 5 credited
 * Commons photos, or none at all.
 */
import { expect, test } from '@jest/globals';

import { MAX_PHOTOS, MIN_PHOTOS, PLACE_PHOTOS, photosFor } from '../placePhotos';

// As the university packs name them (backend/data/universities: cheap_things).
const WITH_PHOTOS = [
  'Pretoria National Botanical Garden',
  'Freedom Park',
  'Voortrekker Monument',
  'DITSONG National Museum of Natural History',
  'Wonderboom Nature Reserve: a fig tree over 1 000 years old, and walks on the Magaliesberg',
  'DITSONG: Tswaing Meteorite Crater',
  'Lowveld National Botanical Garden',
];

test('every place with photos gets a slideshow of 3 to 5', () => {
  for (const name of WITH_PHOTOS) {
    const n = photosFor(name).length;
    expect([name, n >= MIN_PHOTOS && n <= MAX_PHOTOS]).toEqual([name, true]);
  }
  expect(Object.keys(PLACE_PHOTOS)).toHaveLength(WITH_PHOTOS.length);
});

test('a place without its own photos gets none, never another place\'s', () => {
  expect(photosFor('Wits Art Museum')).toEqual([]);
});

test('every photo says what it shows and who took it, and links its Commons page', () => {
  for (const photos of Object.values(PLACE_PHOTOS)) {
    for (const p of photos) {
      expect(p.caption.length).toBeGreaterThan(3);
      expect(p.credit).toMatch(/, (CC BY(-SA)? \d\.\d|CC0|Public domain), Wikimedia Commons \(cropped\)$/);
      expect(p.source).toMatch(/^https:\/\/commons\.wikimedia\.org\/wiki\/File:/);
    }
  }
});
