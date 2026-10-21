/**
 * A section that opens in place: the content grows into view and the chevron
 * turns, instead of the page jumping. Closed, the content is hidden from
 * screen readers too.
 */
import { Feather } from '@expo/vector-icons';
import { ReactNode, useState } from 'react';
import { Animated, Pressable, StyleSheet, Text, View } from 'react-native';

import { fonts } from '@/shared/theme/tokens';

import { EASE_OUT, motionOff } from './motion';

type Props = {
  /** The toggle's words while closed, and while open. */
  closedLabel: string;
  openLabel: string;
  color: string;
  children: ReactNode;
};

export function Expandable({ closedLabel, openLabel, color, children }: Props) {
  const [open, setOpen] = useState(false);
  const [height, setHeight] = useState(0);
  const [shown] = useState(() => new Animated.Value(0));

  function toggle() {
    const next = !open;
    setOpen(next);
    // Height can't run on the native driver.
    if (motionOff()) shown.setValue(next ? 1 : 0);
    else Animated.timing(shown, { toValue: next ? 1 : 0, duration: 300, easing: EASE_OUT, useNativeDriver: false }).start();
  }

  const turn = shown.interpolate({ inputRange: [0, 1], outputRange: ['0deg', '180deg'] });
  return (
    <View>
      <Animated.View style={{ height: shown.interpolate({ inputRange: [0, 1], outputRange: [0, height] }), opacity: shown, overflow: 'hidden' }}>
        <View
          style={styles.measure}
          onLayout={(e) => setHeight(e.nativeEvent.layout.height)}
          accessibilityElementsHidden={!open}
          importantForAccessibility={open ? 'auto' : 'no-hide-descendants'}>
          {children}
        </View>
      </Animated.View>
      <Pressable accessibilityRole="button" accessibilityState={{ expanded: open }} onPress={toggle} hitSlop={6} style={styles.toggle}>
        <Text style={[styles.toggleText, { color }]}>{open ? openLabel : closedLabel}</Text>
        <Animated.View style={{ transform: [{ rotate: turn }] }}>
          <Feather name="chevron-down" size={16} color={color} />
        </Animated.View>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  // Laid out at its full height even while the box around it is closed, so the height is known.
  measure: { position: 'absolute', left: 0, right: 0 },
  toggle: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingTop: 10, alignSelf: 'flex-start' },
  toggleText: { fontFamily: fonts.bold, fontSize: 14.5 },
});
