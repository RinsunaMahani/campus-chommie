import { Feather } from '@expo/vector-icons';
import { router, useFocusEffect } from 'expo-router';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { studentHeader } from '@/features/profile/components/HeaderTools';
import { useProfile } from '@/features/profile/state';
import { activitiesApi, examsApi, timetableApi } from '@/features/timetable/api/timetableApi';
import { rememberModules } from '@/features/timetable/colours';
import { Activity, ExamEntry, TimetableEntry } from '@/features/timetable/types';
import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Card, InfoNote, ListRow } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Overline } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { todaySast } from '@/shared/lib/dates';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import { weekApi } from '../api/weekApi';
import { addDays, addMonths, mondayOf, offDays, Sources, weekdayOf } from '../calendarDays';
import { CalendarGrid, Day } from '../components/CalendarGrid';
import { DayAgenda } from '../components/DayAgenda';
import { MonthGrid } from '../components/MonthGrid';
import { WeekStrip } from '../components/WeekStrip';
import { Week, WeekAnswer } from '../types';

export { addDays } from '../calendarDays';

const SHORT = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const MON3 = MONTHS.map((m) => m.slice(0, 3));
/** The server answers for weeks within a year of today. */
const REACH_DAYS = 360;

type Mode = 'month' | 'week' | 'three' | 'day';
type View_ = 'calendar' | 'load';

/** The time now in South Africa (SAST is UTC+2 all year), in minutes after midnight. */
function nowInSast(): number {
  const d = new Date();
  return ((d.getUTCHours() + 2) % 24) * 60 + d.getUTCMinutes();
}

const dd = (iso: string) => Number(iso.slice(8, 10));
const mon = (iso: string) => MON3[Number(iso.slice(5, 7)) - 1];

/** The first day shown and how many weeks to ask the server for, for a mode around `anchor`. */
function range(mode: Mode, anchor: string): { from: string; weeks: number } {
  if (mode === 'month') return { from: mondayOf(`${anchor.slice(0, 7)}-01`), weeks: 6 };
  if (mode === 'three') return { from: mondayOf(anchor), weeks: 2 };
  return { from: mondayOf(anchor), weeks: 1 };
}

function title(mode: Mode, anchor: string): string {
  if (mode === 'month') return `${MONTHS[Number(anchor.slice(5, 7)) - 1]} ${anchor.slice(0, 4)}`;
  if (mode === 'day') return `${SHORT[weekdayOf(anchor)]} ${dd(anchor)} ${mon(anchor)}`;
  const first = mode === 'week' ? mondayOf(anchor) : anchor;
  const last = addDays(first, mode === 'week' ? 6 : 2);
  return `${dd(first)}${mon(first) !== mon(last) ? ` ${mon(first)}` : ''} – ${dd(last)} ${mon(last)}`;
}

/**
 * The Week tab. Calendar: a month at a glance with the chosen day's list beneath it, or a time grid of a week,
 * three days or one day, with the student's classes (not in their university's recess), their classes' tests and
 * deadlines, their exams and their own plans; arrows move through the year. Load: the coming weeks' load in words.
 * "Add a plan" is the main action; the timetable, classes and marks are one tap away.
 */
