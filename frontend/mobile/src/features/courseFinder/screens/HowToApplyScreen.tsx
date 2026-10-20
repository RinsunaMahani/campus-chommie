/** How to apply to one university, on its own screen: dates on today's date, fee, documents, where. No marks. */
import { useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { View } from 'react-native';

import { HeroScreen } from '@/shared/components/HeroScreen';
import { Card } from '@/shared/components/Parts';
import { ErrorBox } from '@/shared/components/Status';
import { Overline } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { SkeletonCards } from '@/shared/motion/Shimmer';

import { courseFinderApi } from '../api/courseFinderApi';
import { ApplyWindows, GuideCard } from '../components/ApplyBox';
import { TestDateNote } from '../components/StillOpen';
import { ApplyInfoAnswer } from '../types';
import { errorText } from '../words';

export default function HowToApplyScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [answer, setAnswer] = useState<ApplyInfoAnswer | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (!id) return;
    courseFinderApi
      .applyInfo(id)
      .then(setAnswer)
      .catch((e) => setError(errorText(e)));
  }, [id, attempt]);

  return (
    <HeroScreen back overline={answer?.university.name} title={t('university.apply')}>
      {error ? (
        <ErrorBox
          message={error}
          onRetry={() => {
            setError(null);
            setAttempt((n) => n + 1);
          }}
        />
      ) : null}
      {!answer && !error ? <SkeletonCards count={3} /> : null}
      {answer ? (
        <View style={{ gap: 12 }}>
          <TestDateNote apply={answer.apply} />
          <Card style={{ gap: 12 }}>
            <Overline>{t('courseFinder.applyDates')}</Overline>
            <ApplyWindows windows={answer.apply.guide.windows} />
          </Card>
          <GuideCard guide={answer.apply.guide} />
        </View>
      ) : null}
    </HeroScreen>
  );
}
