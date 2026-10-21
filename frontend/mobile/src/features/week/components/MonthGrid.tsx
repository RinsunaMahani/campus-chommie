/**
 * A month at a glance: Monday to Sunday, six weeks, each day's number with a dot for each kind of thing on it
 * (exam and test coral, deadline amber, class mint, plan violet), recess days shaded, today's number in mint, the
 * chosen day ringed. Calendar research: on a phone the month works as a compact overview, with the chosen
 * day's list underneath, so a tap picks a day rather than opening a tiny cell.
 */
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { t } from '@/shared/i18n';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius, space } from '@/shared/theme/tokens';

import { dotsOn, monthGrid, Sources } from '../calendarDays';

const LETTERS = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];

type Props = { month: string; today: string; selected: string; sources: Sources; onPick: (date: string) => void };

export function MonthGrid({ month, today, selected, sources, onPick }: Props) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const dot = { class: colors.accentDeep, test: colors.garnet, exam: colors.garnet, deadline: colors.marigold, plan: colors.classColours[4] };
  const days = monthGrid(month);
  return (
    <View style={styles.wrap}>
      <View style={styles.row}>
        {LETTERS.map((l, i) => (
          <Text key={i} style={styles.letter}>
            {l}
          </Text>
        ))}
      </View>
      {[0, 1, 2, 3, 4, 5].map((w) => (
        <View key={w} style={styles.row}>
          {days.slice(w * 7, w * 7 + 7).map((d) => {
            const inMonth = d.slice(0, 7) === month.slice(0, 7);
            const kinds = dotsOn(d, sources);
            const isSel = d === selected;
            return (
              <Pressable
                key={d}
                accessibilityRole="button"
                accessibilityState={{ selected: isSel }}
                accessibilityLabel={`${Number(d.slice(8))} ${kinds.length ? kinds.map((k) => t(`week.dot.${k}`)).join(', ') : t('week.nothing')}`}
                onPress={() => onPick(d)}
                style={[styles.cell, sources.off.has(d) && styles.off, isSel && styles.selected]}>
                <Text style={[styles.num, !inMonth && styles.other, d === today && styles.today]}>{Number(d.slice(8))}</Text>
                <View style={styles.dots}>
                  {kinds.map((k) => (
                    <View key={k} style={[styles.dot, { backgroundColor: dot[k] }]} />
                  ))}
                </View>
              </Pressable>
            );
          })}
        </View>
      ))}
      <View style={styles.legend}>
        {(['class', 'test', 'deadline', 'plan'] as const).map((k) => (
          <View key={k} style={styles.legendItem}>
            <View style={[styles.dot, { backgroundColor: dot[k] }]} />
            <Text style={styles.legendText}>{t(`week.dot.${k}`)}</Text>
          </View>
        ))}
        <View style={styles.legendItem}>
          <View style={[styles.offSwatch]} />
          <Text style={styles.legendText}>{t('week.recess')}</Text>
        </View>
      </View>
    </View>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    wrap: { gap: 2 },
    row: { flexDirection: 'row' },
    letter: { flex: 1, textAlign: 'center', fontFamily: fonts.bold, fontSize: 13, color: colors.textMuted, paddingVertical: 4 },
    // 48 high: a comfortable thumb target in a 7-column grid at 360 px.
    cell: { flex: 1, height: 48, alignItems: 'center', justifyContent: 'center', gap: 3, borderRadius: radius.sm },
    off: { backgroundColor: colors.iconTile },
    selected: { borderWidth: 1.5, borderColor: colors.accentDeep },
    num: { fontFamily: fonts.semibold, fontSize: 15, color: colors.ink, fontVariant: ['tabular-nums'] },
    other: { color: colors.textFaint },
    today: { color: colors.accentDeep, fontFamily: fonts.extrabold },
    dots: { flexDirection: 'row', gap: 3, height: 6 },
    dot: { width: 6, height: 6, borderRadius: 3 },
    legend: { flexDirection: 'row', flexWrap: 'wrap', gap: space.md, paddingTop: space.sm },
    legendItem: { flexDirection: 'row', alignItems: 'center', gap: 5 },
    legendText: { fontFamily: fonts.medium, fontSize: 13, color: colors.textMuted },
    offSwatch: { width: 12, height: 12, borderRadius: 3, backgroundColor: colors.iconTile },
  });