export default function WeekScreen() {
  const { mock } = useProfile();
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const today = todaySast();
  const [view, setView] = useState<View_>('calendar');
  const [mode, setMode] = useState<Mode>('month');
  const [anchor, setAnchor] = useState(today);
  const [weeks, setWeeks] = useState<Week[] | null>(null);
  const [load, setLoad] = useState<WeekAnswer | null>(null);
  const [classes, setClasses] = useState<TimetableEntry[]>([]);
  const [exams, setExams] = useState<ExamEntry[]>([]);
  const [plans, setPlans] = useState<Activity[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const own = useCallback(() => {
    Promise.all([timetableApi.mine(), examsApi.mine(), activitiesApi.mine(), weekApi.weeks(8)])
      .then(([tt, x, a, w]) => {
        rememberModules(tt.entries.map((e) => e.module));
        setClasses(tt.entries);
        setExams(x.exams);
        setPlans(a.activities);
        setLoad(w);
        setError(null);
      })
      .catch((e) => setError(errorText(e, t('common.error'))))
      .finally(() => setRefreshing(false));
  }, []);

  useFocusEffect(
    useCallback(() => {
      if (!mock) own();
    }, [own, mock]),
  );

  // The weeks the current view needs, fetched whenever the view moves.
  const { from, weeks: count } = range(mode, anchor);
  useEffect(() => {
    if (mock) return;
    let live = true;
    weekApi
      .weeks(count, from)
      .then((w) => live && setWeeks(w.weeks))
      .catch((e) => live && setError(errorText(e, t('common.error'))));
    return () => {
      live = false;
    };
  }, [from, count, mock]);

  const sources: Sources = useMemo(
    () => ({
      classes,
      events: (weeks ?? []).flatMap((w) => w.events),
      exams,
      plans,
      off: offDays((weeks ?? []).flatMap((w) => w.calendar)),
    }),
    [classes, weeks, exams, plans],
  );

  if (mock) {
    return (
      <Screen tab title={t('week.title')}>
        <InfoNote icon="info">{t('money.mockNotice')}</InfoNote>
      </Screen>
    );
  }

  const step = (dir: 1 | -1) => {
    const next = mode === 'month' ? addMonths(anchor, dir) : addDays(anchor, dir * (mode === 'week' ? 7 : mode === 'three' ? 3 : 1));
    const span = (Date.parse(next) - Date.parse(today)) / 86400000;
    if (Math.abs(span) <= REACH_DAYS) setAnchor(next);
  };
  const atEdge = (dir: 1 | -1) => {
    const next = mode === 'month' ? addMonths(anchor, dir) : addDays(anchor, dir * 7);
    return Math.abs((Date.parse(next) - Date.parse(today)) / 86400000) > REACH_DAYS;
  };

  const gridDays: Day[] =
    mode === 'month'
      ? []
      : Array.from({ length: mode === 'week' ? 7 : mode === 'three' ? 3 : 1 }, (_, i) => {
          const date = addDays(mode === 'week' ? mondayOf(anchor) : anchor, i);
          return { date, weekday: weekdayOf(date), label: mode === 'week' ? SHORT[weekdayOf(date)].slice(0, 2) + ` ${dd(date)}` : `${SHORT[weekdayOf(date)]} ${dd(date)}`, today: date === today };
        });

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
        own();
      }}
      refreshing={refreshing}
      title={t('week.title')}
      {...studentHeader()}>
      <Button title={t('activity.add')} variant="primary" icon="plus" onPress={() => router.push({ pathname: '/activity/[id]', params: { id: 'new' } })} />
      <View style={styles.switchRow}>
        {chip(view === 'calendar', t('week.calendarView'), () => setView('calendar'), 'cal')}
        {chip(view === 'load', t('week.load'), () => setView('load'), 'load')}
      </View>
      {error ? <ErrorBox message={error} onRetry={own} /> : null}

      {view === 'calendar' ? (
        <View style={{ gap: 12 }}>
          <View style={styles.switchRow}>
            {chip(mode === 'month', t('week.month'), () => setMode('month'), 'month')}
            {chip(mode === 'week', t('week.week'), () => setMode('week'), 'week')}
            {chip(mode === 'three', t('week.threeDays'), () => setMode('three'), 'three')}
            {chip(mode === 'day', t('week.day'), () => setMode('day'), 'day')}
          </View>
          <View style={styles.navRow}>
            <Pressable accessibilityRole="button" accessibilityLabel={t('week.previous')} disabled={atEdge(-1)} onPress={() => step(-1)} hitSlop={10}>
              <Feather name="chevron-left" size={24} color={atEdge(-1) ? colors.textFaint : colors.ink} />
            </Pressable>
            <Pressable accessibilityRole="button" accessibilityLabel={t('week.backToToday')} onPress={() => setAnchor(today)}>
              <Text style={styles.navTitle}>{title(mode, anchor)}</Text>
            </Pressable>
            <Pressable accessibilityRole="button" accessibilityLabel={t('week.next')} disabled={atEdge(1)} onPress={() => step(1)} hitSlop={10}>
              <Feather name="chevron-right" size={24} color={atEdge(1) ? colors.textFaint : colors.ink} />
            </Pressable>
          </View>
          {!classes.length ? (
            <Pressable accessibilityRole="button" onPress={() => router.push('/timetable')}>
              <InfoNote icon="clock">{t('week.noClasses')}</InfoNote>
            </Pressable>
          ) : null}
          {!weeks ? <Loading /> : null}
          {weeks && mode === 'month' ? (
            <>
              <Card style={{ padding: 10 }}>
                <MonthGrid month={anchor} today={today} selected={anchor} sources={sources} onPick={setAnchor} />
              </Card>
              <Overline>{`${SHORT[weekdayOf(anchor)]} ${dd(anchor)} ${MONTHS[Number(anchor.slice(5, 7)) - 1]}`}</Overline>
              <DayAgenda date={anchor} sources={sources} />
            </>
          ) : null}
          {weeks && mode !== 'month' ? (
            <Card style={{ padding: 10 }}>
              <CalendarGrid
                days={gridDays}
                classes={classes}
                events={sources.events}
                exams={exams}
                activities={plans}
                off={sources.off}
                compact={mode === 'week'}
                nowMinutes={gridDays.some((d) => d.today) ? nowInSast() : null}
              />
            </Card>
          ) : null}
        </View>
      ) : null}

      {view === 'load' && load ? (
        <>
          {load.notes.map((note, i) => (
            <InfoNote key={i} icon="info">
              {note}
            </InfoNote>
          ))}
          <WeekStrip weeks={load.weeks} onOpen={(w) => router.push({ pathname: '/week/[start]', params: { start: w.week_start } })} />
        </>
      ) : null}

      <Card style={{ paddingVertical: 4 }}>
        <ListRow icon="clock" title={t('timetable.title')} subtitle={t('week.timetableSub')} onPress={() => router.push('/timetable')} />
        <ListRow icon="users" title={t('week.classes')} subtitle={t('week.classesSub')} onPress={() => router.push('/classes')} />
        <ListRow icon="award" title={t('week.marks')} subtitle={t('week.marksSub')} onPress={() => router.push('/marks')} last />
      </Card>
    </Screen>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    switchRow: { flexDirection: 'row', gap: 8, flexWrap: 'wrap' },
    navRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
    navTitle: { fontFamily: fonts.bold, fontSize: 17, color: colors.text },
    chip: {
      paddingHorizontal: 14,
      paddingVertical: 8,
      borderRadius: radius.pill,
      borderWidth: 1,
      borderColor: colors.line,
      backgroundColor: colors.white,
    },
    chipOn: { backgroundColor: colors.accent, borderColor: colors.accent },
    chipText: { fontFamily: fonts.semibold, fontSize: 14, color: colors.ink },
    chipTextOn: { color: colors.pillText },
  });
