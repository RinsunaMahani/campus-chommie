/**
 * Add or change a plan of the student's own: what it is (their words), a broad kind, every week or once, when and
 * where. "Find a time" takes how long it needs and suggests free stretches around their classes, exams and other
 * plans; a tap fills in the day and the times. The kinds are broad on purpose: we never ask about religion or
 * anything sensitive, and only the student sees what they type.
 */
import { router, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Card } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { SelectField } from '@/shared/components/SelectField';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Body, Overline } from '@/shared/components/Text';
import { TextField } from '@/shared/components/TextField';
import { t } from '@/shared/i18n';
import { Palette, useStyles } from '@/shared/theme/palette';
import { fonts, radius, space } from '@/shared/theme/tokens';

import { activitiesApi } from '../api/timetableApi';
import { ACTIVITY_KINDS, ActivityKind, FindTimeAnswer } from '../types';
import { cleanTime } from './ClassEditScreen';
import { DAY_NAMES } from './TimetableScreen';

const TIME = /^([01]\d|2[0-3]):([0-5]\d)$/;
const ISO = /^\d{4}-\d{2}-\d{2}$/;
const LENGTHS = [30, 60, 90, 120, 180];

/** Any time of day in 5-minute steps, as the server checks. */
export function dayTimeProblem(value: string): string | null {
  const m = TIME.exec(value);
  if (!m) return t('timetable.timeFormat');
  if (Number(m[2]) % 5) return t('timetable.timeSteps');
  return null;
}

function lengthLabel(minutes: number): string {
  if (minutes < 60) return t('activity.minutes', { n: minutes });
  return t('activity.hours', { n: String(minutes / 60) });
}

