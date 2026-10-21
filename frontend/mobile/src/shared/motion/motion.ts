/**
 * What every moving part shares: whether animations may run on the native
 * thread (not on the web), and whether the phone asks for less motion, in
 * which case things change at once instead of moving.
 */
import { AccessibilityInfo, Easing, Platform } from 'react-native';

/** The native driver exists on phones only; the web runs the same animations in JavaScript. */
export const NATIVE = Platform.OS !== 'web';

/** How things settle: fast out, gentle at the end. */
export const EASE_OUT = Easing.out(Easing.cubic);

let reduced = false;
AccessibilityInfo.isReduceMotionEnabled?.()
  .then((on) => {
    reduced = on;
  })
  .catch(() => undefined);
AccessibilityInfo.addEventListener?.('reduceMotionChanged', (on) => {
  reduced = on;
});

/** True when the phone's settings ask for reduced motion: then things change at once. */
export function motionOff(): boolean {
  return reduced;
}
