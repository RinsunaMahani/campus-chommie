/**
 * The rep's check of a class message (brief, M4): the message as sent, what the
 * engine read, and the form it proposes, with the fields it was unsure of
 * highlighted. Only the rep's confirmation makes an event verified.
 */
import { ReactNode, useMemo, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { ClassEvent, EVENT_KINDS, EventKind } from '@/features/week/types';
import { kindLabel } from '@/features/week/components/EventCard';
import { Button } from '@/shared/components/Button';
import { Card, InfoNote } from '@/shared/components/Parts';
import { SelectField } from '@/shared/components/SelectField';
import { Muted, Overline } from '@/shared/components/Text';
import { TextField } from '@/shared/components/TextField';
import { t } from '@/shared/i18n';
import { dayInMonth, formatMonth, monthsFrom } from '@/shared/lib/dates';
import { fonts, radius } from '@/shared/theme/tokens';

import { Candidate, Change, ConfirmBody } from '../types';
import { Palette, useStyles } from '@/shared/theme/palette';

const CLOCK = /^([01]\d|2[0-3]):[0-5]\d$/;

/** A field the engine wasn't sure of: marked, with words, so colour never stands alone. */
function Check({ on, children }: { on: boolean; children: ReactNode }) {
  const styles = useStyles(makeStyles);
  if (!on) return <>{children}</>;
  return (
    <View style={styles.check}>
      <Text style={styles.checkText}>{t('confirm.check')}</Text>
      {children}
    </View>
  );
}

type Props = {
  candidate: Candidate;
  /** The class's events, for a "moved" or "cancelled" message to point at. */
  events: ClassEvent[];
  busy?: boolean;
  onConfirm: (body: ConfirmBody) => void;
  onDiscard: () => void;
};

export function CandidateForm({ candidate, events, busy, onConfirm, onDiscard }: Props) {
  const styles = useStyles(makeStyles);
  const p = candidate.proposed;
  const months = useMemo(() => monthsFrom(-1, 13), []);
  const [change, setChange] = useState<Change | 'new'>(p.change ?? 'new');
  const [eventId, setEventId] = useState<string | null>(p.event_id ?? candidate.changes_event?.id ?? null);
  const [kind, setKind] = useState<EventKind | null>(p.kind);
  const [title, setTitle] = useState(p.title ?? '');
  const [day, setDay] = useState(p.on ? String(Number(p.on.slice(8, 10))) : '');
  const [month, setMonth] = useState(p.on ? p.on.slice(0, 7) : months[1]);
  const [at, setAt] = useState(p.at ?? '');
  const [venue, setVenue] = useState(p.venue ?? '');
  const [weighting, setWeighting] = useState(p.weighting != null ? String(p.weighting) : '');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const needs = new Set(candidate.needs_check);

  function confirm() {
    const found: Record<string, string> = {};
    const on = day ? dayInMonth(month, Number(day)) : null;
    if (change !== 'cancelled') {
      if (day && !on) found.on = t('confirm.dayInvalid');
      if (at && !CLOCK.test(at)) found.at = t('confirm.timeInvalid');
      const w = Number(weighting.replace(',', '.'));
      if (weighting && !(w > 0 && w <= 100)) found.weighting = t('confirm.weightInvalid');
    }
    setErrors(found);
    if (Object.keys(found).length) return;
    const cancelled = change === 'cancelled';
    onConfirm({
      change: change === 'new' ? null : change,
      event_id: change === 'new' ? null : eventId,
      kind: cancelled ? null : kind,
      title: cancelled ? null : title.trim() || null,
      on: cancelled ? null : on,
      at: cancelled ? null : at || null,
      venue: cancelled ? null : venue.trim() || null,
      weighting: cancelled || !weighting ? null : Number(weighting.replace(',', '.')),
    });
  }

  return (
    <View style={{ gap: 14 }}>
      <Card style={{ gap: 6 }}>
        <Overline>{t('classes.message')}</Overline>
        <Text style={styles.quote}>{candidate.text}</Text>
      </Card>
      {candidate.lines.map((line, i) => (
        <InfoNote key={i} icon="eye">
          {line}
        </InfoNote>
      ))}
      <SelectField
        label={t('confirm.what')}
        value={change}
        options={[
          { value: 'new', label: t('confirm.new') },
          { value: 'moved', label: t('confirm.moved') },
          { value: 'cancelled', label: t('confirm.cancelled') },
        ]}
        onChange={(v) => setChange(v as Change | 'new')}
      />
      {change !== 'new' ? (
        <SelectField
          label={t('confirm.whichEvent')}
          value={eventId}
          options={events.map((e) => ({ value: e.id, label: `${kindLabel(e.kind)}${e.title ? `: ${e.title}` : ''}`, subtitle: e.when }))}
          onChange={setEventId}
        />
      ) : null}
      {change !== 'cancelled' ? (
        <>
          <Check on={needs.has('kind')}>
            <SelectField
              label={t('confirm.kind')}
              value={kind}
              options={EVENT_KINDS.map((k) => ({ value: k, label: kindLabel(k) }))}
              onChange={(v) => setKind(v as EventKind)}
            />
          </Check>
          <Check on={needs.has('title')}>
            <TextField label={t('confirm.name')} value={title} onChangeText={setTitle} maxLength={80} />
          </Check>
          <Check on={needs.has('on')}>
            <View style={styles.row}>
              <View style={{ width: 90 }}>
                <TextField
                  label={t('confirm.day')}
                  value={day}
                  onChangeText={(v) => setDay(v.replace(/[^0-9]/g, '').slice(0, 2))}
                  keyboardType="number-pad"
                  maxLength={2}
                  style={{ minWidth: 0, width: '100%' }}
                  error={errors.on}
                />
              </View>
              <View style={{ flex: 1 }}>
                <SelectField label={t('confirm.month')} value={month} options={months.map((m) => ({ value: m, label: formatMonth(m) }))} onChange={setMonth} />
              </View>
            </View>
          </Check>
          <Check on={needs.has('at')}>
            <TextField label={t('confirm.time')} value={at} onChangeText={setAt} maxLength={5} placeholder="14:00" error={errors.at} />
          </Check>
          <Check on={needs.has('venue')}>
            <TextField label={t('confirm.venue')} value={venue} onChangeText={setVenue} maxLength={80} />
          </Check>
          <Check on={needs.has('weighting')}>
            <TextField label={t('confirm.weighting')} value={weighting} onChangeText={setWeighting} keyboardType="decimal-pad" maxLength={5} error={errors.weighting} />
          </Check>
        </>
      ) : null}
      <View style={styles.row}>
        <Button compact title={t('confirm.discard')} variant="secondary" icon="x" onPress={onDiscard} disabled={busy} />
        <Button compact title={t('confirm.confirm')} variant="accent" icon="check" onPress={confirm} loading={busy} />
      </View>
      <Muted>{t('confirm.hint')}</Muted>
    </View>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  quote: { fontFamily: fonts.medium, fontSize: 14.5, lineHeight: 21, color: colors.text, fontStyle: 'italic' },
  row: { flexDirection: 'row', gap: 10, alignItems: 'flex-start' },
  check: { gap: 6, padding: 10, borderRadius: radius.sm, borderWidth: 1.5, borderColor: colors.marigold, backgroundColor: colors.marigoldTint },
  checkText: { fontFamily: fonts.bold, fontSize: 12, letterSpacing: 0.4, color: colors.marigoldDeep, textTransform: 'uppercase' },
});
