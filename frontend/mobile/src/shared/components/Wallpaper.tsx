/**
 * What sits behind a screen. Under the forest palette: Rinsuna's homescreen gradient, forest moss at the top
 * to terracotta rose at the bottom, under a light dark veil so white text on it stays readable. Under the
 * night palette (the student's side): plain black, so the cards and their colours stand out. Takes no touches.
 */
import { LinearGradient } from 'expo-linear-gradient';
import { StyleSheet, View } from 'react-native';

import { usePalette } from '@/shared/theme/palette';
import { wallpaper } from '@/shared/theme/tokens';

export function Wallpaper() {
  const palette = usePalette();
  if (!palette.wallpaper) {
    return <View style={[StyleSheet.absoluteFill, { backgroundColor: palette.page }]} pointerEvents="none" />;
  }
  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      <LinearGradient colors={[...wallpaper.colors]} locations={[...wallpaper.stops]} style={StyleSheet.absoluteFill} />
      <View style={[StyleSheet.absoluteFill, { backgroundColor: wallpaper.veil }]} />
    </View>
  );
}
