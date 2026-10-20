import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { ReactNode } from 'react';
import { Image, ImageSourcePropType, KeyboardAvoidingView, Platform, Pressable, RefreshControl, ScrollView, StyleSheet, View } from 'react-native';
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
  /** A photo behind the top of the page (the student's campus), fading into the background. */
  backdrop?: ImageSourcePropType;
};

/**
 * The page every screen sits on: the wallpaper, safe areas, keyboard that
 * never hides the field you're typing in, and an action pinned at the
 * bottom where the thumb is. A tab screen leaves room under its content for
 * the floating dock.
 */
export function Screen({ children, footer, back, tab, onRefresh, refreshing = false, backdrop }: Props) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  return (
    <View style={styles.root}>
      <Wallpaper />
      {backdrop ? (
        <View style={styles.backdrop} pointerEvents="none">
          <Image source={backdrop} style={StyleSheet.absoluteFill} resizeMode="cover" accessible={false} accessibilityIgnoresInvertColors />
          {/* Darker at the top for the title, then into the page colour, so the cards read on it. */}
          <LinearGradient
            colors={['rgba(0,0,0,0.45)', 'rgba(0,0,0,0.25)', colors.page]}
            locations={[0, 0.45, 1]}
            style={StyleSheet.absoluteFill}
          />
        </View>
      ) : null}
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

/** How tall the campus photo behind a page's top is. */
export const BACKDROP_HEIGHT = 380;

// The floating dock's height and the gap under it, so the last card isn't hidden behind it.
export const DOCK_ROOM = 112;

const makeStyles = (colors: Palette) => StyleSheet.create({
  backdrop: { position: 'absolute', top: 0, left: 0, right: 0, height: BACKDROP_HEIGHT },
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
