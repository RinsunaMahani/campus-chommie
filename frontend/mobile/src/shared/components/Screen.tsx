import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { ReactNode, useState } from 'react';
import { Animated, Image, ImageSourcePropType, KeyboardAvoidingView, Platform, Pressable, RefreshControl, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Wallpaper } from './Wallpaper';

import { fonts, radius, space, type } from '@/shared/theme/tokens';
import { forest, Palette, PaletteProvider, usePalette, useStyles } from '@/shared/theme/palette';

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
  /** Above the title on the right: a tag (the demo tag). */
  headerRight?: ReactNode;
  /** On the title's line, at the right: one small action (the Help button). */
  titleAside?: ReactNode;
  /**
   * Daylight paper's hero area: the header (tag, title, Help) on a band of Rinsuna's wallpaper, edge to edge with
   * a rounded bottom, in white words (the forest palette inside). With a backdrop, the band shows the photo instead.
   */
  hero?: boolean;
  /** Hero only: a small line above the title (today's date). */
  overline?: string;
  /** Hero only: under the title, on the band (the university). */
  band?: ReactNode;
};

/** How far the page scrolls before the slim title bar has fully faded in. */
const COLLAPSE_AT = 44;

/**
 * The page every screen sits on: the wallpaper, safe areas, keyboard that
 * never hides the field you're typing in, and an action pinned at the
 * bottom where the thumb is. A tab screen leaves room under its content for
 * the floating dock.
 */
export function Screen({ children, footer, back, tab, onRefresh, refreshing = false, backdrop, title, subtitle, headerRight, titleAside, hero, overline, band }: Props) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const [scrollY] = useState(() => new Animated.Value(0));
  const barOpacity = scrollY.interpolate({ inputRange: [COLLAPSE_AT * 0.5, COLLAPSE_AT], outputRange: [0, 1], extrapolate: 'clamp' });
  const isHero = !!(hero && title);
  const head = title ? (
    <Head
      title={title}
      subtitle={subtitle}
      back={back}
      headerRight={headerRight}
      titleAside={titleAside}
      overline={isHero ? overline : undefined}
      band={isHero ? band : undefined}
      onBand={isHero}
    />
  ) : null;
  return (
    <View style={styles.root}>
      <Wallpaper />
      {backdrop && !isHero ? (
        <View style={styles.backdrop}>
          <Image source={backdrop} style={styles.photo} resizeMode="cover" accessible={false} accessibilityIgnoresInvertColors />
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
          {isHero ? (
            <PaletteProvider palette={forest}>
              <View style={styles.hero}>
                {backdrop ? (
                  <View style={[StyleSheet.absoluteFill, { pointerEvents: 'none' }]}>
                    <Image source={backdrop} style={styles.photo} resizeMode="cover" accessible={false} accessibilityIgnoresInvertColors />
                    {/* 0.55 black keeps white words above 4.5:1 on a bright sky. */}
                    <View style={[StyleSheet.absoluteFill, { backgroundColor: 'rgba(0, 0, 0, 0.55)' }]} />
                  </View>
                ) : (
                  <Wallpaper />
                )}
                {head}
              </View>
            </PaletteProvider>
          ) : (
            head
          )}
          {children}
        </Animated.ScrollView>
        {title ? (
          <Animated.View
            style={[styles.bar, { opacity: barOpacity }]}
            importantForAccessibility="no-hide-descendants">
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

/** The large title and what sits around it; under the palette it's drawn in (paper, or forest on a hero band). */
function Head({
  title,
  subtitle,
  back,
  headerRight,
  titleAside,
  overline,
  band,
  onBand,
}: Pick<Props, 'subtitle' | 'back' | 'headerRight' | 'titleAside' | 'overline' | 'band'> & { title: string; onBand: boolean }) {
  const styles = useStyles(makeStyles);
  return (
    <View style={styles.head}>
      {back || headerRight ? (
        <View style={styles.headRow}>
          {back ? <BackButton /> : <View />}
          {headerRight}
        </View>
      ) : null}
      {overline ? <Text style={styles.overline}>{overline}</Text> : null}
      <View style={styles.titleRow}>
        <Text style={[styles.largeTitle, onBand && styles.onBand, { flex: 1 }]} accessibilityRole="header">
          {title}
        </Text>
        {titleAside}
      </View>
      {subtitle ? <Text style={[styles.subtitle, onBand && styles.onBandSoft]}>{subtitle}</Text> : null}
      {band}
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
  // pointerEvents in style: the prop is deprecated on the web.
  backdrop: { position: 'absolute', top: 0, left: 0, right: 0, height: BACKDROP_HEIGHT, pointerEvents: 'none' },
  // Width and height spelled out: a bundled image carries its own size, which would win over insets alone.
  photo: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' },
  root: { flex: 1, backgroundColor: colors.porcelain },
  safe: { flex: 1 },
  flex: { flex: 1 },
  head: { gap: space.xs },
  headRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: space.sm },
  titleRow: { flexDirection: 'row', alignItems: 'center', gap: space.md },
  largeTitle: { fontFamily: fonts.display, ...type.largeTitle, letterSpacing: -0.6, color: colors.ink },
  subtitle: { fontFamily: fonts.medium, ...type.callout, color: colors.textMuted },
  overline: { fontFamily: fonts.semibold, ...type.callout, color: colors.onAccentSoft },
  onBand: { color: colors.onAccent },
  onBandSoft: { color: colors.onAccentSoft },
  // The band reaches past the page's side and top padding to the screen's edges.
  hero: {
    overflow: 'hidden',
    marginHorizontal: -20,
    marginTop: -space.md,
    paddingHorizontal: 20,
    paddingTop: space.md,
    paddingBottom: space.xl,
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
  },
  // The slim bar: the title again, once the large one has scrolled away.
  bar: {
    pointerEvents: 'none',
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