export default function ActivityEditScreen() {
  const styles = useStyles(makeStyles);
  const { id } = useLocalSearchParams<{ id?: string }>();
  const editing = !!id && id !== 'new';
  const [loaded, setLoaded] = useState(!editing);
  const [title, setTitle] = useState('');
  const [kind, setKind] = useState<ActivityKind>('personal');
  const [weekly, setWeekly] = useState(true);
  const [weekday, setWeekday] = useState('0');
  const [on, setOn] = useState('');
  const [starts, setStarts] = useState('');
  const [ends, setEnds] = useState('');
  const [place, setPlace] = useState('');
  const [length, setLength] = useState<number | null>(null);
  const [found, setFound] = useState<FindTimeAnswer | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [failure, setFailure] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!editing) return;
    activitiesApi
      .mine()
      .then(({ activities }) => {
        const a = activities.find((x) => x.id === id);
        if (a) {
          setTitle(a.title);
          setKind(a.kind);
          setWeekly(a.weekday != null);
          setWeekday(String(a.weekday ?? 0));
          setOn(a.on ?? '');
          setStarts(a.starts);
          setEnds(a.ends);
          setPlace(a.place ?? '');
        }
        setLoaded(true);
      })
      .catch((e) => setFailure(errorText(e, t('common.error'))));
  }, [editing, id]);

  async function findTime(minutes: number) {
    setLength(minutes);
    setFound(null);
    try {
      setFound(await activitiesApi.findTime(minutes));
    } catch (e) {
      setFailure(errorText(e, t('common.error')));
    }
  }

  async function save() {
    const s = cleanTime(starts);
    const e = cleanTime(ends);
    setStarts(s);
    setEnds(e);
    const problems: Record<string, string> = {};
    if (!title.trim()) problems.title = t('activity.titleMissing');
    const sp = dayTimeProblem(s);
    const ep = dayTimeProblem(e);
    if (sp) problems.starts = sp;
    if (ep) problems.ends = ep;
    if (!sp && !ep && e <= s) problems.ends = t('activity.endsAfter');
    if (!weekly && !ISO.test(on)) problems.on = t('money.goal.dateFormat');
    setErrors(problems);
    if (Object.keys(problems).length) return;
    const input = {
      title: title.trim(),
      kind,
      weekday: weekly ? Number(weekday) : null,
      on: weekly ? null : on,
      starts: s,
      ends: e,
      place: place.trim() || null,
    };
    setBusy(true);
    setFailure(null);
    try {
      if (editing) await activitiesApi.change(id as string, input);
      else await activitiesApi.add(input);
      router.back();
    } catch (err) {
      setFailure(errorText(err, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    setBusy(true);
    try {
      await activitiesApi.remove(id as string);
      router.back();
    } catch (err) {
      setFailure(errorText(err, t('common.error')));
      setBusy(false);
    }
  }

  const chip = (on_: boolean, label: string, onPress: () => void) => (
    <Pressable key={label} accessibilityRole="button" accessibilityState={{ selected: on_ }} onPress={onPress} style={[styles.chip, on_ && styles.chipOn]}>
      <Text style={[styles.chipText, on_ && styles.chipTextOn]}>{label}</Text>
    </Pressable>
  );

  return (
    <Screen
      back
      title={editing ? t('activity.changeTitle') : t('activity.addTitle')}
      footer={
        <View style={{ flexDirection: 'row', gap: 10 }}>
          {editing ? <Button compact title={t('timetable.delete')} variant="secondary" icon="trash-2" onPress={remove} disabled={busy} /> : null}
          <Button compact title={t('timetable.save')} variant="primary" onPress={save} loading={busy} disabled={!loaded} />
        </View>
      }>
      {!loaded && !failure ? <Loading /> : null}
      {failure ? <ErrorBox message={failure} /> : null}
      <TextField label={t('activity.title')} value={title} onChangeText={setTitle} maxLength={60} placeholder={t('activity.titleExample')} error={errors.title} hint={t('activity.titleHint')} />
      <View style={{ gap: space.sm }}>
        <Overline>{t('activity.kind')}</Overline>
        <View style={styles.wrap}>{ACTIVITY_KINDS.map((k) => chip(kind === k, t(`activity.kind.${k}`), () => setKind(k)))}</View>
      </View>

      <Card style={{ gap: space.sm }}>
        <Overline>{t('activity.findTitle')}</Overline>
        <Body>{t('activity.findSub')}</Body>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.row}>
          {LENGTHS.map((m) => chip(length === m, lengthLabel(m), () => findTime(m)))}
        </ScrollView>
        {found ? (
          <View style={{ gap: space.sm }}>
            {found.slots.length ? null : <Body>{found.lines[0]}</Body>}
            {found.slots.map((s) => (
              <Pressable
                key={`${s.on}${s.starts}`}
                accessibilityRole="button"
                onPress={() => {
                  setWeekly(false);
                  setOn(s.on);
                  setStarts(s.starts);
                  setEnds(s.ends);
                }}
                style={styles.slot}>
                <Text style={styles.slotDay}>{s.day}</Text>
                <Text style={styles.slotTime}>
                  {s.starts} to {s.ends}
                </Text>
              </Pressable>
            ))}
          </View>
        ) : null}
      </Card>

      <View style={styles.row}>
        {chip(weekly, t('activity.weekly'), () => setWeekly(true))}
        {chip(!weekly, t('activity.once'), () => setWeekly(false))}
      </View>
      {weekly ? (
        <SelectField label={t('timetable.day')} value={weekday} options={DAY_NAMES.map((d, i) => ({ value: String(i), label: d }))} onChange={setWeekday} />
      ) : (
        <TextField label={t('activity.date')} value={on} onChangeText={setOn} maxLength={10} placeholder="2026-10-30" keyboardType="numbers-and-punctuation" error={errors.on} />
      )}
      <View style={{ flexDirection: 'row', gap: 12 }}>
        <View style={{ flex: 1 }}>
          <TextField label={t('timetable.starts')} value={starts} onChangeText={setStarts} placeholder="18:00" maxLength={5} keyboardType="numbers-and-punctuation" error={errors.starts} />
        </View>
        <View style={{ flex: 1 }}>
          <TextField label={t('timetable.ends')} value={ends} onChangeText={setEnds} placeholder="19:30" maxLength={5} keyboardType="numbers-and-punctuation" error={errors.ends} />
        </View>
      </View>
      <TextField label={t('activity.place')} value={place} onChangeText={setPlace} maxLength={80} optional />
    </Screen>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    wrap: { flexDirection: 'row', flexWrap: 'wrap', gap: space.sm },
    row: { flexDirection: 'row', gap: space.sm },
    chip: { paddingHorizontal: 14, paddingVertical: 9, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.line, backgroundColor: colors.white },
    chipOn: { backgroundColor: colors.accent, borderColor: colors.accent },
    chipText: { fontFamily: fonts.semibold, fontSize: 14, color: colors.ink },
    chipTextOn: { color: colors.pillText },
    slot: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: space.md, borderRadius: radius.md, borderWidth: 1, borderColor: colors.accentDeep },
    slotDay: { fontFamily: fonts.semibold, fontSize: 15, color: colors.ink },
    slotTime: { fontFamily: fonts.bold, fontSize: 15, color: colors.accentDeep },
  });
