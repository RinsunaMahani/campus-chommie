import { router, useLocalSearchParams } from 'expo-router';
import { ComponentProps, useEffect, useState } from 'react';
import { Text, View } from 'react-native';

import { Button } from '@/shared/components/Button';
import { HeroScreen } from '@/shared/components/HeroScreen';
import { Card, InfoNote, Tag } from '@/shared/components/Parts';
import { SourceLink } from '@/shared/components/SourceLink';
import { ErrorBox } from '@/shared/components/Status';
import { Muted, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { formatDay } from '@/shared/lib/dates';
import { SkeletonCards } from '@/shared/motion/Shimmer';
import { colors, fonts } from '@/shared/theme/tokens';

import { courseFinderApi } from '../api/courseFinderApi';
import { FirstStepsAnswer } from '../types';
import { errorText } from '../words';

type TagTone = NonNullable<ComponentProps<typeof Tag>['tone']>;

function tagTone(status: string): TagTone {
  if (status === 'done') return 'jade';
  if (status === 'now') return 'marigold';
  if (status === 'ahead') return 'info';
  return 'muted';
}

/**
 * NextStepsScreen: What happens from accepting an offer to your first lecture.
 * 1. Title: "If you're accepted at <university name>"
 * 2. Timeline of first_steps[0].steps with status, dates, lines, source links
 * 3. Note: "After you sign up, Support and Money show your campus's..."
 * 4. Pinned primary button: "Create my student account"
 */
export default function NextStepsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [data, setData] = useState<FirstStepsAnswer | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    courseFinderApi
      .firstSteps(id)
      .then(setData)
      .catch((e) => setError(errorText(e)))
      .finally(() => setLoading(false));
  }, [id]);

  function load() {
    if (!id) return;
    setLoading(true);
    setError(null);
    courseFinderApi
      .firstSteps(id)
      .then(setData)
      .catch((e) => setError(errorText(e)))
      .finally(() => setLoading(false));
  }

  const intake = data?.first_steps?.[0];
  const steps = intake?.steps ?? [];
  const empty = !loading && !error && steps.length === 0;

  return (
    <HeroScreen
      back
      title={data?.university ? t('courseFinder.nextStepsTitle', { university: data.university.name }) : t('courseFinder.nextStepsSub')}
      subtitle={t('courseFinder.nextStepsSub')}
      footer={
        <Button
          title={t('courseFinder.createStudentAccount')}
          variant="primary"
          icon="user-plus"
          onPress={() => router.push({ pathname: '/(auth)/create-account', params: { university: id } })}
        />
      }>
      {loading ? <SkeletonCards count={3} /> : null}

      {error ? <ErrorBox message={error} onRetry={load} /> : null}

      {!loading && !error && data ? (
        <View style={{ gap: 16 }}>
          {!data.university.confirmed && data.university.notice ? (
            <InfoNote icon="info">{data.university.notice}</InfoNote>
          ) : null}

          {empty ? (
            <Card style={{ gap: 12, padding: 16 }}>
              <Text style={{ fontFamily: fonts.body, fontSize: 14, color: colors.textMuted }}>
                {t('courseFinder.nextStepsNotPublished')}
              </Text>
              {data.university ? (
                <Button
                  title={data.university.name}
                  variant="secondary"
                  icon="arrow-right"
                  onPress={() => router.push(`/course-finder/university/${data.university.id}`)}
                />
              ) : null}
            </Card>
          ) : (
            <View style={{ gap: 12 }}>
              {steps.map((step) => {
                let dateText: string | null = null;
                if (step.starts && step.ends) {
                  dateText =
                    step.starts === step.ends
                      ? formatDay(step.starts)
                      : t('courseFinder.dateRange', { from: formatDay(step.starts), to: formatDay(step.ends) });
                } else if (step.starts) {
                  dateText = formatDay(step.starts);
                } else if (step.ends) {
                  dateText = formatDay(step.ends);
                }

                return (
                  <Card key={step.key} style={{ gap: 10, padding: 16 }}>
                    <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
                      <Title style={{ fontSize: 17, lineHeight: 22, flex: 1 }}>{step.title}</Title>
                      <Tag label={step.label} tone={tagTone(step.status)} />
                    </View>
                    {dateText ? (
                      <Muted style={{ fontFamily: fonts.medium, fontSize: 13, color: colors.textMuted }}>
                        {dateText}
                      </Muted>
                    ) : null}
                    {step.lines.map((line, idx) => (
                      <Text key={idx} style={{ fontFamily: fonts.body, fontSize: 13.5, lineHeight: 20, color: colors.text }}>
                        {line}
                      </Text>
                    ))}
                    {step.source_urls.length ? (
                      <View style={{ gap: 6, marginTop: 4 }}>
                        {step.source_urls.map((url) => (
                          <SourceLink key={url} url={url} />
                        ))}
                      </View>
                    ) : null}
                  </Card>
                );
              })}
            </View>
          )}

          <InfoNote icon="info">{t('courseFinder.nextStepsSupportMoney')}</InfoNote>
        </View>
      ) : null}
    </HeroScreen>
  );
}
