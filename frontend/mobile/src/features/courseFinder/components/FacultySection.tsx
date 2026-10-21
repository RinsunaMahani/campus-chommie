/**
 * One faculty's programmes in the Courses tab: a header with the faculty's
 * picture, its name and its counts in words, which opens to the programme
 * cards. A field's photo (openly licensed, credited) where we have one, else
 * an icon on glass.
 */
import { Feather } from '@expo/vector-icons';
import { ComponentProps, ReactNode, useState } from 'react';
import { ImageBackground, Pressable, StyleSheet, Text, View } from 'react-native';

import { t } from '@/shared/i18n';
import { FadeIn } from '@/shared/motion/FadeIn';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import { Art, FacultyGroup } from '../faculties';
import { PHOTOS } from '../facultyPhotos';
import { PhotoCredit } from './CampusPhotoCard';

const ICONS: Record<Art, ComponentProps<typeof Feather>['name']> = {
  health: 'heart',
  engineering: 'tool',
  computing: 'monitor',
  commerce: 'bar-chart-2',
  law: 'briefcase',
  education: 'edit-3',
  science: 'aperture',
  agriculture: 'sun',
  arts: 'feather',
  humanities: 'book',
  hospitality: 'coffee',
  sport: 'award',
  other: 'layers',
};

/** "6 meet the minimum · 2 reach · 12 programmes", in words, never colour alone. */
export function facultyCounts(g: FacultyGroup): string {
  const parts: string[] = [];
  if (g.meets) parts.push(t('courseFinder.facultyMeets', { n: g.meets }));
  if (g.reach) parts.push(t('courseFinder.facultyReach', { n: g.reach }));
  const n = g.matches.length;
  parts.push(n === 1 ? t('courseFinder.facultyCountOne') : t('courseFinder.facultyCount', { n }));
  return parts.join(' · ');
}

type Props = { group: FacultyGroup; startOpen: boolean; children: ReactNode };

export function FacultySection({ group, startOpen, children }: Props) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const [open, setOpen] = useState(startOpen);
  const name = group.faculty ?? t('courseFinder.otherFaculty');
  const photo = PHOTOS[group.art];

  const head = (
    <View style={[styles.headInner, photo && styles.headOnPhoto]}>
      {photo ? null : (
        <View style={styles.icon}>
          <Feather name={ICONS[group.art]} size={20} color={colors.ink} />
        </View>
      )}
      <View style={{ flex: 1 }}>
        <Text style={styles.name}>{name}</Text>
        <Text style={styles.counts}>{facultyCounts(group)}</Text>
      </View>
      <Feather name={open ? 'chevron-up' : 'chevron-down'} size={20} color={colors.ink} />
    </View>
  );

  return (
    <View style={styles.card}>
      <Pressable
        accessibilityRole="button"
        accessibilityState={{ expanded: open }}
        accessibilityLabel={`${name}. ${facultyCounts(group)}`}
        onPress={() => setOpen((o) => !o)}>
        {photo ? (
          <ImageBackground source={photo.image} style={styles.photo} imageStyle={styles.photoImage} accessibilityIgnoresInvertColors>
            <View style={styles.scrim} />
            {head}
          </ImageBackground>
        ) : (
          head
        )}
      </Pressable>
      {open ? (
        <FadeIn>
          <View style={styles.body}>
            {children}
            {photo ? <PhotoCredit credit={photo.credit} source={photo.source} /> : null}
          </View>
        </FadeIn>
      ) : null}
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
  photo: { minHeight: 112, justifyContent: 'flex-end' },
  photoImage: { borderTopLeftRadius: radius.lg, borderTopRightRadius: radius.lg },
  // Darkens the photo under the words, so white text stays readable on any picture.
  scrim: { position: 'absolute', top: 0, right: 0, bottom: 0, left: 0, backgroundColor: colors.overlay },
  headInner: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 16 },
  headOnPhoto: { paddingTop: 40 },
  icon: {
    width: 40,
    height: 40,
    borderRadius: radius.sm,
    backgroundColor: colors.iconTile,
    alignItems: 'center',
    justifyContent: 'center',
  },
  name: { fontFamily: fonts.bold, fontSize: 15.5, lineHeight: 21, color: colors.ink },
  counts: { fontFamily: fonts.medium, fontSize: 13.5, lineHeight: 18, color: colors.textMuted, marginTop: 2 },
  body: { gap: 12, padding: 12, paddingTop: 4 },
});
