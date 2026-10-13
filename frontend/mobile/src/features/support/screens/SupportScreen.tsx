import { useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { View } from 'react-native';

import { DemoBanner } from '@/features/profile/components/DemoBanner';
import { useProfile } from '@/features/profile/state';
import { errorText } from '@/shared/api/errors';
import { InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Body, Muted, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';

import { supportApi } from '../api/supportApi';
import { SupportSections } from '../components/SupportSections';
import { SupportAnswer } from '../types';

/** The Support tab: help on the student's campus, each service from the university's own page. */
export default function SupportScreen() {
  const { mock } = useProfile();
  const [answer, setAnswer] = useState<SupportAnswer | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    supportApi
      .forMyCampus()
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

  return (
    <Screen tab>
      <View style={{ gap: 6 }}>
        <Title>{t('support.title')}</Title>
        <DemoBanner />
        <Body>{t('support.intro')}</Body>
        {answer?.campus_name && answer.university ? <Muted>{`${answer.university.name} · ${answer.campus_name}`}</Muted> : null}
      </View>
      {mock ? <InfoNote icon="info">{t('money.mockNotice')}</InfoNote> : null}
      {answer?.university && !answer.university.confirmed && answer.university.notice ? (
        <InfoNote icon="alert-circle">{answer.university.notice}</InfoNote>
      ) : null}
      {answer?.lines.map((line, i) => (
        <InfoNote key={i} icon="info">
          {line}
        </InfoNote>
      ))}
      {error ? <ErrorBox message={error} onRetry={load} /> : null}
      {!mock && !error && !answer ? <Loading /> : null}
      {answer ? <SupportSections kinds={answer.kinds} /> : null}
    </Screen>
  );
}
