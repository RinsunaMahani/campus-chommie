import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { ReactNode } from 'react';
import { KeyboardAvoidingView, Platform, Pressable, RefreshControl, ScrollView, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Wallpaper } from './Wallpaper';

import { radius, space } from '@/shared/theme/tokens';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';

type Props = {
  children: ReactNode;
  /** Pinned under the content: the main action. */
  footer?: ReactNode;
  back?: boolean;
  /** Tab screens: the tab bar already covers the bottom inset. */
  tab?: boolean;
  /** Pull down to refresh (only screens that pass it). */
  onRefresh?: () => void;
  refreshing?: boolean;
};

/**
 * The page every screen sits on: the wallpaper, safe areas, keyboard that
 * never hides the field you're typing in, and an action pinned at the
 * bottom where the thumb is. A tab screen leaves room under its content for
 * the floating dock.
 */
export function Screen({ children, footer, back, tab, onRefresh, refreshing = false }: Props) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  return (
    <View style={styles.root}>
      <Wallpaper />
      <SafeAreaView style={styles.safe} edges={tab ? ['top'] : ['top', 'bottom']}>
      <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView
          style={styles.flex}
          contentContainerStyle={[styles.content, tab && { paddingBottom: DOCK_ROOM }]}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
          refreshControl={onRefresh ? <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.ink} /> : undefined}>
          {back ? <BackButton /> : null}
          {children}
        </ScrollView>
        {footer ? <View style={styles.footer}>{footer}</View> : null}
      </KeyboardAvoidingView>
      </SafeAreaView>
    </View>
  );
}

export function BackButton({ onPress }: { onPress?: () => void }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel="Back"
      hitSlop={8}
      onPress={onPress ?? (() => (router.canGoBack() ? router.back() : router.replace('/')))}
      style={styles.back}>
      <Feather name="chevron-left" size={26} color={colors.ink} />
    </Pressable>
  );
}

// The floating dock's height and the gap under it, so the last card isn't hidden behind it.
export const DOCK_ROOM = 112;

const makeStyles = (colors: Palette) => StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.porcelain },
  safe: { flex: 1 },
  flex: { flex: 1 },
  content: { paddingHorizontal: 20, paddingTop: space.md, paddingBottom: space.xl, gap: space.lg },
  footer: { paddingHorizontal: 20, paddingTop: space.sm, paddingBottom: space.md, gap: space.md },
  // 44 px: the minimum comfortable thumb target.
  back: {
    width: 44,
    height: 44,
    borderRadius: radius.sm,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.white,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
