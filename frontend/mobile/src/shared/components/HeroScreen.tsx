/**
 * A screen that opens on a violet band: where you are and what the screen is
 * for, in white, then the content on porcelain, rising into place. The main
 * action stays pinned at the bottom, as on every screen. The status bar turns
 * light over the band while the screen is open.
 */
import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { ReactNode } from 'react';
import { KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { FadeIn } from '@/shared/motion/FadeIn';
import { colors, fonts, radius, space } from '@/shared/theme/tokens';

type Props = {
  title: string;
  subtitle?: string;
  overline?: string;
  back?: boolean;
  /** Under the title, on the band: chips, say. */
  band?: ReactNode;
  footer?: ReactNode;
  children: ReactNode;
};

export function HeroScreen({ title, subtitle, overline, back, band, footer, children }: Props) {
  const insets = useSafeAreaInsets();
  return (
    <View style={styles.root}>
      <StatusBar style="light" />
      <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView
          style={styles.flex}
          contentContainerStyle={{ paddingBottom: footer ? space.xl : insets.bottom + space.xl }}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}>
          <LinearGradient
            colors={[colors.accent, colors.accentDeep]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={[styles.band, { paddingTop: insets.top + space.md }]}>
            {back ? <BandBack /> : null}
            <View style={{ gap: 6 }}>
              {overline ? <Text style={styles.overline}>{overline}</Text> : null}
              <Text accessibilityRole="header" style={styles.title}>
                {title}
              </Text>
              {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
            </View>
            {band}
          </LinearGradient>
          <FadeIn style={styles.content}>{children}</FadeIn>
        </ScrollView>
        {footer ? <View style={[styles.footer, { paddingBottom: insets.bottom + space.md }]}>{footer}</View> : null}
      </KeyboardAvoidingView>
    </View>
  );
}

function BandBack() {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel="Back"
      hitSlop={8}
      onPress={() => (router.canGoBack() ? router.back() : router.replace('/'))}
      style={styles.back}>
      <Feather name="chevron-left" size={24} color={colors.onAccent} />
    </Pressable>
  );
}

/** A small rounded label on the band. */
export function BandChip({ label }: { label: string }) {
  return (
    <View style={styles.chip}>
      <Text style={styles.chipText}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.porcelain },
  flex: { flex: 1 },
  band: {
    paddingHorizontal: 20,
    paddingBottom: space.xl,
    gap: space.md,
    borderBottomLeftRadius: radius.xl,
    borderBottomRightRadius: radius.xl,
  },
  // 44 px with its slop: a comfortable thumb target.
  back: { width: 40, height: 40, borderRadius: 20, backgroundColor: colors.onAccentTint, alignItems: 'center', justifyContent: 'center' },
  overline: { fontFamily: fonts.bold, fontSize: 12, letterSpacing: 0.8, textTransform: 'uppercase', color: colors.onAccentSoft },
  title: { fontFamily: fonts.display, fontSize: 26, lineHeight: 32, letterSpacing: -0.4, color: colors.onAccent },
  subtitle: { fontFamily: fonts.medium, fontSize: 14.5, lineHeight: 21, color: colors.onAccentSoft },
  chip: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: radius.pill, backgroundColor: colors.onAccentTint, alignSelf: 'flex-start' },
  chipText: { fontFamily: fonts.semibold, fontSize: 12.5, color: colors.onAccent },
  content: { paddingHorizontal: 20, paddingTop: space.lg, gap: space.lg },
  footer: { paddingHorizontal: 20, paddingTop: space.sm, gap: space.md, backgroundColor: colors.porcelain },
});
