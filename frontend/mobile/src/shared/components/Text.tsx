import { StyleSheet, Text, TextProps } from 'react-native';

import { fonts, type } from '@/shared/theme/tokens';
import { Palette, useStyles } from '@/shared/theme/palette';

/** Screen title: "Create your account". */
export function Title({ style, ...props }: TextProps) {
  const styles = useStyles(makeStyles);
  return <Text {...props} style={[styles.title, style]} />;
}

/** Big money number: "R2,340". */
export function Money({ style, ...props }: TextProps) {
  const styles = useStyles(makeStyles);
  return <Text {...props} style={[styles.money, style]} />;
}

export function Body({ style, ...props }: TextProps) {
  const styles = useStyles(makeStyles);
  return <Text {...props} style={[styles.body, style]} />;
}

export function Strong({ style, ...props }: TextProps) {
  const styles = useStyles(makeStyles);
  return <Text {...props} style={[styles.strong, style]} />;
}

export function Muted({ style, ...props }: TextProps) {
  const styles = useStyles(makeStyles);
  return <Text {...props} style={[styles.muted, style]} />;
}

/** "STEP 1 OF 4", "TODAY", "YOUR ACCOUNT". */
export function Overline({ style, ...props }: TextProps) {
  const styles = useStyles(makeStyles);
  return <Text {...props} style={[styles.overline, style]} />;
}

export const makeStyles = (colors: Palette) => StyleSheet.create({
  title: { fontFamily: fonts.display, ...type.largeTitle, letterSpacing: -0.6, color: colors.ink },
  // Figures line up in columns and don't jump as they change.
  money: { fontFamily: fonts.display, fontSize: 44, lineHeight: 50, letterSpacing: -1, color: colors.ink, fontVariant: ['tabular-nums'] },
  body: { fontFamily: fonts.body, ...type.body, color: colors.textMuted },
  strong: { fontFamily: fonts.bold, ...type.body, lineHeight: 22, color: colors.text },
  muted: { fontFamily: fonts.body, ...type.label, color: colors.textMuted },
  overline: {
    fontFamily: fonts.bold,
    fontSize: 12.5,
    lineHeight: 18,
    letterSpacing: 0.9,
    color: colors.textMuted,
    textTransform: 'uppercase',
  },
});
