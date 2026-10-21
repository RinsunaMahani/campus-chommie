import { Redirect, router } from 'expo-router';
import { useEffect, useMemo, useState } from 'react';
import { View } from 'react-native';

import { HeroScreen } from '@/shared/components/HeroScreen';
import { Card, InfoNote } from '@/shared/components/Parts';
import { ErrorBox } from '@/shared/components/Status';
import { Overline } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { FadeIn } from '@/shared/motion/FadeIn';
import { Shimmer, SkeletonCards } from '@/shared/motion/Shimmer';

import { courseFinderApi } from '../api/courseFinderApi';
import { ClosingSoon, FundingRow, fundingRow } from '../components/ClosingSoon';
import { QualifyStats, UniversityRow } from '../components/Qualify';
import { checkRows } from '../marks';
import { useCourseFinder } from '../state';
import { subjectName } from '../subjects';
import { errorText } from '../words';

/**
 * Step 2: where the marks meet the minimum. Every university we cover, with
 * your points there by its own rule and how many of its programmes you meet;
 * funding open now beside it. Nothing is saved.
 */
export default function QualifyScreen() {
  const cf = useCourseFinder();
  const sent = useMemo(() => checkRows(cf.rows), [cf.rows]);
  const valid = sent.marks.length > 0 && !Object.keys(sent.errors).length;
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [funding, setFunding] = useState<FundingRow>({ open: true, funders: [] });
  const { points, setPoints } = cf;

  useEffect(() => {
    if (!valid || points) return;
    courseFinderApi
      .points(sent.marks)
      .then((answer) => {
        setPoints(answer);
        setError(null);
      })
      .catch((e) => setError(errorText(e)));
  }, [valid, points, setPoints, sent.marks, attempt]);

  useEffect(() => {
    courseFinderApi
      .funding()
      .then((list) => setFunding(fundingRow(list)))
      .catch(() => undefined);
  }, []);

  if (!valid) return <Redirect href="/course-finder" />;

  return (
    <HeroScreen back overline={t('courseFinder.step', { n: 2 })} title={t('courseFinder.qualifyTitle')} subtitle={t('courseFinder.qualifySub')}>
      {error ? (
        <ErrorBox
          message={error}
          onRetry={() => {
            setError(null);
            setAttempt((n) => n + 1);
          }}
        />
      ) : null}
      {!points && !error ? (
        <View style={{ gap: 16 }}>
          <Card style={{ gap: 12 }}>
            <Shimmer width="40%" height={12} />
            <Shimmer width="70%" height={34} />
          </Card>
          <SkeletonCards count={3} />
        </View>
      ) : null}
      {points ? (
        <>
          <QualifyStats points={points} />
          {sent.otherLanguage ? (
            <InfoNote icon="info">{t('courseFinder.otherLanguageCounted', { subject: subjectName(sent.otherLanguage) })}</InfoNote>
          ) : null}
          <ClosingSoon row={funding} />
          <View style={{ gap: 10 }}>
            <Overline>{t('courseFinder.apsEach')}</Overline>
            {points.universities.map((u, i) => (
              <FadeIn key={u.university} delay={i * 60}>
                <UniversityRow u={u} onPress={() => router.push({ pathname: '/course-finder/university/[id]', params: { id: u.university } })} />
              </FadeIn>
            ))}
          </View>
          <InfoNote icon="lock">{t('courseFinder.nothingStored')}</InfoNote>
        </>
      ) : null}
    </HeroScreen>
  );
}
