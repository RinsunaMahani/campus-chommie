/**
 * A short name on an earth-tone tile: a university's ("UJ", "WITS", "UKZN") or a funder's ("NSFAS", "CSIR").
 * Text only, by the brief's rule: never a logo, crest or brand colours, which are their owners' trademarks
 * and would read as an endorsement. Hidden from screen readers: the row beside it says the full name.
 */
import { StyleSheet, Text, View } from 'react-native';

import { fonts, radius } from '@/shared/theme/tokens';
import { Palette, useStyles } from '@/shared/theme/palette';

/**
 * Eight earth tones from Rinsuna's wallpaper (forest, olive, khaki, mauve, rose, terracotta, ochre, teal), each
 * with letters that pass WCAG AA on it. A tile's colour comes from its letters by a fixed rule (FNV-1a), so it
 * never changes and is never chosen to match a university's or funder's own colours.
 */
export const TILE_TONES = [
  { bg: '#2F6B3A', fg: '#F4EFE3' },
  { bg: '#56652F', fg: '#F4EFE3' },
  { bg: '#6E6A3E', fg: '#FFFDF3' },
  { bg: '#86506D', fg: '#FBEFF5' },
  { bg: '#93565E', fg: '#FFF3F1' },
  { bg: '#94462B', fg: '#FFF1EA' },
  { bg: '#7E5C14', fg: '#FFF6E2' },
  { bg: '#2F5F5C', fg: '#E9F6F4' },
] as const;

export function toneFor(label: string): (typeof TILE_TONES)[number] {
  let h = 2166136261;
  for (const ch of label.toUpperCase()) {
    h ^= ch.charCodeAt(0);
    h = Math.imul(h, 16777619) >>> 0;
  }
  return TILE_TONES[h % TILE_TONES.length];
}

export function Monogram({ label, size = 46 }: { label: string; size?: number }) {
  const styles = useStyles(makeStyles);
  const text = label.toUpperCase();
  const tone = toneFor(text);
  // Longer names (UNIZULU, NEDBANK) get smaller letters so they fit the tile.
  const scale = text.length <= 3 ? 0.34 : text.length <= 4 ? 0.28 : text.length <= 5 ? 0.23 : text.length <= 6 ? 0.19 : 0.17;
  return (
    <View
      style={[styles.tile, { width: size, height: size, backgroundColor: tone.bg }]}
      accessibilityElementsHidden
      importantForAccessibility="no-hide-descendants">
      <Text style={[styles.text, { fontSize: Math.round(size * scale), color: tone.fg }]} numberOfLines={1}>
        {text}
      </Text>
    </View>
  );
}

export function UniMonogram({ id, size = 46 }: { id: string; size?: number }) {
  return <Monogram label={id} size={size} />;
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  tile: {
    borderRadius: radius.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: { fontFamily: fonts.extrabold, color: colors.ink, letterSpacing: 0.3 },
});
