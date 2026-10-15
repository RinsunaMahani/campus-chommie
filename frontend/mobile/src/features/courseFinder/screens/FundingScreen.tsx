import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { ComponentProps, useEffect, useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { HeroScreen } from '@/shared/components/HeroScreen';
import { Card, InfoNote, Tag } from '@/shared/components/Parts';
import { ErrorBox } from '@/shared/components/Status';
import { Body, Muted, Overline, Strong, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { FadeIn } from '@/shared/motion/FadeIn';
import { SkeletonCards } from '@/shared/motion/Shimmer';
import { colors, fonts, radius } from '@/shared/theme/tokens';

import { courseFinderApi } from '../api/courseFinderApi';
import { useCourseFinder } from '../state';
import { FundingCard, FundingListAnswer } from '../types';
import { errorText } from '../words';

type TagTone = NonNullable<ComponentProps<typeof Tag>['tone']>;

function tagTone(status: string): TagTone {
  if (status === 'open') return 'jade';
  if (status === 'closing_soon' || status === 'late_open') return 'marigold';
  if (status === 'closed' || status === 'not_published') return 'muted';
  return 'info';
}

function matchesGoalField(funder: FundingCard, goalFields: string[]): boolean {
  if (!goalFields.length) return false;
  return funder.fields?.some((f) => goalFields.includes(f.id)) ?? false;
}

/**
 * Funding options: Choice between NSFAS and other bursaries and loans.
 * Public and read-only, nothing sent about the learner.
 */
export default function FundingScreen() {
  const cf = useCourseFinder();
  const [data, setData] = useState<FundingListAnswer | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    courseFinderApi
      .fundingList()
      .then(setData)
      .catch((e) => setError(errorText(e)))
      .finally(() => setLoading(false));
  }, []);

  const goalFields = useMemo(() => cf.plan?.goal?.match.fields ?? [], [cf.plan?.goal?.match.fields]);

  const nsfas = useMemo(() => data?.funders.find((f) => f.id === 'nsfas') ?? null, [data]);

  const otherFunders = useMemo(() => data?.funders.filter((f) => f.id !== 'nsfas') ?? [], [data]);

  const goalFieldLabel = useMemo(() => {
    if (!data || !goalFields.length) return null;
    return data.fields.find((f) => goalFields.includes(f.id))?.label ?? goalFields[0];
  }, [data, goalFields]);

  const sortedOthers = useMemo(() => {
    if (filter !== 'all' || !goalFields.length) return otherFunders;
    const matched: FundingCard[] = [];
    const rest: FundingCard[] = [];
    for (const f of otherFunders) {
      if (matchesGoalField(f, goalFields)) matched.push(f);
      else rest.push(f);
    }
    return [...matched, ...rest];
  }, [otherFunders, filter, goalFields]);

  const displayedFunders = useMemo(() => {
    if (filter === 'all') return sortedOthers;
    return otherFunders.filter(
      (f) => f.any_field || f.fields?.some((field) => field.id === filter),
    );
  }, [filter, sortedOthers, otherFunders]);

  const hasGoalMatches = useMemo(
    () => goalFields.length > 0 && otherFunders.some((f) => matchesGoalField(f, goalFields)),
    [goalFields, otherFunders],
  );

  return (
    <HeroScreen
      back
      title={t('courseFinder.fundingTitle')}
      subtitle={t('courseFinder.fundingSub')}>
      {loading ? <SkeletonCards count={3} /> : null}

      {error ? (
        <ErrorBox
          message={error}
          onRetry={() => {
            setError(null);
            setLoading(true);
            courseFinderApi
              .fundingList()
              .then(setData)
              .catch((e) => setError(errorText(e)))
              .finally(() => setLoading(false));
          }}
        />
      ) : null}

      {data ? (
        <View style={{ gap: 16 }}>
          <Body style={styles.summary}>{data.summary}</Body>

          {!data.confirmed && data.notice ? (
            <InfoNote icon="info">{data.notice}</InfoNote>
          ) : null}

          {/* Choice 1: NSFAS */}
          <Card
            onPress={() => router.push('/course-finder/funding/nsfas')}
            style={styles.choiceCard}>
            <View style={styles.choiceHeader}>
              <View style={{ flex: 1, gap: 2 }}>
                <Overline>{t('courseFinder.nsfasTitle')}</Overline>
                {nsfas?.name ? <Title style={styles.choiceTitle}>{nsfas.name}</Title> : null}
              </View>
              {nsfas?.label ? (
                <Tag label={nsfas.label} tone={tagTone(nsfas.status)} />
              ) : null}
            </View>
            {nsfas ? (
              <View style={styles.metaRow}>
                <Muted>{nsfas.kind_label}</Muted>
                <Muted>·</Muted>
                <Muted>{nsfas.sector_label}</Muted>
              </View>
            ) : null}
            {nsfas?.lines?.length ? (
              <Text style={styles.line}>{nsfas.lines[0]}</Text>
            ) : (
              <Text style={styles.line}>{t('courseFinder.nsfasSubtitle')}</Text>
            )}
            <View style={styles.tapRow}>
              <Text style={styles.tapText}>{t('courseFinder.seeFunderDetails')}</Text>
              <Feather name="chevron-right" size={16} color={colors.accentDeep} />
            </View>
          </Card>

          {/* Choice 2: Other bursaries and loans */}
          <View style={{ gap: 12 }}>
            <Title style={styles.sectionTitle}>{t('courseFinder.otherFundingTitle')}</Title>

            {data.fields.length > 0 ? (
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chips}>
                {[['all', t('courseFinder.filterAll')], ...data.fields.map((f) => [f.id, f.label])].map(
                  ([val, label]) => {
                    const on = filter === val;
                    return (
                      <Pressable
                        key={val}
                        accessibilityRole="button"
                        accessibilityState={{ selected: on }}
                        onPress={() => setFilter(val)}
                        style={[styles.chip, on && styles.chipOn]}>
                        <Text style={[styles.chipText, on && styles.chipTextOn]}>{label}</Text>
                      </Pressable>
                    );
                  },
                )}
              </ScrollView>
            ) : null}

            {filter === 'all' && goalFieldLabel && hasGoalMatches ? (
              <InfoNote icon="award">
                {t('courseFinder.fundingGoalFirst', { field: goalFieldLabel })}
              </InfoNote>
            ) : null}

            <View style={{ gap: 10 }}>
              {displayedFunders.map((funder, i) => (
                <FadeIn key={funder.id} delay={Math.min(i, 8) * 30}>
                  <Card
                    onPress={() => router.push(`/course-finder/funding/${funder.id}`)}
                    style={styles.funderCard}>
                    <View style={styles.funderRow}>
                      <Strong style={styles.funderName}>{funder.name}</Strong>
                      <Tag label={funder.label} tone={tagTone(funder.status)} />
                    </View>
                    <View style={styles.metaRow}>
                      <Muted>{funder.kind_label}</Muted>
                      {funder.sector_label ? (
                        <>
                          <Muted>·</Muted>
                          <Muted>{funder.sector_label}</Muted>
                        </>
                      ) : null}
                    </View>
                    {funder.why ? <Text style={styles.whyLine}>{funder.why}</Text> : null}
                  </Card>
                </FadeIn>
              ))}
            </View>
          </View>
        </View>
      ) : null}
    </HeroScreen>
  );
}

const styles = StyleSheet.create({
  summary: { fontFamily: fonts.medium, fontSize: 14, color: colors.text },
  choiceCard: { gap: 8, padding: 16 },
  choiceHeader: { flexDirection: 'row', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8 },
  choiceTitle: { fontSize: 17, lineHeight: 22, color: colors.text },
  metaRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  line: { fontFamily: fonts.body, fontSize: 13.5, lineHeight: 20, color: colors.text },
  tapRow: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 4 },
  tapText: { fontFamily: fonts.semibold, fontSize: 13, color: colors.accentDeep },
  sectionTitle: { fontSize: 20, color: colors.text, marginTop: 4 },
  chips: { gap: 8, paddingRight: 8 },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.white,
  },
  chipOn: { backgroundColor: colors.ink, borderColor: colors.ink },
  chipText: { fontFamily: fonts.semibold, fontSize: 13, color: colors.ink },
  chipTextOn: { color: colors.pillText },
  funderCard: { gap: 6, padding: 14 },
  funderRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 8, flexWrap: 'wrap' },
  funderName: { flex: 1, fontSize: 14.5, color: colors.text },
  whyLine: { fontFamily: fonts.body, fontSize: 12.5, color: colors.textMuted },
});
