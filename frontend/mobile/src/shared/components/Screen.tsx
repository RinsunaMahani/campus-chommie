import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { ReactNode, useState } from 'react';
import { Animated, Image, ImageSourcePropType, KeyboardAvoidingView, Platform, Pressable, RefreshControl, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Wallpaper } from './Wallpaper';

import { fonts, radius, space, type } from '@/shared/theme/tokens';
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
  /** The screen's name as a large title; it shrinks into a slim bar at the top once scrolled past. */
  title?: string;
  /** One short line under the title. */
  subtitle?: string;
  /** Beside the title on the right: one small action (a tag, a help button). */
  headerRight?: ReactNode;
};

/** How far the page scrolls before the slim title bar has fully faded in. */
const COLLAPSE_AT = 44;

/**
 * The page every screen sits on: the wallpaper, safe areas, keyboard that
 * never hides the field you're typing in, and an action pinned at the
 * bottom where the thumb is. A tab screen leaves room under its content for
 * the floating dock.
 */
export function Screen({ children, footer, back, tab, onRefresh, refreshing = false, backdrop, title, subtitle, headerRight }: Props) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const [scrollY] = useState(() => new Animated.Value(0));
  const barOpacity = scrollY.interpolate({ inputRange: [COLLAPSE_AT * 0.5, COLLAPSE_AT], outputRange: [0, 1], extrapolate: 'clamp' });
  return (
    <View style={styles.root}>
      <Wallpaper />
      {backdrop ? (
        <View style={styles.backdrop} pointerEvents="none">
          <Image source={backdrop} style={StyleSheet.absoluteFill} resizeMode="cover" accessible={false} accessibilityIgnoresInvertColors />
          {/* Darker at the top for the title, then into the page colour, so the cards read on it. */}
          {/* Text-over-photo guidance: darken where the text sits (the top), check the lightest spot, then fade
              into the page. 0.6 black under the title keeps white text above 4.5:1 on a bright sky. */}
          <LinearGradient
            colors={['rgba(0,0,0,0.6)', 'rgba(0,0,0,0.3)', colors.page]}
            locations={[0, 0.45, 1]}
            style={StyleSheet.absoluteFill}
          />
        </View>
      ) : null}
      <SafeAreaView style={styles.safe} edges={tab ? ['top'] : ['top', 'bottom']}>
      <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <Animated.ScrollView
          style={styles.flex}
          scrollEventThrottle={16}
          onScroll={title ? Animated.event([{ nativeEvent: { contentOffset: { y: scrollY } } }], { useNativeDriver: true }) : undefined}
          contentContainerStyle={[styles.content, tab && { paddingBottom: DOCK_ROOM }]}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
          refreshControl={onRefresh ? <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.ink} /> : undefined}>
          {back && !title ? <BackButton /> : null}
          {title ? (
            <View style={styles.head}>
              {back || headerRight ? (
                <View style={styles.headRow}>
                  {back ? <BackButton /> : <View />}
                  {headerRight}
                </View>
              ) : null}
              <Text style={styles.largeTitle} accessibilityRole="header">
                {title}
              </Text>
              {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
            </View>
          ) : null}
          {children}
        </Animated.ScrollView>
        {title ? (
          <Animated.View style={[styles.bar, { opacity: barOpacity }]} pointerEvents="none" importantForAccessibility="no-hide-descendants">
            <Text style={styles.barTitle} numberOfLines={1}>
              {title}
            </Text>
          </Animated.View>
        ) : null}
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
  head: { gap: space.xs },
  headRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: space.sm },
  largeTitle: { fontFamily: fonts.display, ...type.largeTitle, letterSpacing: -0.6, color: colors.ink },
  subtitle: { fontFamily: fonts.medium, ...type.callout, color: colors.textMuted },
  // The slim bar: the title again, once the large one has scrolled away.
  bar: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    paddingHorizontal: 20,
    paddingVertical: space.md,
    backgroundColor: colors.page,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.line,
  },
  barTitle: { fontFamily: fonts.bold, ...type.headline, color: colors.ink, textAlign: 'center' },
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
