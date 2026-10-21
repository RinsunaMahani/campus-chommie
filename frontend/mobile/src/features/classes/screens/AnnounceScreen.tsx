import { router, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox } from '@/shared/components/Status';
import { Body, Title } from '@/shared/components/Text';
import { TextField } from '@/shared/components/TextField';
import { t } from '@/shared/i18n';

import { classesApi } from '../api/classesApi';
import { Candidate } from '../types';

/**
 * Paste a class message: the engine reads its date, time and venue. A rep goes
 * straight on to check and confirm it; a student's waits for a rep.
 */
export default function AnnounceScreen() {
  const { classId } = useLocalSearchParams<{ classId: string }>();
  const [text, setText] = useState('');
  const [sent, setSent] = useState<Candidate | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function read() {
    setBusy(true);
    setError(null);
    try {
      const candidate = await classesApi.announce(classId, text);
      if (candidate.confirmable) {
        router.replace({ pathname: '/classes/confirm', params: { classId, candidateId: candidate.id } });
      } else {
        setSent(candidate);
      }
    } catch (e) {
      setError(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Screen
      back
      footer={
        sent ? (
          <Button title={t('onboarding.continue')} variant="secondary" onPress={() => router.back()} />
        ) : (
          <Button title={t('classes.read')} variant="accent" onPress={read} loading={busy} disabled={!text.trim()} />
        )
      }>
      <Title>{t('classes.announce')}</Title>
      {sent ? (
        <>
          {sent.lines.map((line, i) => (
            <Body key={i}>{line}</Body>
          ))}
          <InfoNote icon="clock">{t('classes.waitsForRep')}</InfoNote>
        </>
      ) : (
        <>
          <Body>{t('classes.announceHint')}</Body>
          <TextField
            label={t('classes.message')}
            value={text}
            onChangeText={setText}
            multiline
            maxLength={2000}
            style={{ height: 140, textAlignVertical: 'top', paddingTop: 12 }}
          />
        </>
      )}
      {error ? <ErrorBox message={error} /> : null}
    </Screen>
  );
}
