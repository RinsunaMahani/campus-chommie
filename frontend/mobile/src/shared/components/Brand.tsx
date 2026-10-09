/**
 * The Campus Chommie mark and wordmark, drawn in code so they stay crisp
 * at any size. The same shapes are in the app icon and splash
 * (assets/images); change both together.
 *
 * The mark: a graduation cap on a violet tile, from choosing a course to
 * graduating. Never a university's logo or colours.
 */
import { StyleSheet, Text, View } from 'react-native';
import Svg, { Circle, Defs, LinearGradient, Path, Polygon, Rect, Stop } from 'react-native-svg';

import { brand, colors, fonts } from '@/shared/theme/tokens';

/** The app-icon tile with the cap inside. */
export function BrandMark({ size = 56 }: { size?: number }) {
  return (
    <Svg width={size} height={size} viewBox="0 0 512 512" accessibilityLabel="Campus Chommie">
      <Defs>
        <LinearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
          <Stop offset="0" stopColor={brand.violetLight} />
          <Stop offset="1" stopColor={brand.violetDeep} />
        </LinearGradient>
      </Defs>
      <Rect width="512" height="512" rx="112" fill="url(#bg)" />
      {/* the cap's band, under the board */}
      <Rect x="150" y="250" width="212" height="96" rx="32" fill={brand.lavender} />
      {/* the board */}
      <Polygon points="256,136 450,224 256,312 62,224" fill={brand.white} />
      {/* the tassel */}
      <Path d="M256 224 L400 262 L400 330" stroke={brand.gold} strokeWidth="14" strokeLinecap="round" strokeLinejoin="round" fill="none" />
      <Circle cx="400" cy="348" r="18" fill={brand.gold} />
    </Svg>
  );
}

/** The wordmark: "Campus" + "Chommie" in the accent colour. Pass onDark on violet backgrounds. */
export function Wordmark({ size = 26, onDark = false }: { size?: number; onDark?: boolean }) {
  return (
    <Text style={[styles.word, { fontSize: size, letterSpacing: -size * 0.02 }]}>
      <Text style={{ color: onDark ? brand.white : colors.ink }}>Campus </Text>
      <Text style={{ color: onDark ? brand.lavender : colors.accent }}>Chommie</Text>
    </Text>
  );
}

export function BrandLockup({ onDark = false }: { onDark?: boolean }) {
  return (
    <View style={styles.lockup}>
      <BrandMark size={44} />
      <Wordmark size={26} onDark={onDark} />
    </View>
  );
}

const styles = StyleSheet.create({
  word: { fontFamily: fonts.extrabold },
  lockup: { flexDirection: 'row', alignItems: 'center', gap: 12 },
});
