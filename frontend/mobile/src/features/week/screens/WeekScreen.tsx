import { Feather } from '@expo/vector-icons';
import { router, useFocusEffect } from 'expo-router';
import { useCallback, useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { DemoBanner } from '@/features/profile/components/DemoBanner';
import { useProfile } from '@/features/profile/state';
import { timetableApi } from '@/features/timetable/api/timetableApi';
import { rememberModules } from '@/features/timetable/colours';
import { TimetableEntry } from '@/features/timetable/types';
import { errorText } from '@/shared/api/errors';
import { Card, InfoNote, ListRow } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import { weekApi } from '../api/weekApi';
import { CalendarGrid, Day } from '../components/CalendarGrid';
import { WeekStrip } from '../components/WeekStrip';
import { WeekAnswer } from '../types';

const SHORT = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

export function addDays(iso: string, n: number): string {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(Date.UTC(y, m - 1, d + n)).toISOString().slice(0, 10);
}

function weekdayOf(iso: string): number {
  const [y, m, d] = iso.split('-').map(Number);
  return (new Date(Date.UTC(y, m - 1, d)).getUTCDay() + 6) % 7;
}

/** The time now in South Africa (SAST is UTC+2 all year), in minutes after midnight. */
function nowInSast(): number {
  const d = new Date();
  return ((d.getUTCHours() + 2) % 24) * 60 + d.getUTCMinutes();
}

type View_ = 'calendar' | 'load';

/**
 * The Week tab. Calendar (the default): the week's days, then a time grid with the student's classes in
 * their module colours and their classes' tests and deadlines, one day or three at a time, week by week.
 * Load: eight weeks, each one's load in words with its reason. Then classes and marks.
 */
export default function WeekScreen() {
  const { mock } = useProfile();
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const [answer, setAnswer] = useState<WeekAnswer | null>(null);
  const [classes, setClasses] = useState<TimetableEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [view, setView] = useState<View_>('calendar');
  const [span, setSpan] = useState<1 | 3>(1);
  const [weekIndex, setWeekIndex] = useState(0);
  const [picked, setPicked] = useState<string | null>(null);

  const load = useCallback(() => {
    Promise.all([weekApi.weeks(8), timetableApi.mine()])
      .then(([w, tt]) => {
        rememberModules(tt.entries.map((e) => e.module));
        setAnswer(w);
        setClasses(tt.entries);
        setError(null);
      })
      .catch((e) => setError(errorText(e, t('common.error'))))
      .finally(() => setRefreshing(false));
  }, []);

  useFocusEffect(
    useCallback(() => {
      if (!mock) load();
    }, [load, mock]),
  );

  const week = answer?.weeks[weekIndex] ?? null;
  const today = answer?.today ?? null;
  const weekDates = useMemo(() => (week ? Array.from({ length: 7 }, (_, i) => addDays(week.week_start, i)) : []), [week]);
  const selected = picked && weekDates.includes(picked) ? picked : today && weekDates.includes(today) ? today : weekDates[0];

  const days: Day[] = useMemo(() => {
    if (!selected) return [];
    let first = weekDates.indexOf(selected);
    if (span === 3) first = Math.min(first, 4);
    return weekDates.slice(first, first + span).map((date) => ({
      date,
      weekday: weekdayOf(date),
      label: `${SHORT[weekdayOf(date)]} ${Number(date.slice(8, 10))}`,
      today: date === today,
    }));
  }, [selected, span, weekDates, today]);

  if (mock) {
    return (
      <Screen tab>
        <Title>{t('week.title')}</Title>
        <InfoNote icon="info">{t('money.mockNotice')}</InfoNote>
      </Screen>
    );
  }

  const chip = (on: boolean, label: string, onPress: () => void, key: string) => (
    <Pressable key={key} accessibilityRole="button" accessibilityState={{ selected: on }} onPress={onPress} style={[styles.chip, on && styles.chipOn]}>
      <Text style={[styles.chipText, on && styles.chipTextOn]}>{label}</Text>
    </Pressable>
  );

  return (
    <Screen
      tab
      onRefresh={() => {
        setRefreshing(true);
        load();
      }}
      refreshing={refreshing}>
      <View style={{ gap: 8 }}>
        <Title>{t('week.title')}</Title>
        <DemoBanner />
      </View>
      <View style={styles.switchRow}>
        {chip(view === 'calendar', t('week.calendarView'), () => setView('calendar'), 'cal')}
        {chip(view === 'load', t('week.load'), () => setView('load'), 'load')}
      </View>
      {answer?.university && !answer.university.confirmed && answer.university.notice ? (
        <InfoNote icon="alert-circle">{answer.university.notice}</InfoNote>
      ) : null}
      {error ? <ErrorBox message={error} onRetry={load} /> : null}
      {!error && !answer ? <Loading /> : null}

      {answer && view === 'calendar' && week ? (
        <View style={{ gap: 12 }}>
          <View style={styles.weekRow}>
            <Pressable accessibilityRole="button" accessibilityLabel={t('week.prevWeek')} disabled={weekIndex === 0} onPress={() => { setWeekIndex((i) => i - 1); setPicked(null); }} hitSlop={8}>
              <Feather name="chevron-left" size={22} color={weekIndex === 0 ? colors.textFaint : colors.ink} />
            </Pressable>
            <Text style={styles.weekTitle}>{week.this_week ? t('week.thisWeek') : `${Number(week.week_start.slice(8, 10))} to ${Number(week.week_end.slice(8, 10))}`}</Text>
            <Pressable accessibilityRole="button" accessibilityLabel={t('week.nextWeek')} disabled={weekIndex >= answer.weeks.length - 1} onPress={() => { setWeekIndex((i) => i + 1); setPicked(null); }} hitSlop={8}>
              <Feather name="chevron-right" size={22} color={weekIndex >= answer.weeks.length - 1 ? colors.textFaint : colors.ink} />
            </Pressable>
          </View>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chips}>
            {weekDates.map((d) => chip(d === selected, `${SHORT[weekdayOf(d)]} ${Number(d.slice(8, 10))}`, () => setPicked(d), d))}
          </ScrollView>
          <View style={styles.switchRow}>
            {chip(span === 1, t('week.day'), () => setSpan(1), 'one')}
            {chip(span === 3, t('week.threeDays'), () => setSpan(3), 'three')}
          </View>
          {!classes.length ? (
            <Pressable accessibilityRole="button" onPress={() => router.push('/timetable')}>
              <InfoNote icon="clock">{t('week.noClasses')}</InfoNote>
            </Pressable>
          ) : null}
          <Card style={{ padding: 10 }}>
            <CalendarGrid days={days} classes={classes} events={week.events} nowMinutes={days.some((d) => d.today) ? nowInSast() : null} />
          </Card>
        </View>
      ) : null}

      {answer && view === 'load' ? (
        <>
          {answer.notes.map((note, i) => (
            <InfoNote key={i} icon="info">
              {note}
            </InfoNote>
          ))}
          <WeekStrip weeks={answer.weeks} onOpen={(w) => router.push({ pathname: '/week/[start]', params: { start: w.week_start } })} />
        </>
      ) : null}

      <Card style={{ paddingVertical: 4 }}>
        <ListRow icon="users" title={t('week.classes')} subtitle={t('week.classesSub')} onPress={() => router.push('/classes')} />
        <ListRow icon="award" title={t('week.marks')} subtitle={t('week.marksSub')} onPress={() => router.push('/marks')} last />
      </Card>
    </Screen>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    switchRow: { flexDirection: 'row', gap: 8 },
    weekRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
    weekTitle: { fontFamily: fonts.bold, fontSize: 16, color: colors.text },
    chips: { gap: 8, paddingRight: 8 },
    chip: {
      paddingHorizontal: 14,
      paddingVertical: 8,
      borderRadius: radius.pill,
      borderWidth: 1,
      borderColor: colors.line,
      backgroundColor: colors.white,
    },
    chipOn: { backgroundColor: colors.accent, borderColor: colors.accent },
    chipText: { fontFamily: fonts.semibold, fontSize: 13, color: colors.ink },
    chipTextOn: { color: colors.pillText },
  });
