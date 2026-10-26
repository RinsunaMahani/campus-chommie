/**
 * A place's photos, one at a time, full width: swipe through them, or let them move on by themselves every few
 * seconds until you touch them (never with reduced motion). Dots and "Photo 2 of 4" say where you are; each photo's
 * caption and credit sit under it, the credit opening its Commons page.
 */
import { useEffect, useRef, useState } from 'react';
import { Image, LayoutChangeEvent, NativeScrollEvent, NativeSyntheticEvent, ScrollView, StyleSheet, Text, View } from 'react-native';

import { PhotoCredit } from '@/features/courseFinder/components/CampusPhotoCard';
import { t } from '@/shared/i18n';
import { motionOff } from '@/shared/motion/motion';
import { Palette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import { PlacePhoto } from '../placePhotos';

export const ADVANCE_MS = 4000;

export function PhotoSlideshow({ photos, place }: { photos: PlacePhoto[]; place: string }) {
  const styles = useStyles(makeStyles);
  const scroller = useRef<ScrollView>(null);
  const [width, setWidth] = useState(0);
  const [index, setIndex] = useState(0);
  const [touched, setTouched] = useState(false);

  // Moves on by itself until the student swipes, and never when the phone asks for less motion.
  useEffect(() => {
    if (touched || motionOff() || !width || photos.length < 2) return;
    const timer = setInterval(() => {
      setIndex((i) => {
        const next = (i + 1) % photos.length;
        scroller.current?.scrollTo({ x: next * width, animated: true });
        return next;
      });
    }, ADVANCE_MS);
    return () => clearInterval(timer);
  }, [touched, width, photos.length]);

  const onLayout = (e: LayoutChangeEvent) => setWidth(e.nativeEvent.layout.width);
  const onSettle = (e: NativeSyntheticEvent<NativeScrollEvent>) => {
    if (width) setIndex(Math.round(e.nativeEvent.contentOffset.x / width));
  };
  const photo = photos[Math.min(index, photos.length - 1)];

  return (
    <View style={{ gap: 8 }}>
      <View style={styles.frame} onLayout={onLayout} testID="slideshow-frame">
        {width ? (
          <ScrollView
            ref={scroller}
            horizontal
            pagingEnabled
            style={{ height: Math.round((width * 9) / 16) }}
            showsHorizontalScrollIndicator={false}
            onScrollBeginDrag={() => setTouched(true)}
            onMomentumScrollEnd={onSettle}
            accessibilityLabel={t('outdoors.photos', { place })}>
            {photos.map((p, i) => (
              <Image
                key={p.source}
                source={p.image}
                // An explicit height: inside a horizontal scroll, the web ignores aspectRatio and shows the photo tall.
                style={{ width, height: Math.round((width * 9) / 16) }}
                resizeMode="cover"
                accessible
                accessibilityLabel={`${t('outdoors.photoOf', { n: i + 1, total: photos.length })}: ${p.caption}`}
              />
            ))}
          </ScrollView>
        ) : (
          <View style={{ aspectRatio: 16 / 9 }} />
        )}
        <View style={styles.count} importantForAccessibility="no-hide-descendants" accessibilityElementsHidden>
          <Text style={styles.countText}>
            {index + 1} / {photos.length}
          </Text>
        </View>
      </View>

      <View style={styles.dots} importantForAccessibility="no-hide-descendants" accessibilityElementsHidden>
        {photos.map((p, i) => (
          <View key={p.source} style={[styles.dot, i === index && styles.dotOn]} />
        ))}
      </View>
      <Text style={styles.caption}>{photo.caption}</Text>
      <PhotoCredit credit={photo.credit} source={photo.source} />
    </View>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    frame: { borderRadius: radius.lg, overflow: 'hidden', backgroundColor: colors.iconTile },
    count: {
      position: 'absolute',
      right: 10,
      bottom: 10,
      paddingHorizontal: 9,
      paddingVertical: 3,
      borderRadius: radius.pill,
      backgroundColor: colors.overlay,
    },
    countText: { fontFamily: fonts.bold, fontSize: 12, color: colors.onAccent },
    dots: { flexDirection: 'row', justifyContent: 'center', gap: 6 },
    dot: { width: 7, height: 7, borderRadius: 4, backgroundColor: colors.line },
    dotOn: { width: 22, backgroundColor: colors.accent },
    caption: { fontFamily: fonts.semibold, fontSize: 14.5, lineHeight: 19, color: colors.ink },
  });
