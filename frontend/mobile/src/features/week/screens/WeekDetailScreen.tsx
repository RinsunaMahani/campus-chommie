import { useLocalSearchParams } from 'expo-router';
import { useCallback, useEffect, useState } from 'react';
import { View } from 'react-native';

import { SourceLink } from '@/shared/components/SourceLink';
import { errorText } from '@/shared/api/errors';
import { Card } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Body, Muted, Overline, Strong, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { formatShortDay } from '@/shared/lib/dates';

import { weekApi } from '../api/weekApi';
import { EventCard } from '../components/EventCard';
import { LoadBadge, weekLabel } from '../components/WeekStrip';
import { ClassEvent, FlagReason, Week } from '../types';

/** One week: its load and reason, its verified tests and deadlines (each can be flagged), and the university's calendar. */
export default function WeekDetailScreen() {
  const { start } = useLocalSearchParams<{ start: string }>();
  const [week, setWeek] = useState<Week | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const load = useCallback(() => {
    weekApi
      .weeks(1, start)
      .then((a) => setWeek(a.weeks[0] ?? null))
      .catch((e) => setError(errorText(e, t('common.error'))));
  }, [start]);

  useEffect(load, [load]);

  async function flag(event: ClassEvent, reason: FlagReason | null) {
    setBusy(event.id);
    try {
      const updated = reason ? await weekApi.flag(event.id, reason) : await weekApi.unflag(event.id);
      setWeek((w) => (w ? { ...w, events: w.events.map((e) => (e.id === updated.id ? { ...e, your_flag: updated.your_flag } : e)) } : w));
    } catch (e) {
      setError(errorText(e, t('common.error')));
    } finally {
      setBusy(null);
    }
  }

  return (
    <Screen back>
      {error ? <ErrorBox message={error} onRetry={load} /> : null}
      {!error && !week ? <Loading /> : null}
      {week ? (
        <>
          <View style={{ gap: 6 }}>
            <Title>{weekLabel(week)}</Title>
            <LoadBadge week={week} />
            <Body>{week.reason}</Body>
          </View>
          <Overline>{t('week.events')}</Overline>
          {week.events.length ? null : <Body>{t('week.noEvents')}</Body>}
          {week.events.map((e) => (
            <EventCard key={e.id} event={e} onFlag={(r) => flag(e, r)} busy={busy === e.id} />
          ))}
          {week.calendar.length ? <Overline>{t('week.calendar')}</Overline> : null}
          {week.calendar.map((c, i) => (
            <Card key={`${c.name}-${i}`} style={{ gap: 4 }}>
              <Strong>{c.name}</Strong>
              <Muted>{c.start === c.end ? formatShortDay(c.start) : t('week.range', { from: formatShortDay(c.start), to: formatShortDay(c.end) })}</Muted>
              {c.note ? <Body>{c.note}</Body> : null}
              <SourceLink url={c.source_url} />
            </Card>
          ))}
        </>
      ) : null}
    </Screen>
  );
}
