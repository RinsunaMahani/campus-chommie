/**
 * A screen that opens on a photo (Daylight paper): the photo edge to edge at the top, under the status bar, with
 * its credit on it and a round back button (and one optional round action on the right); then the paper page
 * rising over the photo with a rounded top, carrying the screen's head and its content. A photo's credit opens
 * its source page (author, licence, the original). Without a photo, the top is a short band of Rinsuna's
 * wallpaper instead, so a page never shows a stock picture that says nothing about it.
 */
import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { ComponentProps, ReactNode } from 'react';
import { Image, ImageSourcePropType, KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { FadeIn } from '@/shared/motion/FadeIn';
import { forest, Palette, PaletteProvider, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius, space } from '@/shared/theme/tokens';

import { Wallpaper } from './Wallpaper';

export type HeroPhoto = {
  image: ImageSourcePropType;
  /** What it shows ("Ruth First Hall, Soshanguve South campus"), read out and shown before the credit. */
  caption?: string;
  /** "author, licence, Wikimedia Commons (cropped)" */
  credit: string;
  source: string;
};

type Props = {
  photo?: HeroPhoto | null;
  /** One round action on the photo's right (Save). */
  action?: { icon: ComponentProps<typeof Feather>['name']; label: string; on?: boolean; onPress: () => void };
  /** The top of the page: overline, title, chips. */
  head?: ReactNode;
  footer?: ReactNode;
  children: ReactNode;
};

/** How tall the photo is under the status bar. */
const PHOTO_HEIGHT = 230;
/** How far the page rises over the photo. */
const OVERLAP = 26;

export function PhotoHero({ photo, action, head, footer, children }: Props) {
  const styles = useStyles(makeStyles);
  const insets = useSafeAreaInsets();
  return (
    <View style={styles.root}>
      <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView
          style={styles.flex}
          contentContainerStyle={{ paddingBottom: footer ? space.xl : insets.bottom + space.xl }}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}>
          <View style={{ height: (photo ? PHOTO_HEIGHT : 64) + insets.top + OVERLAP }}>
            {photo ? (
              <Image
                source={photo.image}
                style={styles.photo}
                resizeMode="cover"
                accessibilityRole="image"
                accessibilityLabel={photo.caption}
                accessibilityIgnoresInvertColors
              />
            ) : (
              <PaletteProvider palette={forest}>
                <Wallpaper />
              </PaletteProvider>
            )}
            <View style={[styles.buttons, { top: insets.top + space.sm }]}>
              <RoundButton icon="chevron-left" label="Back" onPress={() => (router.canGoBack() ? router.back() : router.replace('/'))} />
              {action ? <RoundButton icon={action.icon} label={action.label} on={action.on} onPress={action.onPress} /> : null}
            </View>
          </View>
          <View style={styles.sheet}>
            {head ? <View style={styles.head}>{head}</View> : null}
            <FadeIn style={styles.content}>{children}</FadeIn>
          </View>
        </ScrollView>
        {footer ? <View style={[styles.footer, { paddingBottom: insets.bottom + space.md }]}>{footer}</View> : null}
      </KeyboardAvoidingView>
    </View>
  );
}

/** A white circle on the photo: easy to see on any picture, 44 px with its slop. */
function RoundButton({ icon, label, on, onPress }: { icon: ComponentProps<typeof Feather>['name']; label: string; on?: boolean; onPress: () => void }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={label}
      accessibilityState={on === undefined ? undefined : { selected: on }}
      hitSlop={6}
      onPress={onPress}
      style={[styles.round, on && styles.roundOn]}>
      <Feather name={icon} size={20} color={on ? colors.pillText : colors.ink} />
    </Pressable>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    root: { flex: 1, backgroundColor: colors.porcelain },
    flex: { flex: 1 },
    // Width and height spelled out: a bundled image carries its own size, which would win over insets alone.
    photo: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' },
    buttons: { position: 'absolute', left: 16, right: 16, flexDirection: 'row', justifyContent: 'space-between' },
    round: {
      width: 40,
      height: 40,
      borderRadius: 20,
      backgroundColor: colors.white,
      alignItems: 'center',
      justifyContent: 'center',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.18)',
    },
    roundOn: { backgroundColor: colors.accent },
    // The credit sits on a dark pill, so it reads on any photo.
    credit: { position: 'absolute', right: 12, maxWidth: '86%', borderRadius: radius.sm, backgroundColor: 'rgba(0, 0, 0, 0.6)', paddingHorizontal: 8, paddingVertical: 3 },
    creditText: { fontFamily: fonts.medium, fontSize: 11.5, lineHeight: 15, color: '#FFFFFF' },
    sheet: { marginTop: -OVERLAP, borderTopLeftRadius: 28, borderTopRightRadius: 28, backgroundColor: colors.porcelain },
    head: { paddingHorizontal: 20, paddingTop: space.lg, gap: space.sm },
    content: { paddingHorizontal: 20, paddingTop: space.lg, gap: space.lg },
    footer: { paddingHorizontal: 20, paddingTop: space.sm, gap: space.md },
  });
