/**
 * Your points at one university, big, on raised glass: how that university counts
 * them, then each of your subjects with its mark, its level on that
 * university's scale and the points it adds, named as you chose them.
 */
import { StyleSheet, Text, View } from 'react-native';

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
      {points.subjects.length ? (
        <Expandable closedLabel={t('courseFinder.seeSubjects')} openLabel={t('courseFinder.hideSubjects')} color={colors.onAccent}>
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
  card: { borderRadius: radius.lg, padding: 18, gap: 6, borderWidth: 1, borderColor: colors.line, backgroundColor: colors.glassElevated },
  overline: { fontFamily: fonts.bold, fontSize: 11.5, letterSpacing: 0.8, textTransform: 'uppercase', color: colors.onAccentSoft },
  big: { fontFamily: fonts.display, fontSize: 40, lineHeight: 46, letterSpacing: -1, color: colors.onAccent },
  unit: { fontFamily: fonts.medium, fontSize: 16, letterSpacing: 0, color: colors.onAccentSoft },
  none: { fontFamily: fonts.bold, fontSize: 18, color: colors.onAccent },
  line: { fontFamily: fonts.body, fontSize: 14.5, lineHeight: 19, color: colors.onAccentSoft },
  rows: { marginTop: 8 },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingVertical: 8,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.onAccentTint,
  },
  subject: { fontFamily: fonts.semibold, fontSize: 15, color: colors.onAccent },
  level: { fontFamily: fonts.body, fontSize: 13.5, color: colors.onAccentSoft },
  adds: { fontFamily: fonts.bold, fontSize: 16, color: colors.onAccent },
  notCounted: { fontFamily: fonts.medium, fontSize: 13.5, color: colors.onAccentSoft },
});
