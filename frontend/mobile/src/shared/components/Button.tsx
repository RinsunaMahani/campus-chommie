import { Feather } from '@expo/vector-icons';
import { ComponentProps, ReactNode } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';

import { fonts, radius, sizes } from '@/shared/theme/tokens';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';

type Variant = 'primary' | 'secondary' | 'accent' | 'danger' | 'soft';

type Props = {
  title: string;
  onPress?: () => void;
  variant?: Variant;
  icon?: ComponentProps<typeof Feather>['name'];
  leading?: ReactNode;
  loading?: boolean;
  disabled?: boolean;
  compact?: boolean;
};

export function Button({ title, onPress, variant = 'primary', icon, leading, loading, disabled, compact }: Props) {
  const styles = useStyles(makeStyles);
  const v = variantsOf(usePalette())[variant];
  const inactive = disabled || loading;
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ disabled: !!inactive, busy: !!loading }}
      onPress={onPress}
      disabled={inactive}
      style={({ pressed }) => [
        styles.base,
        compact && styles.compact,
        { backgroundColor: v.bg, borderColor: v.border },
        pressed && { opacity: 0.85 },
        disabled && { opacity: 0.45 },
      ]}>
      {loading ? (
        <ActivityIndicator color={v.fg} />
      ) : (
        <View style={styles.row}>
          {leading}
          {icon ? <Feather name={icon} size={17} color={v.fg} /> : null}
          <Text style={[styles.label, { color: v.fg }]}>{title}</Text>
        </View>
      )}
    </Pressable>
  );
}

const variantsOf = (colors: Palette): Record<Variant, { bg: string; fg: string; border: string }> => ({
  // On the black student side the main action is the mint pill; on the wallpaper, the white one.
  primary: colors.wallpaper
    ? { bg: colors.ink, fg: colors.pillText, border: colors.ink }
    : { bg: colors.accent, fg: colors.pillText, border: colors.accent },
  secondary: { bg: colors.white, fg: colors.ink, border: colors.line },
  accent: { bg: colors.accent, fg: colors.pillText, border: colors.accent },
  danger: { bg: colors.garnet, fg: colors.pillText, border: colors.garnet },
  // A second action that still invites a tap: green words on a mint wash.
  soft: { bg: colors.accentTint, fg: colors.accentDeep, border: colors.accentTint },
});

const makeStyles = (colors: Palette) => StyleSheet.create({
  base: {
    height: sizes.button,
    borderRadius: radius.md,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 18,
  },
  compact: { flex: 1, height: 48 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  label: { fontFamily: fonts.bold, fontSize: 15.5 },
});
