/**
 * A card's barcode, black on white with quiet zones either side (scanners need the white margin), drawn as SVG
 * rectangles from barcode.ts. The number sits under it so a cashier can type it if their scanner can't read a
 * phone screen. Hidden from screen readers: the number is read out instead.
 */
import { StyleSheet, Text, View } from 'react-native';
import Svg, { Rect } from 'react-native-svg';

import { fonts } from '@/shared/theme/tokens';

import { barcodeFor } from '../barcode';

const QUIET = 10; // modules of white either side

export function BarcodeView({ number, height = 120 }: { number: string; height?: number }) {
  const code = barcodeFor(number);
  if (!code) return null;
  const total = code.widths.reduce((a, b) => a + b, 0) + QUIET * 2;
  let x = QUIET;
  const bars: { x: number; w: number }[] = [];
  code.widths.forEach((w, i) => {
    if (i % 2 === 0) bars.push({ x, w });
    x += w;
  });
  return (
    <View style={styles.card} accessible accessibilityLabel={number}>
      <Svg width="100%" height={height} viewBox={`0 0 ${total} 100`} preserveAspectRatio="none">
        <Rect x={0} y={0} width={total} height={100} fill="#FFFFFF" />
        {bars.map((b, i) => (
          <Rect key={i} x={b.x} y={0} width={b.w} height={100} fill="#000000" />
        ))}
      </Svg>
      <Text style={styles.number} selectable>
        {number.replace(/(.{4})/g, '$1 ').trim()}
      </Text>
    </View>
  );
}

// Barcode colours are fixed black and white whatever the theme: scanners read nothing else reliably.
const styles = StyleSheet.create({
  card: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: 16, gap: 10, alignItems: 'stretch' },
  number: { fontFamily: fonts.bold, fontSize: 20, letterSpacing: 1.5, color: '#000000', textAlign: 'center', fontVariant: ['tabular-nums'] },
});
