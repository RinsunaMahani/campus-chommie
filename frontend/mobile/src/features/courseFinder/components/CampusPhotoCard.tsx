/**
 * A real photo of the university's campus at the top of its page, with what it
 * shows and its credit. Tapping the credit opens the photo's Commons page
 * (author, licence, the original). Nothing for a university without a photo:
 * its monogram stays in the lists.
 */
import { Image, StyleSheet, Text, View } from 'react-native';

import { Palette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import { CAMPUS_PHOTOS } from '../campusPhotos';

export function CampusPhotoCard({ university }: { university: string }) {
  const styles = useStyles(makeStyles);
  const photo = CAMPUS_PHOTOS[university];
  if (!photo) return null;
  return (
    <View style={styles.card}>
      <Image
        source={photo.image}
        style={styles.image}
        resizeMode="cover"
        accessibilityRole="image"
        accessibilityLabel={photo.caption}
        accessibilityIgnoresInvertColors
      />
      <View style={styles.words}>
        <Text style={styles.caption}>{photo.caption}</Text>
      </View>
    </View>
  );
}


const makeStyles = (colors: Palette) =>
  StyleSheet.create({
  card: {
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.white,
    overflow: 'hidden',
  },
  image: { width: '100%', aspectRatio: 16 / 9 },
  words: { gap: 2, paddingHorizontal: 14, paddingVertical: 10 },
  caption: { fontFamily: fonts.semibold, fontSize: 14.5, lineHeight: 19, color: colors.ink },
  credit: { fontFamily: fonts.body, fontSize: 11, lineHeight: 16, color: colors.textFaint, textDecorationLine: 'underline' },
});
