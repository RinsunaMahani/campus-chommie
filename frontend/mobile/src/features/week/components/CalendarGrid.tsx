/**
 * The week as a calendar, the way Outlook shows a day: a time grid with the student's classes as blocks
 * (each module in its own colour) and their classes' tests and deadlines on top (coral for tests, quizzes
 * and exams, amber for assignments, blue for practicals). Deadlines without a time, or late at night, sit
 * in a "Due" row above the grid. The student's own exams sit on their dates as coral blocks as long as the
 * paper (or a marker where the list doesn't say). One day or three days side by side; a line marks the time
 * now on today.
 * Nothing here is worked out about the student: it only places what they and their reps entered.
 */
import { router } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { moduleColour, tint } from '@/features/timetable/colours';
import { ExamEntry, TimetableEntry } from '@/features/timetable/types';
import { t } from '@/shared/i18n';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import { ClassEvent } from '../types';

export const FIRST_HOUR = 7;
export const LAST_HOUR = 20; // the grid ends at 20:00
const HOUR = 56; // px per hour
const EVENT_MINUTES = 45; // how tall an event marker is: its length isn't known, so it never claims one

export type Day = { date: string; weekday: number; label: string; today: boolean };

function minutesOf(hhmm: string): number {
  const [h, m] = hhmm.split(':').map(Number);
  return h * 60 + m;
}

function top(minutes: number): number {
  return ((minutes - FIRST_HOUR * 60) / 60) * HOUR;
}

/** Events with no time, or outside the grid's hours, go in the "Due" row. */
export function inGrid(e: ClassEvent): boolean {
  if (!e.at) return false;
  const m = minutesOf(e.at);
  return m >= FIRST_HOUR * 60 && m + EVENT_MINUTES <= LAST_HOUR * 60;
}

function eventColour(colors: Palette, e: ClassEvent): string {
  if (e.kind === 'assignment') return colors.marigold;
  if (e.kind === 'practical') return colors.classColours[1];
  return colors.garnet;
}

type Props = { days: Day[]; classes: TimetableEntry[]; events: ClassEvent[]; exams?: ExamEntry[]; nowMinutes: number | null };

