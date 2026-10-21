/**
 * One exam: its module in its own colour, the paper, the date, when it starts and how long it runs (if the
 * list says), a coral "Clashes" tag when another exam is at the same time, and a bin to delete it.
 */
import { Feather } from '@expo/vector-icons';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { Card, Tag } from '@/shared/components/Parts';
import { t } from '@/shared/i18n';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import { moduleColour } from '../colours';
import { ExamEntry, FoundExam } from '../types';

/** "3 h", "1.5 h" or "45 min"; empty when the list doesn't say. */
export function examLength(minutes: number | null): string {
  if (!minutes) return '';
  if (minutes < 60) return t('timetable.examLengthMinutes', { m: minutes });
  return t('timetable.examLength', { h: String(Math.round((minutes / 60) * 10) / 10) });
}

type Props = { exam: ExamEntry | FoundExam; onRemove?: () => void; removeLabel?: string };

export function ExamCard({ exam, onRemove, removeLabel }: Props) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const colour = moduleColour(colors, exam.module);
  const length = examLength(exam.minutes);
  return (
    <Card style={styles.card}>
      <View style={[styles.bar, { backgroundColor: colour }]} />
      <View style={styles.body}>
        <View style={styles.head}>
          <Text style={[styles.module, { color: colour }]}>{exam.module}</Text>
          {exam.paper ? <Text style={styles.paper}>{exam.paper}</Text> : null}
          {'clashes' in exam && exam.clashes ? <Tag label={t('timetable.clashes')} tone="garnet" /> : null}
        </View>
        {exam.title ? (
          <Text style={styles.title} numberOfLines={1}>
            {exam.title}
          </Text>
        ) : null}
        <View style={styles.meta}>
          <Feather name="calendar" size={13} color={colors.textMuted} />
          <Text style={styles.metaText}>
            {exam.day} · {exam.starts}
            {length ? ` · ${length}` : ''}
          </Text>
        </View>
      </View>
      {onRemove ? (
        <Pressable accessibilityRole="button" accessibilityLabel={removeLabel} onPress={onRemove} hitSlop={8} style={styles.remove}>
          <Feather name="x" size={18} color={colors.textMuted} />
        </Pressable>
      ) : null}
    </Card>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    card: { flexDirection: 'row', alignItems: 'center', padding: 0, overflow: 'hidden' },
    bar: { alignSelf: 'stretch', width: 5, borderTopLeftRadius: radius.lg, borderBottomLeftRadius: radius.lg },
    body: { flex: 1, gap: 4, padding: 12 },
    head: { flexDirection: 'row', alignItems: 'center', gap: 8, flexWrap: 'wrap' },
    module: { fontFamily: fonts.bold, fontSize: 16 },
    paper: { fontFamily: fonts.medium, fontSize: 14, color: colors.textMuted },
    title: { fontFamily: fonts.medium, fontSize: 14.5, color: colors.text },
    meta: { flexDirection: 'row', alignItems: 'center', gap: 6 },
    metaText: { flexShrink: 1, fontFamily: fonts.medium, fontSize: 14, color: colors.textMuted },
    remove: { padding: 14 },
  });
