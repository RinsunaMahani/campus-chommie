import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { ComponentProps, useCallback, useEffect, useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { useSession } from '@/features/auth/session/SessionProvider';
import { Button } from '@/shared/components/Button';
import { EmptyState } from '@/shared/components/EmptyState';
import { HeroScreen } from '@/shared/components/HeroScreen';
import { Card, InfoNote, Tag } from '@/shared/components/Parts';
import { Section } from '@/shared/components/Section';
import { ErrorBox } from '@/shared/components/Status';
import { Body, Muted, Overline, Strong, Title } from '@/shared/components/Text';
import { Monogram } from '@/shared/components/UniMonogram';
import { t } from '@/shared/i18n';
import { FadeIn } from '@/shared/motion/FadeIn';
import { SkeletonCards } from '@/shared/motion/Shimmer';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import { courseFinderApi } from '../api/courseFinderApi';
import { funderMonogram } from '../funderPhotos';
import { useCourseFinder } from '../state';
import { FundingCard, FundingListAnswer, FundingSection, SavedFundingCard } from '../types';
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

/** "Bursary · Government": what kind of funding and who runs it. */
function Meta({ funder }: { funder: FundingCard }) {
  const styles = useStyles(makeStyles);
  return (
    <View style={styles.metaRow}>
      <Muted>{funder.kind_label}</Muted>
      {funder.sector_label ? (
        <>
          <Muted>·</Muted>
          <Muted>{funder.sector_label}</Muted>
        </>
      ) : null}
    </View>
  );
}

function SaveButton({ funder, saved, onPress }: { funder: FundingCard; saved: boolean; onPress: () => void }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={
        saved ? t('courseFinder.unsaveFunder', { name: funder.name }) : t('courseFinder.saveFunder', { name: funder.name })
      }
      onPress={onPress}
      hitSlop={6}
      style={[styles.saveBtn, saved && styles.saveBtnOn]}>
      <Feather name="bookmark" size={13} color={saved ? colors.pillText : colors.ink} />
      <Text style={[styles.saveText, saved && styles.saveTextOn]}>
        {saved ? t('courseFinder.saved') : t('courseFinder.save')}
      </Text>
    </Pressable>
  );
}

type FeatherName = ComponentProps<typeof Feather>['name'];

/** Each group's icon: who offers the funding. */
const SECTION_ICONS: Record<string, FeatherName> = {
  missing_middle: 'trending-up',
  government: 'flag',
  company: 'briefcase',
  non_profit: 'heart',
  university: 'book-open',
};

/** One funder: its tile, name, kind, status with Save on one line, then why it's here. */
function FunderRow({
  funder,
  saved,
  savedOn,
  onSave,
  showIncome,
}: {
  funder: FundingCard;
  saved: boolean;
  savedOn?: string;
  onSave: () => void;
  showIncome?: boolean;
}) {
  const styles = useStyles(makeStyles);
  return (
    <Card onPress={() => router.push(`/course-finder/funding/${funder.id}`)} style={styles.funderCard}>
      <View style={styles.cardRow}>
        <Monogram label={funderMonogram(funder)} size={44} />
        <View style={styles.cardBody}>
          <Strong style={styles.funderName}>{funder.name}</Strong>
          <Meta funder={funder} />
          <View style={styles.statusRow}>
            <Tag label={funder.label} tone={tagTone(funder.status)} />
            <SaveButton funder={funder} saved={saved} onPress={onSave} />
          </View>
          {savedOn ? <Muted>{t('courseFinder.savedOn', { date: formatDay(savedOn) })}</Muted> : null}
          {funder.why ? <Text style={styles.whyLine}>{funder.why}</Text> : null}
          {showIncome && funder.income_says ? (
            <Text style={styles.whyLine}>{t('courseFinder.incomeRule', { says: funder.income_says })}</Text>
          ) : null}
        </View>
      </View>
    </Card>
  );
}

/**
 * Funding options: Choice between NSFAS and other bursaries and loans, plus
 * saving funding when signed in. "All" shows the list in groups (who offers it, and the
 * missing middle), so it never scrolls on and on; Saved and a field show one short list.
 */
