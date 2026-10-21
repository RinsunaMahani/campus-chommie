/**
 * Tabs inside a screen, as one pill: the highlight slides to the tab chosen.
 * Each tab is a tab to a screen reader, marked when selected.
 */
import { useEffect, useState } from 'react';
import { Animated, Pressable, StyleSheet, Text, View } from 'react-native';

import { fonts, radius } from '@/shared/theme/tokens';

import { motionOff, NATIVE } from './motion';
import { Palette, useStyles } from '@/shared/theme/palette';

type Props = { tabs: string[]; index: number; onChange: (index: number) => void };

const PAD = 4;

export function SlidingTabs({ tabs, index, onChange }: Props) {
  const styles = useStyles(makeStyles);
  const [width, setWidth] = useState(0);
  const [at] = useState(() => new Animated.Value(index));
  useEffect(() => {
    if (motionOff()) at.setValue(index);
    else Animated.spring(at, { toValue: index, useNativeDriver: NATIVE, speed: 18, bounciness: 5 }).start();
  }, [at, index]);

  const tabWidth = width ? (width - PAD * 2) / tabs.length : 0;
  const last = Math.max(1, tabs.length - 1);
  const x = at.interpolate({ inputRange: [0, last], outputRange: [0, tabWidth * last] });

  return (
    <View accessibilityRole="tablist" style={styles.bar} onLayout={(e) => setWidth(e.nativeEvent.layout.width)}>
      {tabWidth ? <Animated.View style={[styles.highlight, { width: tabWidth, transform: [{ translateX: x }] }]} /> : null}
      {tabs.map((label, i) => (
        <Pressable
          key={label}
          accessibilityRole="tab"
          accessibilityState={{ selected: i === index }}
          onPress={() => onChange(i)}
          style={styles.tab}>
          <Text style={[styles.label, i === index && styles.labelOn]} numberOfLines={1}>
            {label}
          </Text>
        </Pressable>
      ))}
    </View>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  bar: {
    flexDirection: 'row',
    padding: PAD,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.white,
  },
  highlight: { position: 'absolute', top: PAD, bottom: PAD, left: PAD, borderRadius: radius.pill, backgroundColor: colors.ink },
  tab: { flex: 1, alignItems: 'center', paddingVertical: 10, paddingHorizontal: 6 },
  label: { fontFamily: fonts.semibold, fontSize: 15, color: colors.textMuted },
  labelOn: { color: colors.pillText },
});
