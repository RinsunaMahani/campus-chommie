/**
 * Design tokens: deep indigo for text and main actions, violet for the
 * accent (primary call to action, progress, selection), and amber, green
 * and red only for signals (Busy, Manageable, Heavy; attention). Clean
 * light background. Every text colour meets WCAG AA on the backgrounds
 * it is used on. No university's colours: the app serves them all.
 *
 * Key names are kept stable so screens don't churn when values change.
 */
export const colors = {
  ink: '#1E1B4B', // deep indigo: text, primary buttons, headers
  inkSoft: '#312E81',
  accent: '#6D28D9', // violet: main call to action, progress, selected
  accentDeep: '#5B21B6',
  accentTint: '#EDE9FE',
  marigold: '#F59E0B', // amber: attention only (busy, due soon, pending)
  marigoldDeep: '#B45309',
  marigoldTint: '#FEF3C7',
  jade: '#047857', // green: manageable, done
  jadeTint: '#D1FAE5',
  garnet: '#DC2626', // red: heavy, errors
  garnetTint: '#FEE2E2',
  porcelain: '#F8F7FC', // app background
  line: '#E6E3F0',
  white: '#FFFFFF',
  text: '#1E1B4B',
  textMuted: '#5E5978',
  textFaint: '#9A95AF',
  iconTile: '#F1EFF8',
  infoTint: '#F1EFF8',
  overlay: 'rgba(30, 27, 75, 0.5)',
  // On the violet band at the top of a screen (white is at least 6:1 on it)
  onAccent: '#FFFFFF',
  onAccentSoft: 'rgba(255, 255, 255, 0.86)',
  onAccentTint: 'rgba(255, 255, 255, 0.18)',
} as const;

export const fonts = {
  // Titles and money: the wordmark's heavy sans, so text matches the logo.
  display: 'PlusJakartaSans_800ExtraBold',
  body: 'PlusJakartaSans_400Regular',
  medium: 'PlusJakartaSans_500Medium',
  semibold: 'PlusJakartaSans_600SemiBold',
  bold: 'PlusJakartaSans_700Bold',
  extrabold: 'PlusJakartaSans_800ExtraBold',
} as const;

/** Logo colours for the mark, wordmark, icon and splash (assets/images match these). */
export const brand = {
  violet: '#6D28D9',
  violetLight: '#7C3AED',
  violetDeep: '#5B21B6',
  lavender: '#DDD6FE',
  gold: '#FBBF24',
  white: '#FFFFFF',
} as const;

export const space = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24, xxl: 32 } as const;

export const radius = { sm: 10, md: 14, lg: 18, xl: 24, pill: 999 } as const;

// Big targets: buttons 52 px high, inputs 50.
export const sizes = { button: 52, input: 50, iconButton: 36, tile: 40 } as const;
