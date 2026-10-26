/**
 * The last few weeks' spending as small bars, oldest first and this week last. One series, so no legend: the
 * sentence above it says what it shows. A week with nothing logged has no bar and says so, so it never reads as R0.
 * Bars share one colour; this week is picked out by its label and amount, never by colour alone.
 */
import { StyleSheet, Text, View } from 'react-native';

import { t } from '@/shared/i18n';
import { formatRand } from '@/shared/lib/money';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts } from '@/shared/theme/tokens';

const HEIGHT = 72;

export function SpendingWeeks({ weeks }: { weeks: (number | null)[] }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const top = Math.max(1, ...weeks.map((w) => w ?? 0));
  const last = weeks.length - 1;
  const label = (i: number) => (i === last ? t('review.thisWeek') : t('review.weeksAgo', { n: last - i }));
  const summary = weeks
    .map((w, i) => `${label(i)}: ${w == null ? t('review.nothingLogged') : formatRand(w)}`)
    .join(', ');

  return (
    <View accessible accessibilityLabel={summary} style={styles.row}>
      {weeks.map((w, i) => (
        <View key={i} style={styles.col}>
          {i === last && w != null ? <Text style={styles.value}>{formatRand(w)}</Text> : null}
          <View style={styles.plot}>
            {w == null ? (
              <Text style={styles.none}>{t('review.noLog')}</Text>
            ) : (
              <View style={[styles.bar, { height: Math.max(3, Math.round((w / top) * HEIGHT)), backgroundColor: colors.accent }]} />
            )}
          </View>
          <Text style={[styles.label, i === last && styles.labelNow]} numberOfLines={1}>
            {label(i)}
          </Text>
        </View>
      ))}
    </View>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    row: { flexDirection: 'row', alignItems: 'flex-end', gap: 2, paddingTop: 4 },
    col: { flex: 1, alignItems: 'center', gap: 4 },
    plot: {
      height: HEIGHT,
      alignSelf: 'stretch',
      justifyContent: 'flex-end',
      alignItems: 'center',
      borderBottomWidth: StyleSheet.hairlineWidth,
      borderBottomColor: colors.line,
    },
    bar: { width: '56%', borderTopLeftRadius: 4, borderTopRightRadius: 4 },
    none: { fontFamily: fonts.medium, fontSize: 11, color: colors.textMuted, paddingBottom: 4 },
    value: { fontFamily: fonts.bold, fontSize: 12, color: colors.ink },
    label: { fontFamily: fonts.medium, fontSize: 11, color: colors.textMuted },
    labelNow: { fontFamily: fonts.bold, color: colors.ink },
  });
