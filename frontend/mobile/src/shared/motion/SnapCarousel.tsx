/**
 * Cards in a row that swipe and settle one at a time, edge to edge of the
 * screen, with pill dots that stretch to show where you are.
 */
import { ReactNode, useState } from 'react';
import { Animated, StyleSheet, View } from 'react-native';

import { colors } from '@/shared/theme/tokens';

type Props<T> = {
  items: T[];
  cardWidth: number;
  keyOf: (item: T) => string;
  render: (item: T) => ReactNode;
  /** What the row holds, for a screen reader. */
  label: string;
  /** The screen's side padding, which the row runs through to the edges. */
  bleed?: number;
};

const GAP = 12;

export function SnapCarousel<T>({ items, cardWidth, keyOf, render, label, bleed = 20 }: Props<T>) {
  const [scrollX] = useState(() => new Animated.Value(0));
  const step = cardWidth + GAP;
  return (
    <View style={{ gap: 10 }}>
      <Animated.ScrollView
        horizontal
        accessibilityLabel={label}
        showsHorizontalScrollIndicator={false}
        snapToInterval={step}
        decelerationRate="fast"
        style={{ marginHorizontal: -bleed }}
        contentContainerStyle={{ gap: GAP, paddingHorizontal: bleed }}
        scrollEventThrottle={16}
        onScroll={Animated.event([{ nativeEvent: { contentOffset: { x: scrollX } } }], { useNativeDriver: false })}>
        {items.map((item) => (
          <View key={keyOf(item)} style={{ width: cardWidth }}>
            {render(item)}
          </View>
        ))}
      </Animated.ScrollView>
      {items.length > 1 ? (
        <View style={styles.dots} importantForAccessibility="no-hide-descendants" accessibilityElementsHidden>
          {items.map((item, i) => {
            const range = [(i - 1) * step, i * step, (i + 1) * step];
            const width = scrollX.interpolate({ inputRange: range, outputRange: [7, 22, 7], extrapolate: 'clamp' });
            const backgroundColor = scrollX.interpolate({ inputRange: range, outputRange: [colors.line, colors.accent, colors.line], extrapolate: 'clamp' });
            return <Animated.View key={keyOf(item)} style={[styles.dot, { width, backgroundColor }]} />;
          })}
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  dots: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 6 },
  dot: { height: 7, borderRadius: 4 },
});
