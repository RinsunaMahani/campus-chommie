/**
 * One faculty's programmes in the Courses tab: a header with the field's icon
 * on a mint tile, the faculty's name and its counts in words, which opens to
 * the programme cards. Daylight paper: no photo here (dark words on a darkened
 * photo didn't read); the field photos stay on funder pages.
 */
import { Feather } from '@expo/vector-icons';
import { ComponentProps, ReactNode, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { t } from '@/shared/i18n';
import { FadeIn } from '@/shared/motion/FadeIn';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import { Art, FacultyGroup } from '../faculties';

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

  const head = (
    <View style={styles.headInner}>
      <View style={styles.icon}>
        <Feather name={ICONS[group.art]} size={20} color={colors.accentDeep} />
      </View>
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
        {head}
      </Pressable>
      {open ? (
        <FadeIn>
          <View style={styles.body}>
            {children}
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
  headInner: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 16 },
  icon: {
    width: 40,
    height: 40,
    borderRadius: radius.sm,
    backgroundColor: colors.accentTint,
    alignItems: 'center',
    justifyContent: 'center',
  },
  name: { fontFamily: fonts.display, fontSize: 17, lineHeight: 22, color: colors.ink },
  counts: { fontFamily: fonts.medium, fontSize: 13.5, lineHeight: 18, color: colors.textMuted, marginTop: 2 },
  body: { gap: 12, padding: 12, paddingTop: 4 },
});
