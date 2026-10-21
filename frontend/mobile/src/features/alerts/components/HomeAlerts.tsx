/**
 * Home's top section: today's alerts, most pressing first, each action opening
 * the screen it names. Reloads whenever Home comes back into view.
 */
import { Href, router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { View } from 'react-native';

import { useProfile } from '@/features/profile/state';
import { errorText } from '@/shared/api/errors';
import { InfoNote } from '@/shared/components/Parts';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Body, Overline } from '@/shared/components/Text';
import { t } from '@/shared/i18n';

import { alertsApi } from '../api/alertsApi';
import { ActionTarget, AlertsAnswer } from '../types';
import { AlertCard } from './AlertCard';

export const TARGETS: Record<ActionTarget, Href> = {
  week: '/week',
  money: '/money',
  cheap_things: '/money/cheap-things',
  marks: '/marks',
  support: '/support',
};

export function HomeAlerts() {
  const { mock } = useProfile();
  const [answer, setAnswer] = useState<AlertsAnswer | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    alertsApi
      .today()
      .then((a) => {
        setAnswer(a);
        setError(null);
      })
      .catch((e) => setError(errorText(e, t('common.error'))));
  }, []);

  useFocusEffect(
    useCallback(() => {
      if (!mock) load();
    }, [load, mock]),
  );

  if (mock) return null;
  return (
    <View style={{ gap: 10 }}>
      <Overline>{t('alerts.today')}</Overline>
      {error ? <ErrorBox message={error} onRetry={load} /> : null}
      {!error && !answer ? <Loading /> : null}
      {answer && !answer.alerts.length ? <Body>{t('alerts.none')}</Body> : null}
      {answer?.alerts.map((a, i) => (
        <AlertCard key={`${a.kind}-${i}`} alert={a} onOpen={(target) => router.push(TARGETS[target])} />
      ))}
      {answer?.notes.map((note, i) => (
        <InfoNote key={i} icon="info">
          {note}
        </InfoNote>
      ))}
    </View>
  );
}
