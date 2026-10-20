/**
 * Every text colour in the night palette is readable (WCAG AA, 4.5:1) on the black page and on the
 * cards; the mint pill's words are readable on the pill. Both palettes have the same keys.
 */
import { expect, test } from '@jest/globals';

import { forest, night } from '../palette';

function rgb(hex: string): [number, number, number] {
  const h = hex.replace('#', '');
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16) / 255) as [number, number, number];
}
function luminance(hex: string): number {
  const [r, g, b] = rgb(hex).map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
function contrast(a: string, b: string): number {
  const [x, y] = [luminance(a), luminance(b)].sort((p, q) => q - p);
  return (x + 0.05) / (y + 0.05);
}

const TEXT = ['ink', 'text', 'textMuted', 'textFaint', 'accentDeep', 'jade', 'marigold', 'garnet'] as const;
const SURFACES = ['page', 'white', 'glassElevated', 'infoTint', 'dock'] as const;

test.each(TEXT.flatMap((text) => SURFACES.map((surface) => [text, surface] as const)))(
  'night: %s on %s meets 4.5:1',
  (text, surface) => {
    expect(contrast(night[text], night[surface])).toBeGreaterThanOrEqual(4.5);
  },
);

test.each([...night.classColours])('night: class colour %s reads on the cards', (colour) => {
  expect(contrast(colour, night.white)).toBeGreaterThanOrEqual(4.5);
});

test('the words on the mint pill and on coral are readable', () => {
  expect(contrast(night.pillText, night.accent)).toBeGreaterThanOrEqual(4.5);
  expect(contrast(night.pillText, night.garnet)).toBeGreaterThanOrEqual(4.5);
});

test('both palettes have the same keys, so a screen looks right under either', () => {
  expect(Object.keys(night).sort()).toEqual(Object.keys(forest).sort());
  expect(night.wallpaper).toBe(false);
  expect(forest.wallpaper).toBe(true);
});
