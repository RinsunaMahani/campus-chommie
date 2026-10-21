/**
 * Home's "Today": three tiles read at a glance, each one tap from its tab. The next class (or the one on now),
 * the next test or deadline, and how many days the money lasts, in amber when it runs out before the next
 * payment. Each tile says something useful even when its part isn't set up yet, with what to do.
 */
import { Feather } from '@expo/vector-icons';
import { router, useFocusEffect } from 'expo-router';
import { ComponentProps, useCallback, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { moneyApi } from '@/features/money/api/moneyApi';
import { Summary } from '@/features/money/types';
import { timetableApi } from '@/features/timetable/api/timetableApi';
import { TimetableEntry } from '@/features/timetable/types';
import { weekApi } from '@/features/week/api/weekApi';
import { ClassEvent } from '@/features/week/types';
import { t } from '@/shared/i18n';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius, space } from '@/shared/theme/tokens';

import { nextClass, nextDeadline, nowInSast } from '../today';

type IconName = ComponentProps<typeof Feather>['name'];

/** A big figure with a small unit under it, so the figure fits a narrow tile: "2" / "days", "Today". */
function inDays(n: number): [string, string] {
  if (n <= 0) return [t('home.today'), ''];
  return [String(n), n === 1 ? t('home.dayUnit') : t('home.daysUnit')];
}

export function TodayTiles() {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const [classes, setClasses] = useState<TimetableEntry[] | null>(null);
  const [events, setEvents] = useState<ClassEvent[] | null>(null);
  const [money, setMoney] = useState<Summary | null>(null);

  useFocusEffect(
    useCallback(() => {
      timetableApi.mine().then((a) => setClasses(a.entries)).catch(() => setClasses([]));
      weekApi.weeks(3).then((w) => setEvents(w.weeks.flatMap((x) => x.events))).catch(() => setEvents([]));
      moneyApi.summary().then(setMoney).catch(() => setMoney(null));
    }, []),
  );

  const now = nowInSast();
  const next = classes ? nextClass(classes, now) : null;
  const due = events ? nextDeadline(events, now.date, now.minutes) : null;

  const tile = (icon: IconName, label: string, [value, unit]: [string, string], sub: string, onPress: () => void, tint?: string) => (
    <Pressable
      key={label}
      accessibilityRole="button"
      accessibilityLabel={`${label}: ${value} ${unit}. ${sub}`}
      onPress={onPress}
      style={({ pressed }) => [styles.tile, pressed && { opacity: 0.8 }]}>
      <Feather name={icon} size={18} color={tint ?? colors.accentDeep} />
      <Text style={styles.label}>{label}</Text>
      <Text style={[styles.value, value.length > 5 && styles.valueLong, tint ? { color: tint } : null]} numberOfLines={1}>
        {value}
        {unit ? <Text style={styles.unit}> {unit}</Text> : null}
      </Text>
      <Text style={styles.sub} numberOfLines={2}>
        {sub}
      </Text>
    </Pressable>
  );

  const ready = money && money.ready ? money : null;
  const days = ready?.runway.days ?? null;
  return (
    <View style={styles.row}>
      {next
        ? tile(
            'clock',
            next.now ? t('home.classNow') : t('home.nextClass'),
            next.daysAhead === 0 ? [next.entry.starts, ''] : inDays(next.daysAhead),
            `${next.entry.module}${next.entry.venue ? ` · ${next.entry.venue}` : ''}`,
            () => router.push('/timetable'),
          )
        : tile('clock', t('home.nextClass'), ['—', ''], classes ? t('home.addClasses') : '', () => router.push('/timetable'))}
      {due
        ? tile(
            'flag',
            t('home.nextDue'),
            inDays(due.days),
            `${due.event.module} ${due.event.title ?? t(`week.kind.${due.event.kind}`)}`,
            () => router.push('/week'),
            due.days <= 2 ? colors.marigold : undefined,
          )
        : tile('flag', t('home.nextDue'), ['—', ''], events ? t('home.nothingDue') : '', () => router.push('/week'))}
      {ready
        ? tile(
            'credit-card',
            t('home.moneyLasts'),
            days == null ? [t('home.covered'), ''] : [String(days), days === 1 ? t('home.dayUnit') : t('home.daysUnit')],
            ready.runway.short_before_next ? t('home.shortBeforePay') : t('home.untilPay'),
            () => router.push('/money'),
            ready.runway.short_before_next ? colors.marigold : undefined,
          )
        : tile('credit-card', t('home.moneyLasts'), ['—', ''], money ? t('home.setUpMoney') : '', () => router.push('/money'))}
    </View>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    row: { flexDirection: 'row', gap: space.sm },
    tile: {
      flex: 1,
      gap: 4,
      padding: space.md,
      minHeight: 132,
      borderRadius: radius.lg,
      borderWidth: 1,
      borderColor: colors.line,
      backgroundColor: colors.white,
    },
    label: { fontFamily: fonts.semibold, fontSize: 13, lineHeight: 17, color: colors.textMuted },
    value: { fontFamily: fonts.display, fontSize: 26, lineHeight: 32, color: colors.ink },
    valueLong: { fontSize: 18, lineHeight: 32 },
    unit: { fontFamily: fonts.bold, fontSize: 14 },
    sub: { fontFamily: fonts.medium, fontSize: 13, lineHeight: 17, color: colors.textMuted },
  });
