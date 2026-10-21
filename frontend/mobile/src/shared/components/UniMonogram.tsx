/**
 * A short name on a forest-glass tile: a university's ("UJ", "WITS", "UKZN") or a funder's ("NSFAS", "CSIR").
 * Text only, by the brief's rule: never a logo, crest or brand colours, which are their owners' trademarks
 * and would read as an endorsement. Hidden from screen readers: the row beside it says the full name.
 */
import { StyleSheet, Text, View } from 'react-native';

import { brand, fonts, radius } from '@/shared/theme/tokens';
import { Palette, useStyles } from '@/shared/theme/palette';

export function Monogram({ label, size = 46 }: { label: string; size?: number }) {
  const styles = useStyles(makeStyles);
  const text = label.toUpperCase();
  // Longer names (UNIZULU, NEDBANK) get smaller letters so they fit the tile.
  const scale = text.length <= 3 ? 0.34 : text.length <= 4 ? 0.28 : text.length <= 5 ? 0.23 : text.length <= 6 ? 0.19 : 0.17;
  return (
    <View
      style={[styles.tile, { width: size, height: size }]}
      accessibilityElementsHidden
      importantForAccessibility="no-hide-descendants">
      <Text style={[styles.text, { fontSize: Math.round(size * scale) }]} numberOfLines={1}>
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
    borderWidth: 1,
    borderColor: brand.rim,
    backgroundColor: colors.glassElevated,
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: { fontFamily: fonts.extrabold, color: colors.ink, letterSpacing: 0.3 },
});
