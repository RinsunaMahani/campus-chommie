import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { ComponentProps, useCallback, useEffect, useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { useSession } from '@/features/auth/session/SessionProvider';
import { Button } from '@/shared/components/Button';
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
import { FundingCard, FundingListAnswer, SavedFundingCard } from '../types';
import { errorText, formatDay } from '../words';

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

function useSignedIn(): boolean {
  try {
    return useSession().status === 'active';
  } catch {
    return false;
  }
}

/**
 * Funding options: Choice between NSFAS and other bursaries and loans, plus
 * saving funding when signed in.
 */
export default function FundingScreen() {
  const cf = useCourseFinder();
  const signedIn = useSignedIn();
  const [data, setData] = useState<FundingListAnswer | null>(null);
  const [savedList, setSavedList] = useState<SavedFundingCard[]>([]);
  const [signInPrompt, setSignInPrompt] = useState(false);
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

  useEffect(() => {
    if (!signedIn) return;
    courseFinderApi
      .savedFundingList()
      .then((res) => setSavedList(res.funders))
      .catch(() => undefined);
  }, [signedIn]);

  const activeSavedList = useMemo(() => (signedIn ? savedList : []), [signedIn, savedList]);

  const savedById = useMemo(() => {
    const map: Record<string, SavedFundingCard> = {};
    for (const f of activeSavedList) map[f.id] = f;
    return map;
  }, [activeSavedList]);

  const toggleSave = useCallback(
    async (funder: FundingCard) => {
      if (!signedIn) {
        setSignInPrompt(true);
        return;
      }
      const existing = savedById[funder.id];
      if (existing) {
        setSavedList((prev) => prev.filter((x) => x.id !== funder.id));
        try {
          await courseFinderApi.unsaveFunder(funder.id);
        } catch {
          setSavedList((prev) => [...prev, existing]);
        }
      } else {
        try {
          const saved = await courseFinderApi.saveFunder(funder.id);
          setSavedList((prev) => [...prev.filter((x) => x.id !== funder.id), saved]);
        } catch (e) {
          setError(errorText(e));
        }
      }
    },
    [signedIn, savedById],
  );

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
    if (filter === 'saved') return activeSavedList;
    if (filter === 'all') return sortedOthers;
    return otherFunders.filter(
      (f) => f.any_field || f.fields?.some((field) => field.id === filter),
    );
  }, [filter, activeSavedList, sortedOthers, otherFunders]);

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

          {signInPrompt && !signedIn ? (
            <Card style={styles.signInCard}>
              <Body>{t('courseFinder.saveSignInPrompt')}</Body>
              <Button
                title={t('courseFinder.saveSignInButton')}
                variant="accent"
                compact
                icon="log-in"
                onPress={() => router.push('/(auth)/sign-in')}
              />
            </Card>
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
              <View style={styles.actionsRow}>
                {nsfas?.label ? (
                  <Tag label={nsfas.label} tone={tagTone(nsfas.status)} />
                ) : null}
                {nsfas ? (
                  <Pressable
                    accessibilityRole="button"
                    accessibilityLabel={
                      savedById[nsfas.id]
                        ? t('courseFinder.unsaveFunder', { name: nsfas.name })
                        : t('courseFinder.saveFunder', { name: nsfas.name })
                    }
                    onPress={() => toggleSave(nsfas)}
                    style={[styles.saveBtn, !!savedById[nsfas.id] && styles.saveBtnOn]}>
                    <Feather
                      name="bookmark"
                      size={13}
                      color={savedById[nsfas.id] ? colors.pillText : colors.ink}
                    />
                    <Text style={[styles.saveText, !!savedById[nsfas.id] && styles.saveTextOn]}>
                      {savedById[nsfas.id] ? t('courseFinder.saved') : t('courseFinder.save')}
                    </Text>
                  </Pressable>
                ) : null}
              </View>
            </View>
            {nsfas ? (
              <View style={styles.metaRow}>
                <Muted>{nsfas.kind_label}</Muted>
                <Muted>·</Muted>
                <Muted>{nsfas.sector_label}</Muted>
              </View>
            ) : null}
            {savedById.nsfas?.saved_on ? (
              <Muted>{t('courseFinder.savedOn', { date: formatDay(savedById.nsfas.saved_on) })}</Muted>
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

            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chips}>
              {[
                ['all', t('courseFinder.filterAll')],
                ['saved', t('courseFinder.filterSaved')],
                ...data.fields.map((f) => [f.id, f.label]),
              ].map(([val, label]) => {
                const on = filter === val;
                return (
                  <Pressable
                    key={val}
                    accessibilityRole="button"
                    accessibilityLabel={label}
                    accessibilityState={{ selected: on }}
                    onPress={() => {
                      setFilter(val);
                      if (val === 'saved' && !signedIn) setSignInPrompt(true);
                    }}
                    style={[styles.chip, on && styles.chipOn]}>
                    <Text style={[styles.chipText, on && styles.chipTextOn]}>{label}</Text>
                  </Pressable>
                );
              })}
            </ScrollView>

            {filter === 'all' && goalFieldLabel && hasGoalMatches ? (
              <InfoNote icon="award">
                {t('courseFinder.fundingGoalFirst', { field: goalFieldLabel })}
              </InfoNote>
            ) : null}

            {filter === 'saved' && signedIn && displayedFunders.length === 0 ? (
              <InfoNote icon="bookmark">{t('courseFinder.savedEmpty')}</InfoNote>
            ) : null}

            <View style={{ gap: 10 }}>
              {displayedFunders.map((funder, i) => {
                const savedEntry = savedById[funder.id];
                const isSaved = !!savedEntry;
                const savedOnDate = (funder as SavedFundingCard).saved_on ?? savedEntry?.saved_on;
                return (
                  <FadeIn key={funder.id} delay={Math.min(i, 8) * 30}>
                    <Card
                      onPress={() => router.push(`/course-finder/funding/${funder.id}`)}
                      style={styles.funderCard}>
                      <View style={styles.funderRow}>
                        <Strong style={styles.funderName}>{funder.name}</Strong>
                        <View style={styles.actionsRow}>
                          <Tag label={funder.label} tone={tagTone(funder.status)} />
                          <Pressable
                            accessibilityRole="button"
                            accessibilityLabel={
                              isSaved
                                ? t('courseFinder.unsaveFunder', { name: funder.name })
                                : t('courseFinder.saveFunder', { name: funder.name })
                            }
                            onPress={() => toggleSave(funder)}
                            style={[styles.saveBtn, isSaved && styles.saveBtnOn]}>
                            <Feather
                              name="bookmark"
                              size={13}
                              color={isSaved ? colors.pillText : colors.ink}
                            />
                            <Text style={[styles.saveText, isSaved && styles.saveTextOn]}>
                              {isSaved ? t('courseFinder.saved') : t('courseFinder.save')}
                            </Text>
                          </Pressable>
                        </View>
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
                      {savedOnDate ? (
                        <Muted>{t('courseFinder.savedOn', { date: formatDay(savedOnDate) })}</Muted>
                      ) : null}
                      {funder.why ? <Text style={styles.whyLine}>{funder.why}</Text> : null}
                    </Card>
                  </FadeIn>
                );
              })}
            </View>
          </View>
        </View>
      ) : null}
    </HeroScreen>
  );
}

const styles = StyleSheet.create({
  summary: { fontFamily: fonts.medium, fontSize: 14, color: colors.text },
  signInCard: { gap: 10, padding: 14 },
  choiceCard: { gap: 8, padding: 16 },
  choiceHeader: { flexDirection: 'row', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8 },
  choiceTitle: { fontSize: 17, lineHeight: 22, color: colors.text },
  actionsRow: { flexDirection: 'row', alignItems: 'center', gap: 6, flexWrap: 'wrap' },
  saveBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.white,
  },
  saveBtnOn: { backgroundColor: colors.ink, borderColor: colors.ink },
  saveText: { fontFamily: fonts.semibold, fontSize: 12, color: colors.ink },
  saveTextOn: { color: colors.pillText },
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
