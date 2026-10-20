/**
 * Placeholders while an answer loads: blocks in the shape of what's coming,
 * with light sweeping across, so the screen doesn't jump when it arrives.
 */
import { LinearGradient } from 'expo-linear-gradient';
import { useEffect, useState } from 'react';
import { Animated, DimensionValue, Easing, StyleSheet, View } from 'react-native';

import { Card } from '@/shared/components/Parts';
import { t } from '@/shared/i18n';
import { radius } from '@/shared/theme/tokens';

import { motionOff, NATIVE } from './motion';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';

export function Shimmer({ width = '100%', height = 14, rounded = 8 }: { width?: DimensionValue; height?: number; rounded?: number }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const [sweep] = useState(() => new Animated.Value(0));
  const [boxWidth, setBoxWidth] = useState(0);
  useEffect(() => {
    if (motionOff()) return;
    const loop = Animated.loop(Animated.timing(sweep, { toValue: 1, duration: 1200, easing: Easing.linear, useNativeDriver: NATIVE }));
    loop.start();
    return () => loop.stop();
  }, [sweep]);
  const x = sweep.interpolate({ inputRange: [0, 1], outputRange: [-boxWidth, boxWidth] });
  return (
    <View onLayout={(e) => setBoxWidth(e.nativeEvent.layout.width)} style={[styles.block, { width, height, borderRadius: rounded }]}>
      {boxWidth ? (
        <Animated.View style={[StyleSheet.absoluteFill, { transform: [{ translateX: x }] }]}>
          <LinearGradient
            colors={[colors.iconTile, colors.white, colors.iconTile]}
            start={{ x: 0, y: 0.5 }}
            end={{ x: 1, y: 0.5 }}
            style={StyleSheet.absoluteFill}
          />
        </Animated.View>
      ) : null}
    </View>
  );
}

/** Cards of placeholder lines, said to a screen reader as loading. */
export function SkeletonCards({ count = 3 }: { count?: number }) {
  return (
    <View accessibilityLabel={t('common.loading')} accessible style={{ gap: 12 }}>
      {Array.from({ length: count }, (_, i) => (
        <Card key={i} style={{ gap: 10 }}>
          <Shimmer width="45%" height={12} />
          <Shimmer width="85%" height={18} />
          <Shimmer width="60%" height={12} />
        </Card>
      ))}
    </View>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  block: { backgroundColor: colors.iconTile, overflow: 'hidden', borderRadius: radius.sm },
});