export function CalendarGrid({ days, classes, events, exams = [], nowMinutes }: Props) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const hours = Array.from({ length: LAST_HOUR - FIRST_HOUR }, (_, i) => FIRST_HOUR + i);
  const due = (d: Day) => events.filter((e) => e.on === d.date && !inGrid(e) && !e.cancelled);

  return (
    <View style={styles.wrap}>
      {/* Day headings and the "Due" row */}
      <View style={styles.row}>
        <View style={styles.gutter} />
        {days.map((d) => (
          <View key={d.date} style={styles.col}>
            <Text style={[styles.dayLabel, d.today && styles.today]}>{d.label}</Text>
            {due(d).map((e) => (
              <Pressable
                key={e.id}
                accessibilityRole="button"
                accessibilityLabel={`${e.module} ${e.title ?? e.kind}, ${e.when}`}
                onPress={() => router.push('/classes')}
                style={[styles.due, { borderColor: eventColour(colors, e), backgroundColor: tint(eventColour(colors, e)) }]}>
                <Text style={[styles.dueText, { color: eventColour(colors, e) }]} numberOfLines={2}>
                  {t('week.dueLabel')} {e.at ?? ''} · {e.module} {e.title ?? t(`week.kind.${e.kind}`)}
                </Text>
              </Pressable>
            ))}
          </View>
        ))}
      </View>

      {/* The time grid */}
      <View style={[styles.row, { height: (LAST_HOUR - FIRST_HOUR) * HOUR }]}>
        <View style={styles.gutter}>
          {hours.map((h) => (
            <Text key={h} style={[styles.hour, { top: top(h * 60) - 7 }]}>
              {String(h).padStart(2, '0')}:00
            </Text>
          ))}
        </View>
        {days.map((d) => (
          <View key={d.date} style={[styles.col, styles.lane]}>
            {hours.map((h) => (
              <View key={h} style={[styles.line, { top: top(h * 60) }]} />
            ))}
            {classes
              .filter((c) => c.weekday === d.weekday)
              .map((c) => {
                const colour = moduleColour(colors, c.module);
                const start = Math.max(minutesOf(c.starts), FIRST_HOUR * 60);
                const end = Math.min(minutesOf(c.ends), LAST_HOUR * 60);
                if (end <= start) return null;
                return (
                  <Pressable
                    key={c.id}
                    accessibilityRole="button"
                    accessibilityLabel={`${c.module} ${t(`timetable.kind.${c.kind}`)}, ${c.starts} to ${c.ends}${c.venue ? `, ${c.venue}` : ''}`}
                    onPress={() => router.push(`/timetable/${c.id}`)}
                    style={[styles.block, { top: top(start), height: Math.max(((end - start) / 60) * HOUR - 2, 22), backgroundColor: tint(colour), borderLeftColor: colour }]}>
                    <Text style={[styles.blockTitle, { color: colour }]} numberOfLines={1}>
                      {c.module}
                    </Text>
                    <Text style={styles.blockText} numberOfLines={2}>
                      {t(`timetable.kind.${c.kind}`)} · {c.starts}
                      {c.venue ? ` · ${c.venue}` : ''}
                    </Text>
                  </Pressable>
                );
              })}
            {events
              .filter((e) => e.on === d.date && inGrid(e) && !e.cancelled)
              .map((e) => {
                const colour = eventColour(colors, e);
                return (
                  <Pressable
                    key={e.id}
                    accessibilityRole="button"
                    accessibilityLabel={`${e.module} ${e.title ?? e.kind}, ${e.when}`}
                    onPress={() => router.push('/classes')}
                    style={[styles.event, { top: top(minutesOf(e.at as string)), height: (EVENT_MINUTES / 60) * HOUR, borderColor: colour, backgroundColor: colors.white }]}>
                    <Text style={[styles.blockTitle, { color: colour }]} numberOfLines={1}>
                      {e.at} {e.title ?? t(`week.kind.${e.kind}`)}
                    </Text>
                    <Text style={styles.blockText} numberOfLines={1}>
                      {e.module}
                    </Text>
                  </Pressable>
                );
              })}
            {exams
              .filter((x) => x.on === d.date)
              .map((x) => {
                const start = Math.max(minutesOf(x.starts), FIRST_HOUR * 60);
                const end = Math.min(start + (x.minutes ?? EVENT_MINUTES), LAST_HOUR * 60);
                if (end <= start) return null;
                return (
                  <Pressable
                    key={x.id}
                    accessibilityRole="button"
                    accessibilityLabel={`${t('timetable.exam')} ${x.module}${x.paper ? ` ${x.paper}` : ''}, ${x.day} ${x.starts}`}
                    onPress={() => router.push('/timetable')}
                    style={[styles.block, { top: top(start), height: Math.max(((end - start) / 60) * HOUR - 2, 22), backgroundColor: tint(colors.garnet), borderLeftColor: colors.garnet }]}>
                    <Text style={[styles.blockTitle, { color: colors.garnet }]} numberOfLines={1}>
                      {t('timetable.exam')} · {x.module}
                    </Text>
                    <Text style={styles.blockText} numberOfLines={2}>
                      {x.starts}
                      {x.paper ? ` · ${x.paper}` : ''}
                    </Text>
                  </Pressable>
                );
              })}
            {d.today && nowMinutes != null && nowMinutes >= FIRST_HOUR * 60 && nowMinutes <= LAST_HOUR * 60 ? (
              <View style={[styles.now, { top: top(nowMinutes) }]} accessibilityLabel={t('week.now')} />
            ) : null}
          </View>
        ))}
      </View>
    </View>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    wrap: { gap: 6 },
    row: { flexDirection: 'row' },
    gutter: { width: 42 },
    col: { flex: 1, gap: 4, paddingHorizontal: 2 },
    lane: { position: 'relative', borderLeftWidth: 1, borderLeftColor: colors.line },
    dayLabel: { fontFamily: fonts.bold, fontSize: 13, color: colors.textMuted, textAlign: 'center', paddingVertical: 4 },
    today: { color: colors.accentDeep },
    due: { borderWidth: 1, borderRadius: radius.sm, paddingHorizontal: 6, paddingVertical: 4 },
    dueText: { fontFamily: fonts.semibold, fontSize: 11.5 },
    hour: { position: 'absolute', left: 0, fontFamily: fonts.medium, fontSize: 10.5, color: colors.textFaint },
    line: { position: 'absolute', left: 0, right: 0, height: 1, backgroundColor: colors.line },
    block: {
      position: 'absolute',
      left: 2,
      right: 2,
      borderRadius: radius.sm,
      borderLeftWidth: 4,
      paddingHorizontal: 6,
      paddingVertical: 4,
      overflow: 'hidden',
    },
    event: {
      position: 'absolute',
      left: 6,
      right: 2,
      borderRadius: radius.sm,
      borderWidth: 1.5,
      paddingHorizontal: 6,
      paddingVertical: 3,
      overflow: 'hidden',
    },
    blockTitle: { fontFamily: fonts.bold, fontSize: 12.5 },
    blockText: { fontFamily: fonts.medium, fontSize: 11, color: colors.text },
    now: { position: 'absolute', left: 0, right: 0, height: 2, backgroundColor: colors.garnet },
  });
