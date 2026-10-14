/**
 * Rinsuna's homescreen gradient behind a screen, forest moss at the top to
 * terracotta rose at the bottom, under a light dark veil so white text on it
 * stays readable. Sits behind everything and takes no touches.
 */
import { LinearGradient } from 'expo-linear-gradient';
import { StyleSheet, View } from 'react-native';

import { wallpaper } from '@/shared/theme/tokens';

export function Wallpaper() {
  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      <LinearGradient colors={[...wallpaper.colors]} locations={[...wallpaper.stops]} style={StyleSheet.absoluteFill} />
      <View style={[StyleSheet.absoluteFill, { backgroundColor: wallpaper.veil }]} />
    </View>
  );
}
