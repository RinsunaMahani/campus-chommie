/**
 * Outdoors, opened from the centre button of the tab bar: a sheet that slides up over whatever screen you're on,
 * like YouTube's and Standard Bank's centre buttons. It lists the free and cheap places near your campus; tap one
 * and the sheet previews it (what, cost, hours, where, Open in maps). Tap outside, the handle or Close to put it
 * away; "See all" opens the full list. With reduced motion it appears at once.
 */
import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useEffect, useMemo, useState } from 'react';
import { Animated, Pressable, ScrollView, StyleSheet, Text, useWindowDimensions, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { moneyApi } from '@/features/money/api/moneyApi';
import { CheapThing } from '@/features/money/types';
import { errorText } from '@/shared/api/errors';
import { IconTile } from '@/shared/components/Parts';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Body, Muted } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { EASE_OUT, motionOff, NATIVE } from '@/shared/motion/motion';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius, space, type } from '@/shared/theme/tokens';

import { PlacePreview } from '../components/PlacePreview';
import { categoryIcon, categoryLabel } from '../places';

export default function OutdoorsSheet() {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const insets = useSafeAreaInsets();
  const { height } = useWindowDimensions();
  const [places, setPlaces] = useState<CheapThing[] | null>(null);
  const [failure, setFailure] = useState<string | null>(null);
  const [chosen, setChosen] = useState<CheapThing | null>(null);
  const [filter, setFilter] = useState('all');
  const [rise] = useState(() => new Animated.Value(motionOff() ? 1 : 0));

  useEffect(() => {
    if (!motionOff()) Animated.timing(rise, { toValue: 1, duration: 260, easing: EASE_OUT, useNativeDriver: NATIVE }).start();
    moneyApi
      .cheapThings()
      .then((a) => setPlaces(a.cheap_things))
      .catch((e) => setFailure(errorText(e, t('common.error'))));
  }, [rise]);

  const close = () => {
    const leave = () => (router.canGoBack() ? router.back() : router.replace('/home'));
    if (motionOff()) return leave();
    Animated.timing(rise, { toValue: 0, duration: 180, easing: EASE_OUT, useNativeDriver: NATIVE }).start(leave);
  };

  const categories = useMemo(() => Array.from(new Set((places ?? []).map((p) => p.category).filter(Boolean))), [places]);
  const shown = (places ?? []).filter((p) => filter === 'all' || p.category === filter);
  const translateY = rise.interpolate({ inputRange: [0, 1], outputRange: [height * 0.6, 0] });

  return (
    <View style={StyleSheet.absoluteFill}>
      <Animated.View style={[StyleSheet.absoluteFill, { backgroundColor: colors.overlay, opacity: rise }]}>
        <Pressable style={StyleSheet.absoluteFill} onPress={close} accessibilityRole="button" accessibilityLabel={t('outdoors.close')} />
      </Animated.View>

      <Animated.View
        accessibilityViewIsModal
        style={[styles.sheet, { maxHeight: height * 0.86, paddingBottom: space.lg + insets.bottom, transform: [{ translateY }] }]}>
        <Pressable onPress={close} accessibilityRole="button" accessibilityLabel={t('outdoors.close')} style={styles.handleHit}>
          <View style={styles.handle} />
        </Pressable>

        <View style={styles.header}>
          {chosen ? (
            <Pressable onPress={() => setChosen(null)} accessibilityRole="button" accessibilityLabel={t('outdoors.backToPlaces')} hitSlop={8} style={styles.round}>
              <Feather name="arrow-left" size={20} color={colors.ink} />
            </Pressable>
          ) : null}
          <View style={{ flex: 1 }}>
            <Text style={styles.title} accessibilityRole="header">
              {chosen ? t('outdoors.preview') : t('outdoors.title')}
            </Text>
            {!chosen ? <Muted>{t('outdoors.sub')}</Muted> : null}
          </View>
          <Pressable onPress={close} accessibilityRole="button" accessibilityLabel={t('outdoors.close')} hitSlop={8} style={styles.round}>
            <Feather name="x" size={20} color={colors.ink} />
          </Pressable>
        </View>

        <ScrollView contentContainerStyle={{ gap: space.md, paddingBottom: space.sm }} showsVerticalScrollIndicator={false}>
          {failure ? <ErrorBox message={failure} /> : null}
          {!places && !failure ? <Loading /> : null}

          {chosen ? (
            <PlacePreview place={chosen} />
          ) : places ? (
            <>
              {categories.length > 1 ? (
                <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chips}>
                  {['all', ...categories].map((c) => {
                    const on = filter === c;
                    return (
                      <Pressable
                        key={c}
                        accessibilityRole="button"
                        accessibilityState={{ selected: on }}
                        onPress={() => setFilter(c)}
                        style={[styles.chip, on && styles.chipOn]}>
                        <Text style={[styles.chipText, on && styles.chipTextOn]}>{c === 'all' ? t('outdoors.all') : categoryLabel(c)}</Text>
                      </Pressable>
                    );
                  })}
                </ScrollView>
              ) : null}

              {shown.length ? (
                shown.map((p, i) => (
                  <Pressable
                    key={`${p.name}-${i}`}
                    accessibilityRole="button"
                    accessibilityLabel={`${p.name}. ${categoryLabel(p.category)}`}
                    accessibilityHint={t('outdoors.previewHint')}
                    onPress={() => setChosen(p)}
                    style={({ pressed }) => [styles.place, pressed && { opacity: 0.8 }]}>
                    <IconTile name={categoryIcon(p.category)} size={44} />
                    <View style={{ flex: 1, gap: 2 }}>
                      <Text style={styles.placeName} numberOfLines={2}>
                        {p.name}
                      </Text>
                      <Text style={styles.placeMeta} numberOfLines={1}>
                        {[categoryLabel(p.category), p.cost_note].filter(Boolean).join(' · ')}
                      </Text>
                    </View>
                    <Feather name="chevron-right" size={20} color={colors.textFaint} />
                  </Pressable>
                ))
              ) : (
                <View style={styles.empty}>
                  <IconTile name="sun" size={48} />
                  <Body>{t('cheap.none')}</Body>
                </View>
              )}

              {places.length ? (
                <Pressable
                  accessibilityRole="link"
                  onPress={() => router.replace('/money/cheap-things')}
                  style={styles.seeAll}>
                  <Text style={styles.seeAllText}>{t('outdoors.seeAll')}</Text>
                </Pressable>
              ) : null}
            </>
          ) : null}
        </ScrollView>
      </Animated.View>
    </View>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    sheet: {
      position: 'absolute',
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: colors.white,
      borderTopLeftRadius: radius.xl,
      borderTopRightRadius: radius.xl,
      borderWidth: 1,
      borderColor: colors.line,
      paddingHorizontal: space.lg + 4,
      gap: space.md,
    },
    handleHit: { alignSelf: 'center', paddingTop: space.sm, paddingBottom: 2, paddingHorizontal: space.xl },
    handle: { width: 44, height: 5, borderRadius: 3, backgroundColor: colors.line },
    header: { flexDirection: 'row', alignItems: 'center', gap: space.md },
    title: { fontFamily: fonts.bold, ...type.title, color: colors.ink },
    round: {
      width: 36,
      height: 36,
      borderRadius: 18,
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: colors.porcelain,
    },
    chips: { gap: space.sm, paddingVertical: 2 },
    chip: {
      paddingHorizontal: 14,
      paddingVertical: 8,
      borderRadius: radius.pill,
      borderWidth: 1,
      borderColor: colors.line,
      backgroundColor: colors.white,
    },
    chipOn: { backgroundColor: colors.ink, borderColor: colors.ink },
    chipText: { fontFamily: fonts.semibold, fontSize: 14, color: colors.ink },
    chipTextOn: { color: colors.pillText },
    place: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: space.md,
      padding: space.md,
      borderRadius: radius.md,
      borderWidth: 1,
      borderColor: colors.line,
      backgroundColor: colors.white,
    },
    placeName: { fontFamily: fonts.bold, ...type.callout, color: colors.ink },
    placeMeta: { fontFamily: fonts.medium, ...type.caption, color: colors.textMuted },
    empty: { alignItems: 'center', gap: space.sm, paddingVertical: space.lg },
    seeAll: { alignSelf: 'center', paddingVertical: space.sm, paddingHorizontal: space.lg },
    seeAllText: { fontFamily: fonts.bold, fontSize: 15, color: colors.accentDeep },
  });
