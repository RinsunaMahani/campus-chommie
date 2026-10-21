/**
 * Design tokens: Rinsuna's homescreen. Every screen sits on her wallpaper
 * gradient (forest moss down to terracotta rose) under a light dark veil;
 * cards, fields and sheets are dark forest glass with white text; the main
 * action is a crisp white pill with near-black text. Mint, amber and coral
 * only for signals (manageable or done, attention, heavy or errors). Every
 * text colour meets WCAG AA where it's used: white on glass is above 12:1;
 * on the veiled wallpaper's lightest bands (sage gold and rose) white is
 * above 5:1 and muted text above 4.5:1. Notes are the darker glass, so they
 * read anywhere. No university's colours.
 *
 * Key names are kept stable so screens don't churn when values change: so
 * "white" is the glass surface, "ink" and "text" are what reads on it, and
 * "accent" is the white pill, with "pillText" on it.
 */
export const colors = {
  ink: '#FFFFFF', // text and icons on glass; the primary button's pill
  inkSoft: '#EDE8D8', // cream
  accent: '#FFFFFF', // the white pill: main call to action, selected
  accentDeep: '#A8E6B4', // mint: selected words and icons on glass
  accentTint: 'rgba(168, 230, 180, 0.20)',
  marigold: '#FFD08A', // amber: attention only (busy, due soon, pending)
  marigoldDeep: '#FFD08A',
  marigoldTint: 'rgba(255, 208, 138, 0.22)',
  jade: '#A8E6B4', // mint: manageable, done
  jadeTint: 'rgba(168, 230, 180, 0.20)',
  garnet: '#FFB4A8', // coral: heavy, errors
  garnetTint: 'rgba(255, 180, 168, 0.22)',
  porcelain: '#417F4B', // under the wallpaper, where a screen has none
  line: 'rgba(255, 255, 255, 0.15)',
  white: 'rgba(28, 49, 30, 0.88)', // forest glass: cards, fields, sheets
  text: '#FFFFFF',
  textMuted: 'rgba(255, 255, 255, 0.85)',
  textFaint: 'rgba(255, 255, 255, 0.58)',
  iconTile: 'rgba(255, 255, 255, 0.10)',
  infoTint: 'rgba(24, 34, 26, 0.72)',
  overlay: 'rgba(8, 16, 9, 0.62)',
  // The white pill's words, and what reads on mint, amber and coral
  pillText: '#111A13',
  // Glass a step up (the points card), and the floating dock
  glassElevated: 'rgba(22, 40, 24, 0.92)',
  dock: 'rgba(25, 42, 27, 0.90)',
  // On the wallpaper itself
  onAccent: '#FFFFFF',
  onAccentSoft: 'rgba(255, 255, 255, 0.86)',
  onAccentTint: 'rgba(255, 255, 255, 0.18)',
} as const;

/** The wallpaper, top to bottom, sampled from Rinsuna's homescreen, and the veil that keeps white text readable on it. */
export const wallpaper = {
  colors: ['#417F4B', '#7A8B54', '#959167', '#AD708E', '#B68389'] as const,
  stops: [0, 0.32, 0.54, 0.78, 1] as const,
  veil: 'rgba(12, 22, 13, 0.32)',
};

export const fonts = {
  // Titles and big numbers: Fraunces, a warm serif (Daylight paper, 21 Oct 2026). The wordmark keeps the sans.
  display: 'Fraunces_700Bold',
  displaySemi: 'Fraunces_600SemiBold',
  body: 'PlusJakartaSans_400Regular',
  medium: 'PlusJakartaSans_500Medium',
  semibold: 'PlusJakartaSans_600SemiBold',
  bold: 'PlusJakartaSans_700Bold',
  extrabold: 'PlusJakartaSans_800ExtraBold',
} as const;

/** Logo colours for the CC monogram, wordmark, icon and splash (assets/images match these). */
export const brand = {
  forest: '#417F4B',
  glass: 'rgba(22, 40, 24, 0.92)',
  glassFrom: '#2B4C2E',
  glassTo: '#182C1A',
  rim: 'rgba(255, 255, 255, 0.22)',
  cream: '#EDE8D8',
  white: '#FFFFFF',
} as const;

/**
 * The type scale. Platform guidance and readability studies agree on 16 for body text on a phone (Material: 14 at
 * the least), a line height about 1.5 times the size, and a large title at the top of a screen that shrinks to a
 * bar as you scroll (iOS uses 34). Captions and labels never go under 13, except inside dense grids (the calendar,
 * the tab bar) where space is the point.
 */
export const type = {
  largeTitle: { fontSize: 32, lineHeight: 38 }, // the screen's name, top left
  title: { fontSize: 22, lineHeight: 28 }, // a section that heads its own cards
  headline: { fontSize: 17, lineHeight: 23 }, // a card's title; the compact header bar
  body: { fontSize: 16, lineHeight: 24 },
  callout: { fontSize: 15, lineHeight: 22 }, // secondary lines in a card
  label: { fontSize: 14, lineHeight: 20 }, // meta lines, field hints
  caption: { fontSize: 13, lineHeight: 18 }, // sources, credits, timestamps
} as const;

export const space = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24, xxl: 32 } as const;

export const radius = { sm: 10, md: 14, lg: 18, xl: 24, pill: 999 } as const;

// Big targets: buttons 52 px high, inputs 50.
export const sizes = { button: 52, input: 50, iconButton: 36, tile: 40 } as const;
