/**
 * The Campus Chommie mark and wordmark, drawn in code so they stay crisp
 * at any size. The same shapes are in the app icon and splash
 * (assets/images); change both together.
 *
 * The mark: two interlocking Cs, white and cream, on a forest-glass tile.
 * Never a university's logo or colours.
 */
import { StyleSheet, Text, View } from 'react-native';
import Svg, { Defs, LinearGradient, Path, Rect, Stop } from 'react-native-svg';

import { brand, fonts } from '@/shared/theme/tokens';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';

/** The CC monogram's two strokes, on a 64-unit square. */
function Cs({ stroke = 7 }: { stroke?: number }) {
  return (
    <>
      <Path d="M29 15C18.5 15 11 22.4 11 32C11 41.6 18.5 49 29 49" stroke={brand.white} strokeWidth={stroke} strokeLinecap="round" fill="none" />
      <Path d="M49 15C38.5 15 31 22.4 31 32C31 41.6 38.5 49 49 49" stroke={brand.cream} strokeWidth={stroke} strokeLinecap="round" fill="none" />
    </>
  );
}

/** The app-icon tile with the CC inside. */
export function BrandMark({ size = 56 }: { size?: number }) {
  return (
    <Svg width={size} height={size} viewBox="0 0 64 64" accessibilityLabel="Campus Chommie">
      <Defs>
        <LinearGradient id="tile" x1="0" y1="0" x2="1" y2="1">
          <Stop offset="0" stopColor={brand.glassFrom} />
          <Stop offset="1" stopColor={brand.glassTo} />
        </LinearGradient>
      </Defs>
      <Rect x="0.5" y="0.5" width="63" height="63" rx="18" fill="url(#tile)" stroke={brand.rim} strokeWidth="1" />
      <Cs />
    </Svg>
  );
}

/** The wordmark: "Campus" in white and "Chommie" in cream, for the wallpaper and glass. */
export function Wordmark({ size = 26 }: { size?: number }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  return (
    <Text style={[styles.word, { fontSize: size, letterSpacing: -size * 0.02 }]}>
      <Text style={{ color: colors.ink }}>Campus </Text>
      <Text style={{ color: brand.cream }}>Chommie</Text>
    </Text>
  );
}

export function BrandLockup() {
  const styles = useStyles(makeStyles);
  return (
    <View style={styles.lockup}>
      <BrandMark size={44} />
      <Wordmark size={26} />
    </View>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  // Centred, so it still looks right if large system text makes it wrap.
  word: { fontFamily: fonts.extrabold, textAlign: 'center' },
  lockup: { flexDirection: 'row', alignItems: 'center', gap: 12 },
});
