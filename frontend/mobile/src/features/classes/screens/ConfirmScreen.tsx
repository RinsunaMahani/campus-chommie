import { router, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';

import { ClassEvent } from '@/features/week/types';
import { errorText } from '@/shared/api/errors';
import { InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';

import { classesApi } from '../api/classesApi';
import { CandidateForm } from '../components/CandidateForm';
import { Candidate, ConfirmBody } from '../types';

/** A rep checks one message and confirms it for the class, or discards it. */
export default function ConfirmScreen() {
  const { classId, candidateId } = useLocalSearchParams<{ classId: string; candidateId: string }>();
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [events, setEvents] = useState<ClassEvent[]>([]);
  const [done, setDone] = useState<string[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    Promise.all([classesApi.candidates(classId), classesApi.events(classId)])
      .then(([cands, evs]) => {
        setCandidate(cands.find((c) => c.id === candidateId) ?? null);
        setEvents(evs.filter((e) => !e.cancelled));
      })
      .catch((e) => setError(errorText(e, t('common.error'))));
  }, [classId, candidateId]);

  async function confirm(body: ConfirmBody) {
    setBusy(true);
    setError(null);
    try {
      const answer = await classesApi.confirm(candidateId, body);
      setDone(answer.lines.length ? answer.lines : [t('confirm.done')]);
    } catch (e) {
      setError(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  async function discard() {
    setBusy(true);
    try {
      await classesApi.discard(candidateId);
      router.back();
    } catch (e) {
      setError(errorText(e, t('common.error')));
      setBusy(false);
    }
  }

  return (
    <Screen back>
      <Title>{t('confirm.title')}</Title>
      {error ? <ErrorBox message={error} /> : null}
      {done ? (
        done.map((line, i) => (
          <InfoNote key={i} icon="check" tone="ok">
            {line}
          </InfoNote>
        ))
      ) : candidate ? (
        <CandidateForm candidate={candidate} events={events} busy={busy} onConfirm={confirm} onDiscard={discard} />
      ) : !error ? (
        <Loading />
      ) : null}
    </Screen>
  );
}
