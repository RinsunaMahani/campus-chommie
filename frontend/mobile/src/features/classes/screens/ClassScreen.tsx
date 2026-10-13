import { router, useFocusEffect, useLocalSearchParams } from 'expo-router';
import { useCallback, useState } from 'react';
import { View } from 'react-native';

import { EventCard } from '@/features/week/components/EventCard';
import { weekApi } from '@/features/week/api/weekApi';
import { ClassEvent, FlagReason } from '@/features/week/types';
import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Card } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Body, Muted, Overline, Strong, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';

import { classesApi } from '../api/classesApi';
import { RepPanel } from '../components/RepPanel';
import { Candidate, ClassSummary, RepCode } from '../types';

/**
 * One class: its invite code, the rep's tools for reps, a way for students to
 * pass a message to their rep, and the confirmed tests and deadlines (each can
 * be flagged; reps see the counts).
 */
export default function ClassScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [cls, setCls] = useState<ClassSummary | null>(null);
  const [events, setEvents] = useState<ClassEvent[] | null>(null);
  const [waiting, setWaiting] = useState<Candidate[]>([]);
  const [repCode, setRepCode] = useState<RepCode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  useFocusEffect(
    useCallback(() => {
      Promise.all([classesApi.mine(), classesApi.events(id), classesApi.candidates(id)])
        .then(([mine, evs, cands]) => {
          setCls(mine.find((c) => c.id === id) ?? null);
          setEvents(evs);
          setWaiting(cands);
          setError(null);
        })
        .catch((e) => setError(errorText(e, t('common.error'))));
    }, [id]),
  );

  async function makeRepCode() {
    setBusy('rep');
    setError(null);
    try {
      setRepCode(await classesApi.repCode(id));
    } catch (e) {
      setError(errorText(e, t('common.error')));
    } finally {
      setBusy(null);
    }
  }

  async function flag(event: ClassEvent, reason: FlagReason | null) {
    setBusy(event.id);
    try {
      const updated = reason ? await weekApi.flag(event.id, reason) : await weekApi.unflag(event.id);
      setEvents((list) => (list ?? []).map((e) => (e.id === updated.id ? { ...e, your_flag: updated.your_flag, flags: e.flags } : e)));
    } catch (e) {
      setError(errorText(e, t('common.error')));
    } finally {
      setBusy(null);
    }
  }

  const announce = () => router.push({ pathname: '/classes/announce', params: { classId: id } });
  const rep = cls?.role === 'rep';

  return (
    <Screen back>
      {error ? <ErrorBox message={error} /> : null}
      {!error && !cls ? <Loading /> : null}
      {cls ? (
        <>
          <View style={{ gap: 4 }}>
            <Title>{cls.module_code}</Title>
            {cls.module_name ? <Strong>{cls.module_name}</Strong> : null}
            <Muted>{t('classes.counts', { members: cls.members, reps: cls.reps })}</Muted>
          </View>
          <Card style={{ gap: 4 }}>
            <Strong selectable>{t('classes.inviteCode', { code: cls.invite_code })}</Strong>
            <Muted>{t('classes.inviteHint')}</Muted>
          </Card>
          {rep ? (
            <RepPanel
              waiting={waiting.length}
              onCheck={() => router.push({ pathname: '/classes/confirm', params: { classId: id, candidateId: waiting[0].id } })}
              onAnnounce={announce}
              repCode={repCode}
              onMakeRepCode={makeRepCode}
              making={busy === 'rep'}
            />
          ) : (
            <View style={{ gap: 6 }}>
              <Button title={t('classes.announce')} variant="secondary" icon="clipboard" onPress={announce} />
              <Muted>{t('classes.waitsForRep')}</Muted>
            </View>
          )}
          <Overline>{t('classes.events')}</Overline>
          {events && !events.length ? <Body>{t('classes.noEvents')}</Body> : null}
          {events?.map((e) => (
            <EventCard key={e.id} event={e} onFlag={(r) => flag(e, r)} busy={busy === e.id} />
          ))}
        </>
      ) : null}
    </Screen>
  );
}
