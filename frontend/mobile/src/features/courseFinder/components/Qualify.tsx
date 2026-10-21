/**
 * Step 2's parts: how many programmes the marks meet the minimum for, and
 * where, in big numbers; then a row per university with your points there,
 * each by its own rule. Universities come in name order: none is ranked
 * above another.
 */
import { Feather } from '@expo/vector-icons';
import { StyleSheet, Text, View } from 'react-native';

import { Card } from '@/shared/components/Parts';
import { Overline } from '@/shared/components/Text';
import { UniMonogram } from '@/shared/components/UniMonogram';
import { t } from '@/shared/i18n';
import { PressScale } from '@/shared/motion/PressScale';
import { colors, fonts, radius } from '@/shared/theme/tokens';

import { PointsAnswer, Tier, UniversityPoints } from '../types';

/** A reach programme's minimum is met too: it adds competitive selection on top. */
const MET: Tier[] = ['competitive', 'meets_minimum', 'reach'];

export function metAt(u: UniversityPoints): { met: number; total: number } {
  const total = Object.values(u.tiers).reduce((a, b) => a + b, 0);
  return { met: MET.reduce((a, tier) => a + (u.tiers[tier] ?? 0), 0), total };
}

/** Programmes whose minimum the marks meet, and at how many universities. */
export function qualifyCounts(points: PointsAnswer): { programmes: number; universities: number } {
  const met = points.universities.map((u) => metAt(u).met);
  return { programmes: met.reduce((a, b) => a + b, 0), universities: met.filter((n) => n > 0).length };
}

export function QualifyStats({ points }: { points: PointsAnswer }) {
  const { programmes, universities } = qualifyCounts(points);
  return (
    <Card style={{ gap: 12 }}>
      <Overline>{t('courseFinder.meetFor')}</Overline>
      <View style={styles.stats}>
        <View style={styles.stat}>
          <Text style={styles.big}>{programmes}</Text>
          <Text style={styles.statLabel}>{programmes === 1 ? t('courseFinder.statProgramme') : t('courseFinder.statProgrammes')}</Text>
        </View>
        <View style={styles.stat}>
          <Text style={styles.big}>{universities}</Text>
          <Text style={styles.statLabel}>{universities === 1 ? t('courseFinder.statUniversity') : t('courseFinder.statUniversities')}</Text>
        </View>
      </View>
      <Text style={styles.note}>{t('courseFinder.minimumNote')}</Text>
    </Card>
  );
}

export function UniversityRow({ u, onPress }: { u: UniversityPoints; onPress: () => void }) {
  const { met, total } = metAt(u);
  const sub = total ? t('courseFinder.meetsOf', { met, total }) : t('courseFinder.noProgrammesYet');
  return (
    <PressScale accessibilityRole="button" accessibilityLabel={`${u.university_name}: ${aps(u)}. ${sub}`} onPress={onPress} style={styles.row}>
      <UniMonogram id={u.university} size={40} />
      <View style={{ flex: 1, gap: 3 }}>
        <Text style={styles.name}>{u.university_name}</Text>
        <Text style={styles.sub}>{sub}</Text>
        {!u.confirmed && u.notice ? <Text style={styles.notice}>{u.notice}</Text> : null}
      </View>
      <View style={styles.score}>
        <Text style={styles.points}>{u.points == null ? '–' : fmt(u.points)}</Text>
        <Text style={styles.apsLabel}>{u.points == null ? t('courseFinder.noApsRule') : t('courseFinder.apsLabel')}</Text>
      </View>
      <Feather name="chevron-right" size={18} color={colors.textFaint} />
    </PressScale>
  );
}

/** "33", or "33.5" where Life Orientation counts for half. */
export function fmt(points: number): string {
  return Number.isInteger(points) ? String(points) : points.toFixed(1);
}

function aps(u: UniversityPoints): string {
  return u.points == null ? t('courseFinder.noApsRule') : `${fmt(u.points)} ${t('courseFinder.apsLabel')}`;
}

const styles = StyleSheet.create({
  stats: { flexDirection: 'row', gap: 16 },
  stat: { flex: 1 },
  big: { fontFamily: fonts.display, fontSize: 38, lineHeight: 44, letterSpacing: -1, color: colors.accent },
  statLabel: { fontFamily: fonts.bold, fontSize: 12, letterSpacing: 0.6, textTransform: 'uppercase', color: colors.text },
  note: { fontFamily: fonts.body, fontSize: 13, lineHeight: 19, color: colors.textMuted },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    padding: 14,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.white,
  },
  name: { fontFamily: fonts.bold, fontSize: 15, lineHeight: 20, color: colors.text },
  sub: { fontFamily: fonts.medium, fontSize: 13, color: colors.textMuted },
  notice: { fontFamily: fonts.body, fontSize: 12, color: colors.textFaint },
  // Narrow, so the university's name keeps the room: "No points rule yet" wraps onto two lines.
  score: { alignItems: 'flex-end', minWidth: 48, maxWidth: 64 },
  points: { fontFamily: fonts.display, fontSize: 26, lineHeight: 30, color: colors.accent },
  apsLabel: { fontFamily: fonts.semibold, fontSize: 11, color: colors.textMuted, textAlign: 'right' },
});
