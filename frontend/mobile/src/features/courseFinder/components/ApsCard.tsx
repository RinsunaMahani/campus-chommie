/**
 * Your points at one university, big, on a paper card: how that university counts
 * them, then each of your subjects with its mark, its level on that
 * university's scale and the points it adds, named as you chose them.
 */
import * as WebBrowser from 'expo-web-browser';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { t } from '@/shared/i18n';
import { Expandable } from '@/shared/motion/Expandable';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import { MarkRow, Sent } from '../marks';
import { subjectName } from '../subjects';
import { UniversityPoints } from '../types';
import { fmt } from './Qualify';

type Props = { points: UniversityPoints; sent: Sent; rows: MarkRow[] };

export function ApsCard({ points, sent, rows }: Props) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const percent = new Map(rows.map((r) => [r.subject, r.percent]));
  return (
    <View style={styles.card}>
      <Text style={styles.overline}>{t('courseFinder.apsHere')}</Text>
      {points.points == null ? (
        <Text style={styles.none}>{t('courseFinder.noApsRule')}</Text>
      ) : (
        <Text style={styles.big}>
          {fmt(points.points)} <Text style={styles.unit}>{t('courseFinder.pointsWord')}</Text>
        </Text>
      )}
      {points.lines.map((line, i) => (
        <Text key={i} style={styles.line}>
          {line}
        </Text>
      ))}
      {points.points == null && points.source_url ? (
        <Pressable accessibilityRole="link" onPress={() => WebBrowser.openBrowserAsync(points.source_url!)} hitSlop={6}>
          <Text style={styles.link}>{t('courseFinder.checkOwnPoints')} ›</Text>
        </Pressable>
      ) : null}
      {points.subjects.length ? (
        <Expandable closedLabel={t('courseFinder.seeSubjects')} openLabel={t('courseFinder.hideSubjects')} color={colors.accentDeep}>
          <View style={styles.rows}>
            {points.subjects.map((s) => {
              const mine = sent.names[s.subject] ?? s.subject;
              return (
                <View key={s.subject} style={styles.row}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.subject}>{subjectName(mine)}</Text>
                    <Text style={styles.level}>{t('courseFinder.subjectLevel', { percent: percent.get(mine) ?? '', level: s.level })}</Text>
                  </View>
                  <Text style={[styles.adds, !s.counted && styles.notCounted]}>
                    {s.counted ? `+${fmt(s.points)}` : t('courseFinder.notCounted')}
                  </Text>
                </View>
              );
            })}
          </View>
        </Expandable>
      ) : null}
    </View>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
  // Daylight paper: dark words on a card, the number in forest (it was white on glass for the dark wallpaper).
  card: {
    borderRadius: radius.lg,
    padding: 18,
    gap: 6,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.white,
    boxShadow: '0 6px 18px rgba(28, 43, 30, 0.08)',
  },
  overline: { fontFamily: fonts.bold, fontSize: 11.5, letterSpacing: 0.8, textTransform: 'uppercase', color: colors.textMuted },
  big: { fontFamily: fonts.display, fontSize: 40, lineHeight: 46, letterSpacing: -1, color: colors.accentDeep },
  unit: { fontFamily: fonts.medium, fontSize: 16, letterSpacing: 0, color: colors.textMuted },
  none: { fontFamily: fonts.bold, fontSize: 18, color: colors.ink },
  line: { fontFamily: fonts.body, fontSize: 14.5, lineHeight: 19, color: colors.text },
  link: { fontFamily: fonts.bold, fontSize: 14.5, color: colors.accentDeep, marginTop: 4 },
  rows: { marginTop: 8 },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingVertical: 8,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.line,
  },
  subject: { fontFamily: fonts.semibold, fontSize: 15, color: colors.ink },
  level: { fontFamily: fonts.body, fontSize: 13.5, color: colors.textMuted },
  adds: { fontFamily: fonts.bold, fontSize: 16, color: colors.accentDeep },
  notCounted: { fontFamily: fonts.medium, fontSize: 13.5, color: colors.textMuted },
});
