/**
 * The week strip (brief, M4): each week's load as a word ("Manageable",
 * "Busy", "Heavy"), with colour and an icon only adding to it, the one-line
 * reason, and a tap to open the week.
 */
import { Feather } from '@expo/vector-icons';
import { ComponentProps } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { t } from '@/shared/i18n';
import { formatShortDay } from '@/shared/lib/dates';
import { fonts, radius } from '@/shared/theme/tokens';

import { Week } from '../types';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';

type IconName = ComponentProps<typeof Feather>['name'];

const lookOf = (colors: Palette): Record<Week['colour'], { icon: IconName; bg: string; fg: string; bar: string }> => ({
  green: { icon: 'smile', bg: colors.jadeTint, fg: colors.jade, bar: colors.jade },
  amber: { icon: 'alert-circle', bg: colors.marigoldTint, fg: colors.marigoldDeep, bar: colors.marigold },
  red: { icon: 'alert-triangle', bg: colors.garnetTint, fg: colors.garnet, bar: colors.garnet },
});

/** The load in words, with its colour and icon. */
export function LoadBadge({ week }: { week: Pick<Week, 'colour' | 'load'> }) {
  const styles = useStyles(makeStyles);
  const LOOK = lookOf(usePalette());
  const look = LOOK[week.colour] ?? LOOK.amber;
  return (
    <View style={[styles.badge, { backgroundColor: look.bg }]}>
      <Feather name={look.icon} size={13} color={look.fg} />
      <Text style={[styles.badgeText, { color: look.fg }]}>{week.load}</Text>
    </View>
  );
}

export function weekLabel(week: Pick<Week, 'week_start' | 'week_end' | 'this_week'>): string {
  if (week.this_week) return t('week.thisWeek');
  return t('week.range', { from: formatShortDay(week.week_start), to: formatShortDay(week.week_end) });
}

export function WeekStrip({ weeks, onOpen }: { weeks: Week[]; onOpen: (week: Week) => void }) {
  const LOOK = lookOf(usePalette());
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  return (
    <View style={{ gap: 10 }}>
      {weeks.map((week) => {
        const look = LOOK[week.colour] ?? LOOK.amber;
        return (
          <Pressable
            key={week.week_start}
            accessibilityRole="button"
            accessibilityLabel={`${weekLabel(week)}: ${week.reason}`}
            onPress={() => onOpen(week)}
            style={({ pressed }) => [styles.row, pressed && { opacity: 0.9 }]}>
            <View style={[styles.bar, { backgroundColor: look.bar }]} />
            <View style={styles.body}>
              <View style={styles.head}>
                <Text style={[styles.label, week.this_week && styles.labelNow]}>{weekLabel(week)}</Text>
                <LoadBadge week={week} />
              </View>
              <Text style={styles.reason}>{week.reason}</Text>
            </View>
            <Feather name="chevron-right" size={18} color={colors.textFaint} />
          </Pressable>
        );
      })}
    </View>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: colors.white,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.line,
    paddingRight: 12,
    overflow: 'hidden',
  },
  bar: { width: 5, alignSelf: 'stretch' },
  body: { flex: 1, gap: 4, paddingVertical: 12 },
  head: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 8, flexWrap: 'wrap' },
  label: { fontFamily: fonts.bold, fontSize: 14.5, color: colors.text },
  labelNow: { color: colors.accentDeep },
  reason: { fontFamily: fonts.body, fontSize: 13, lineHeight: 18, color: colors.textMuted },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    alignSelf: 'flex-start',
    borderRadius: radius.pill,
    paddingHorizontal: 9,
    paddingVertical: 3,
  },
  badgeText: { fontFamily: fonts.bold, fontSize: 12 },
});
