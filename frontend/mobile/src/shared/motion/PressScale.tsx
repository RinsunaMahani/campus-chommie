/**
 * A card or row that sinks a little under the thumb, so it answers the touch
 * before the next screen arrives. Otherwise it's a plain Pressable.
 */
import { ReactNode, useState } from 'react';
import { Animated, Pressable, PressableProps, StyleProp, ViewStyle } from 'react-native';

import { motionOff, NATIVE } from './motion';

type Props = Omit<PressableProps, 'style' | 'children'> & { style?: StyleProp<ViewStyle>; children: ReactNode; scale?: number };

export function PressScale({ style, children, scale = 0.97, onPressIn, onPressOut, ...props }: Props) {
  const [value] = useState(() => new Animated.Value(1));
  const to = (v: number) => {
    if (motionOff()) return;
    Animated.spring(value, { toValue: v, useNativeDriver: NATIVE, speed: 40, bounciness: 4 }).start();
  };
  return (
    <Pressable
      {...props}
      onPressIn={(e) => {
        to(scale);
        onPressIn?.(e);
      }}
      onPressOut={(e) => {
        to(1);
        onPressOut?.(e);
      }}>
      <Animated.View style={[style, { transform: [{ scale: value }] }]}>{children}</Animated.View>
    </Pressable>
  );
}
