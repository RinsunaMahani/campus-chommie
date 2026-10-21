/**
 * Content that rises into place as it appears: a screen's body, or the items
 * of a list one after another (`delay`).
 */
import { ReactNode, useEffect, useState } from 'react';
import { Animated, StyleProp, ViewStyle } from 'react-native';

import { EASE_OUT, motionOff, NATIVE } from './motion';

export function FadeIn({ children, delay = 0, style }: { children: ReactNode; delay?: number; style?: StyleProp<ViewStyle> }) {
  const [shown] = useState(() => new Animated.Value(0));
  useEffect(() => {
    if (motionOff()) shown.setValue(1);
    else Animated.timing(shown, { toValue: 1, duration: 280, delay, easing: EASE_OUT, useNativeDriver: NATIVE }).start();
  }, [shown, delay]);
  const rise = shown.interpolate({ inputRange: [0, 1], outputRange: [10, 0] });
  return <Animated.View style={[style, { opacity: shown, transform: [{ translateY: rise }] }]}>{children}</Animated.View>;
}
