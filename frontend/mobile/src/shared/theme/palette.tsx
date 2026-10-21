/**
 * Palettes with the same keys, so a screen looks right under any of them:
 *
 *  - paper: the whole app since 21 Oct 2026 (Daylight paper, below);
 *  - forest: Rinsuna's homescreen wallpaper with forest glass, now for hero areas only (the welcome screen);
 *  - night: the black student side used until 21 Oct 2026, kept for comparison. A
 *    black page with dark grey cards, so the content stands out, and one colour per job: titles white,
 *    body text light grey, secondary text and small labels mid grey, actions and what's on track in
 *    mint, attention in amber, what's urgent or late in coral.
 *
 * Every text colour meets WCAG AA (4.5:1) on the surfaces it's used on (palette.test.ts checks it).
 * A component reads its colours with usePalette() and builds its styles with useStyles(), which keeps one
 * StyleSheet per palette, so switching costs nothing after the first render.
 */
import { createContext, ReactNode, useContext } from 'react';

import { colors as forestColors } from './tokens';

export type Palette = { [K in keyof typeof forestColors]: string } & {
  /** The page under everything: the wallpaper's base, or black. */
  page: string;
  /** Whether screens draw the forest wallpaper behind themselves. */
  wallpaper: boolean;
  /** One colour per module in the timetable and calendar, readable on the cards (as text and as a bar). */
  classColours: readonly string[];
};

const CLASS_COLOURS = ['#7FD99A', '#7CC4FF', '#C9A7FF', '#FFC266', '#FF9CCB', '#5ED6C8', '#C6E77A', '#FFA97A'] as const;

export const forest: Palette = { ...forestColors, page: forestColors.porcelain, wallpaper: true, classColours: CLASS_COLOURS };

export const night: Palette = {
  ink: '#FFFFFF', // titles, icons, the main text on cards
  inkSoft: '#E6E8E6',
  accent: '#7FD99A', // the main action: a mint pill with near-black words
  accentDeep: '#8FE3A8', // links and selected words
  accentTint: 'rgba(127, 217, 154, 0.16)',
  marigold: '#FFC266', // attention: busy, due soon, pending
  marigoldDeep: '#FFC266',
  marigoldTint: 'rgba(255, 194, 102, 0.16)',
  jade: '#7FD99A', // on track, done
  jadeTint: 'rgba(127, 217, 154, 0.16)',
  garnet: '#FF8A7A', // urgent, late, errors
  garnetTint: 'rgba(255, 138, 122, 0.16)',
  porcelain: '#000000',
  line: 'rgba(255, 255, 255, 0.10)',
  white: '#141615', // cards, fields, sheets: dark grey on black
  text: '#F2F3F2',
  textMuted: '#B4BAB6', // secondary text
  textFaint: '#8E9591', // small labels, hints
  iconTile: 'rgba(255, 255, 255, 0.08)',
  infoTint: '#1C1F1D',
  overlay: 'rgba(0, 0, 0, 0.55)',
  pillText: '#0B0D0C',
  glassElevated: '#1A1D1B',
  dock: '#101211',
  onAccent: '#FFFFFF',
  onAccentSoft: 'rgba(255, 255, 255, 0.86)',
  onAccentTint: 'rgba(255, 255, 255, 0.14)',
  page: '#000000',
  wallpaper: false,
  classColours: CLASS_COLOURS,
};

/**
 * Daylight paper (chosen by Rinsuna, 21 Oct 2026): the whole app on warm cream paper with white cards and
 * forest ink, readable in sunlight on any screen. Her wallpaper stays for hero areas (the welcome screen and
 * the summary cards at the top of a screen), the main button is a forest pill with cream words, and signals
 * are forest (on track), amber (attention) and rose (urgent). Module colours are deep earth tones that read
 * on white.
 */
export const paper: Palette = {
  ink: '#1C2B1E', // titles, icons, the main text on cards
  inkSoft: '#4A5A4C',
  accent: '#2F6B3A', // the main action: a forest pill with cream words
  accentDeep: '#2F6B3A', // links and selected words
  accentTint: '#E3EFDF',
  marigold: '#8A5300', // attention: busy, due soon, pending
  marigoldDeep: '#8A5300',
  marigoldTint: '#FBEBCF',
  jade: '#2F6B3A', // on track, done
  jadeTint: '#E3EFDF',
  garnet: '#A3332A', // urgent, late, errors
  garnetTint: '#FBE3DE',
  porcelain: '#F4EFE3',
  line: 'rgba(28, 49, 30, 0.10)',
  white: '#FFFDF8', // cards, fields, sheets: white on cream
  text: '#1C2B1E',
  textMuted: '#4A5A4C', // secondary text
  textFaint: '#56645A', // small labels, hints
  iconTile: '#ECE6D8',
  infoTint: '#ECE6D8',
  overlay: 'rgba(28, 43, 30, 0.45)',
  pillText: '#F4EFE3',
  glassElevated: '#FFFFFF',
  dock: '#FFFDF8',
  onAccent: '#FFFFFF', // words on the wallpaper
  onAccentSoft: 'rgba(255, 255, 255, 0.86)',
  onAccentTint: 'rgba(255, 255, 255, 0.18)',
  page: '#F4EFE3',
  wallpaper: false,
  classColours: ['#2F6B3A', '#3B5B8C', '#86506D', '#8A5300', '#A1405A', '#2F5F5C', '#56652F', '#94462B'],
};

const PaletteContext = createContext<Palette>(paper);

export function PaletteProvider({ palette, children }: { palette: Palette; children: ReactNode }) {
  return <PaletteContext.Provider value={palette}>{children}</PaletteContext.Provider>;
}

export function usePalette(): Palette {
  return useContext(PaletteContext);
}

const cache = new WeakMap<(c: Palette) => unknown, Map<Palette, unknown>>();

/** A component's styles for the palette it's under, made once per palette. */
export function useStyles<T>(make: (c: Palette) => T): T {
  const palette = usePalette();
  let byPalette = cache.get(make);
  if (!byPalette) {
    byPalette = new Map();
    cache.set(make, byPalette);
  }
  if (!byPalette.has(palette)) byPalette.set(palette, make(palette));
  return byPalette.get(palette) as T;
}