export default function FundingScreen() {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
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

  /** A group's funders, in the list's order; the goal's field first, as in the flat list. */
  const byId = useMemo(() => new Map((data?.funders ?? []).map((f) => [f.id, f])), [data]);
  const groupFunders = useCallback(
    (section: FundingSection) => {
      const list = section.funder_ids.map((id) => byId.get(id)).filter((f): f is FundingCard => !!f);
      if (!goalFields.length) return list;
      return [...list.filter((f) => matchesGoalField(f, goalFields)), ...list.filter((f) => !matchesGoalField(f, goalFields))];
    },
    [byId, goalFields],
  );

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
            <View style={styles.cardRow}>
              <Monogram label={nsfas ? funderMonogram(nsfas) : 'NSFAS'} size={48} />
              <View style={styles.cardBody}>
                <Overline>{t('courseFinder.nsfasTitle')}</Overline>
                {nsfas?.name ? <Title style={styles.choiceTitle}>{nsfas.name}</Title> : null}
                {nsfas ? (
                  <>
                    <Meta funder={nsfas} />
                    <View style={styles.statusRow}>
                      <Tag label={nsfas.label} tone={tagTone(nsfas.status)} />
                      <SaveButton funder={nsfas} saved={!!savedById[nsfas.id]} onPress={() => toggleSave(nsfas)} />
                    </View>
                  </>
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
              </View>
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
              <EmptyState
                icon="bookmark"
                title={t('courseFinder.savedEmptyTitle')}
                body={t('courseFinder.savedEmpty')}
                action={{ label: t('courseFinder.browseAll'), icon: 'search', onPress: () => setFilter('all') }}
              />
            ) : null}

            {filter === 'all' && data.sections?.length ? (
              <View>
                {[...(data.missing_middle ? [data.missing_middle] : []), ...data.sections].map((section, i) => (
                  <Section
                    key={section.id}
                    first={i === 0}
                    title={section.title}
                    summary={section.line}
                    icon={SECTION_ICONS[section.id] ?? 'folder'}>
                    {section.id === 'missing_middle' ? <Muted>{t('courseFinder.missingMiddleNote')}</Muted> : null}
                    {groupFunders(section).map((funder) => (
                      <FunderRow
                        key={funder.id}
                        funder={funder}
                        saved={!!savedById[funder.id]}
                        savedOn={savedById[funder.id]?.saved_on}
                        onSave={() => toggleSave(funder)}
                        showIncome={section.id === 'missing_middle'}
                      />
                    ))}
                  </Section>
                ))}
              </View>
            ) : (
              <View style={{ gap: 10 }}>
                {displayedFunders.map((funder, i) => (
                  <FadeIn key={funder.id} delay={Math.min(i, 8) * 30}>
                    <FunderRow
                      funder={funder}
                      saved={!!savedById[funder.id]}
                      savedOn={(funder as SavedFundingCard).saved_on ?? savedById[funder.id]?.saved_on}
                      onSave={() => toggleSave(funder)}
                    />
                  </FadeIn>
                ))}
              </View>
            )}
          </View>
        </View>
      ) : null}
    </HeroScreen>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
  summary: { fontFamily: fonts.medium, fontSize: 15, color: colors.text },
  signInCard: { gap: 10, padding: 14 },
  choiceCard: { gap: 8, padding: 16 },
  choiceTitle: { fontSize: 17, lineHeight: 22, color: colors.text },
  // Every card: the tile on the left, then name, kind, and status with Save on one line, all on one edge.
  cardRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 12 },
  cardBody: { flex: 1, gap: 6 },
  statusRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 8 },
  saveBtn: {
    flexShrink: 0,
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
  saveText: { fontFamily: fonts.semibold, fontSize: 13, color: colors.ink },
  saveTextOn: { color: colors.pillText },
  metaRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  line: { fontFamily: fonts.body, fontSize: 14.5, lineHeight: 20, color: colors.text },
  tapRow: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 4 },
  tapText: { fontFamily: fonts.semibold, fontSize: 14, color: colors.accentDeep },
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
  chipText: { fontFamily: fonts.semibold, fontSize: 14, color: colors.ink },
  chipTextOn: { color: colors.pillText },
  funderCard: { gap: 6, padding: 14 },
  funderName: { fontSize: 16, lineHeight: 20, color: colors.text },
  whyLine: { fontFamily: fonts.body, fontSize: 13.5, color: colors.textMuted },
});
