import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { View } from 'react-native';

import { DemoBanner } from '@/features/profile/components/DemoBanner';
import { useProfile } from '@/features/profile/state';
import { errorText } from '@/shared/api/errors';
import { Card, InfoNote, ListRow } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';

import { weekApi } from '../api/weekApi';
import { WeekStrip } from '../components/WeekStrip';
import { WeekAnswer } from '../types';

/** The Week tab: eight weeks, each one's load in words with its reason; then classes and marks. */
export default function WeekScreen() {
  const { mock } = useProfile();
  const [answer, setAnswer] = useState<WeekAnswer | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(() => {
    weekApi
      .weeks(8)
      .then((a) => {
        setAnswer(a);
        setError(null);
      })
      .catch((e) => setError(errorText(e, t('common.error'))))
      .finally(() => setRefreshing(false));
  }, []);

  useFocusEffect(
    useCallback(() => {
      if (!mock) load();
    }, [load, mock]),
  );

  if (mock) {
    return (
      <Screen tab>
        <Title>{t('week.title')}</Title>
        <InfoNote icon="info">{t('money.mockNotice')}</InfoNote>
      </Screen>
    );
  }

  return (
    <Screen
      tab
      onRefresh={() => {
        setRefreshing(true);
        load();
      }}
      refreshing={refreshing}>
      <View style={{ gap: 8 }}>
        <Title>{t('week.title')}</Title>
        <DemoBanner />
      </View>
      {answer?.university && !answer.university.confirmed && answer.university.notice ? (
        <InfoNote icon="alert-circle">{answer.university.notice}</InfoNote>
      ) : null}
      {answer?.notes.map((note, i) => (
        <InfoNote key={i} icon="info">
          {note}
        </InfoNote>
      ))}
      {error ? <ErrorBox message={error} onRetry={load} /> : null}
      {!error && !answer ? <Loading /> : null}
      {answer ? <WeekStrip weeks={answer.weeks} onOpen={(w) => router.push({ pathname: '/week/[start]', params: { start: w.week_start } })} /> : null}

      <Card style={{ paddingVertical: 4 }}>
        <ListRow icon="users" title={t('week.classes')} subtitle={t('week.classesSub')} onPress={() => router.push('/classes')} />
        <ListRow icon="award" title={t('week.marks')} subtitle={t('week.marksSub')} onPress={() => router.push('/marks')} last />
      </Card>
    </Screen>
  );
}
