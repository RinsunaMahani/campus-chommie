/**
 * Add or change one class: the module code, what kind of class, which day, from when to when (24-hour,
 * 5-minute steps, 06:00 to 22:00, as the server checks too), and optionally its name and venue.
 */
import { router, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Screen } from '@/shared/components/Screen';
import { SelectField } from '@/shared/components/SelectField';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Title } from '@/shared/components/Text';
import { TextField } from '@/shared/components/TextField';
import { t } from '@/shared/i18n';

import { timetableApi } from '../api/timetableApi';
import { CLASS_KINDS, ClassKind, EntryInput } from '../types';
import { DAY_NAMES } from './TimetableScreen';

const TIME = /^([01]\d|2[0-3]):([0-5]\d)$/;

/** "8:30", "830" or "0830" become "08:30"; anything else is left for the check to explain. */
export function cleanTime(value: string): string {
  const digits = value.replace(/[^0-9]/g, '');
  if (/^\d{3,4}$/.test(digits)) {
    const padded = digits.padStart(4, '0');
    return `${padded.slice(0, 2)}:${padded.slice(2)}`;
  }
  return value.trim();
}

export function timeProblem(value: string): string | null {
  const m = TIME.exec(value);
  if (!m) return t('timetable.timeFormat');
  const minutes = Number(m[1]) * 60 + Number(m[2]);
  if (minutes % 5) return t('timetable.timeSteps');
  if (minutes < 6 * 60 || minutes > 22 * 60) return t('timetable.timeRange');
  return null;
}

export default function ClassEditScreen() {
  const { id } = useLocalSearchParams<{ id?: string }>();
  const editing = !!id && id !== 'new';
  const [loaded, setLoaded] = useState(!editing);
  const [module, setModule] = useState('');
  const [title, setTitle] = useState('');
  const [kind, setKind] = useState<ClassKind>('lecture');
  const [weekday, setWeekday] = useState('0');
  const [starts, setStarts] = useState('');
  const [ends, setEnds] = useState('');
  const [venue, setVenue] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [failure, setFailure] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!editing) return;
    timetableApi
      .mine()
      .then(({ entries }) => {
        const e = entries.find((x) => x.id === id);
        if (e) {
          setModule(e.module);
          setTitle(e.title ?? '');
          setKind(e.kind);
          setWeekday(String(e.weekday));
          setStarts(e.starts);
          setEnds(e.ends);
          setVenue(e.venue ?? '');
        }
        setLoaded(true);
      })
      .catch((e) => setFailure(errorText(e, t('common.error'))));
  }, [editing, id]);

  async function save() {
    const s = cleanTime(starts);
    const e = cleanTime(ends);
    setStarts(s);
    setEnds(e);
    const found: Record<string, string> = {};
    if (!/^[A-Za-z0-9 ]{2,20}$/.test(module.trim())) found.module = t('timetable.moduleInvalid');
    const sp = timeProblem(s);
    const ep = timeProblem(e);
    if (sp) found.starts = sp;
    if (ep) found.ends = ep;
    if (!sp && !ep && e <= s) found.ends = t('timetable.endsAfter');
    setErrors(found);
    if (Object.keys(found).length) return;

    const input: EntryInput = {
      module: module.trim(),
      kind,
      weekday: Number(weekday),
      starts: s,
      ends: e,
      title: title.trim() || null,
      venue: venue.trim() || null,
    };
    setBusy(true);
    setFailure(null);
    try {
      if (editing) await timetableApi.change(id as string, input);
      else await timetableApi.add(input);
      router.back();
    } catch (err) {
      setFailure(errorText(err, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    if (!editing) return;
    setBusy(true);
    try {
      await timetableApi.remove(id as string);
      router.back();
    } catch (err) {
      setFailure(errorText(err, t('common.error')));
      setBusy(false);
    }
  }

  return (
    <Screen
      back
      footer={
        <View style={{ flexDirection: 'row', gap: 10 }}>
          {editing ? <Button compact title={t('timetable.delete')} variant="secondary" icon="trash-2" onPress={remove} disabled={busy} /> : null}
          <Button compact title={t('timetable.save')} variant="primary" onPress={save} loading={busy} disabled={!loaded} />
        </View>
      }>
      <Title>{editing ? t('timetable.changeTitle') : t('timetable.addTitle')}</Title>
      {!loaded && !failure ? <Loading /> : null}
      {failure ? <ErrorBox message={failure} /> : null}
      <TextField
        label={t('timetable.module')}
        value={module}
        onChangeText={setModule}
        autoCapitalize="characters"
        maxLength={20}
        placeholder="ANA201"
        hint={t('timetable.moduleHint')}
        error={errors.module}
      />
      <SelectField
        label={t('timetable.kindLabel')}
        value={kind}
        options={CLASS_KINDS.map((k) => ({ value: k, label: t(`timetable.kind.${k}`) }))}
        onChange={(v) => setKind(v as ClassKind)}
      />
      <SelectField
        label={t('timetable.day')}
        value={weekday}
        options={DAY_NAMES.map((d, i) => ({ value: String(i), label: d }))}
        onChange={setWeekday}
      />
      <View style={{ flexDirection: 'row', gap: 12 }}>
        <View style={{ flex: 1 }}>
          <TextField label={t('timetable.starts')} value={starts} onChangeText={setStarts} placeholder="08:00" maxLength={5} keyboardType="numbers-and-punctuation" error={errors.starts} />
        </View>
        <View style={{ flex: 1 }}>
          <TextField label={t('timetable.ends')} value={ends} onChangeText={setEnds} placeholder="09:40" maxLength={5} keyboardType="numbers-and-punctuation" error={errors.ends} />
        </View>
      </View>
      <TextField label={t('timetable.venue')} value={venue} onChangeText={setVenue} maxLength={80} optional />
      <TextField label={t('timetable.name')} value={title} onChangeText={setTitle} maxLength={80} optional hint={t('timetable.nameHint')} />
    </Screen>
  );
}
