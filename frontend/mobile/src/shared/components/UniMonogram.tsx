/**
 * A university's short name on a forest-glass tile ("UJ", "WITS", "UKZN").
 * Text only, by the brief's rule: never a university's logo, crest or colours.
 * Hidden from screen readers: the row beside it says the full name.
 */
import { StyleSheet, Text, View } from 'react-native';

import { brand, colors, fonts, radius } from '@/shared/theme/tokens';

export function UniMonogram({ id, size = 46 }: { id: string; size?: number }) {
  const label = id.toUpperCase();
  // Longer names (UNIZULU, UNIVEN) get smaller letters so they fit the tile.
  const fontSize = Math.round(size * (label.length <= 3 ? 0.34 : label.length <= 4 ? 0.28 : label.length <= 5 ? 0.23 : 0.19));
  return (
    <View
      style={[styles.tile, { width: size, height: size }]}
      accessibilityElementsHidden
      importantForAccessibility="no-hide-descendants">
      <Text style={[styles.text, { fontSize }]} numberOfLines={1}>
        {label}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
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
