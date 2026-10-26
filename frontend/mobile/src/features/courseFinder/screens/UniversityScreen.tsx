import { Redirect, router, useLocalSearchParams } from 'expo-router';
import { useEffect, useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { Card, Tag } from '@/shared/components/Parts';
import { PhotoHero } from '@/shared/components/PhotoHero';
import { ErrorBox } from '@/shared/components/Status';
import { Body, Overline } from '@/shared/components/Text';
import { UniMonogram } from '@/shared/components/UniMonogram';
import { t } from '@/shared/i18n';
import { FadeIn } from '@/shared/motion/FadeIn';
import { SkeletonCards } from '@/shared/motion/Shimmer';
import { SlidingTabs } from '@/shared/motion/SlidingTabs';
import { Palette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import { courseFinderApi } from '../api/courseFinderApi';
import { ApplyWindows, GuideCard } from '../components/ApplyBox';
import { ApsCard } from '../components/ApsCard';
import { FacultySection } from '../components/FacultySection';
import { TestDateNote } from '../components/StillOpen';
import { TierCard } from '../components/TierCard';
import { groupByFaculty, hasFaculties } from '../faculties';
import { CAMPUS_PHOTOS } from '../campusPhotos';
import { checkRows } from '../marks';
import { useCourseFinder } from '../state';
import { Match, Tier } from '../types';
import { errorText } from '../words';

/**
 * Step 3: one university, opening on its campus photo (where we have one). Its
 * name, where it is, its type and how many programmes; your points there,
 * opening to each subject; then its programmes grouped by faculty (best first),
 * and how to apply there today, on two sliding tabs.
 * Choosing a programme as the goal builds the three-choice plan.
 */
export default function UniversityScreen() {
  const styles = useStyles(makeStyles);
  const { id } = useLocalSearchParams<{ id: string }>();
  const cf = useCourseFinder();
  const sent = useMemo(() => checkRows(cf.rows), [cf.rows]);
  const valid = sent.marks.length > 0 && !Object.keys(sent.errors).length;
  const [tab, setTab] = useState(0);
  const [filter, setFilter] = useState<Tier | 'all'>('all');
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [picking, setPicking] = useState<string | null>(null);
  const { answer, setAnswer, setPlan } = cf;
  const here = answer && answer.university.id === id ? answer : null;
  const points = cf.points?.universities.find((u) => u.university === id) ?? null;

  useEffect(() => {
    if (!valid || !id || here) return;
    courseFinderApi
      .assess(id, sent.marks)
      .then(setAnswer)
      .catch((e) => setError(errorText(e)));
  }, [valid, id, here, setAnswer, sent.marks, attempt]);

  const matches = useMemo(() => here?.matches ?? [], [here]);
  // One chip per tier the learner actually has, named as the server names it.
  const tiers = useMemo(() => {
    const seen = new Map<Tier, string>();
    for (const m of matches) if (!seen.has(m.tier)) seen.set(m.tier, m.label);
    return [...seen.entries()];
  }, [matches]);

  if (!valid || !id) return <Redirect href="/course-finder" />;
  const shown = filter === 'all' ? matches : matches.filter((m) => m.tier === filter);
  const groups = hasFaculties(shown) ? groupByFaculty(shown) : null;

  async function pick(match: Match) {
    setPicking(match.programme);
    setError(null);
    try {
      setPlan(await courseFinderApi.plan(id, match.programme, sent.marks));
      router.push('/course-finder/plan');
    } catch (e) {
      setError(errorText(e));
    } finally {
      setPicking(null);
    }
  }

  return (
    <PhotoHero
      photo={CAMPUS_PHOTOS[id]}
      head={
        <>
          <Text style={styles.step}>{t('courseFinder.step', { n: 3 })}</Text>
          <View style={styles.titleRow}>
            <UniMonogram id={id} size={48} />
            <Text style={styles.title} accessibilityRole="header">
              {here?.university.name ?? points?.university_name ?? ''}
            </Text>
          </View>
          {here ? (
            <View style={styles.chipRow}>
              {[here.university.city, here.university.province].filter(Boolean).length ? (
                <Tag label={[here.university.city, here.university.province].filter(Boolean).join(', ')} tone="info" />
              ) : null}
              {here.university.institution_type_label ? <Tag label={here.university.institution_type_label} tone="info" /> : null}
              <Tag label={t('courseFinder.programmesChip', { n: matches.length })} tone="jade" />
            </View>
          ) : null}
        </>
      }>
      {points ? <ApsCard points={points} sent={sent} rows={cf.rows} /> : null}
      <SlidingTabs tabs={[t('courseFinder.tabCourses'), t('courseFinder.tabApply')]} index={tab} onChange={setTab} />

      {error ? (
        <ErrorBox
          message={error}
          onRetry={() => {
            setError(null);
            setAttempt((n) => n + 1);
          }}
        />
      ) : null}
      {!here && !error ? <SkeletonCards count={3} /> : null}

      {here && tab === 0 ? (
        <View style={{ gap: 12 }}>
          {tiers.length > 1 ? (
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chips}>
              {[['all', t('courseFinder.filterAll')] as const, ...tiers].map(([value, label]) => {
                const on = filter === value;
                return (
                  <Pressable
                    key={value}
                    accessibilityRole="button"
                    accessibilityState={{ selected: on }}
                    onPress={() => setFilter(value)}
                    style={[styles.chip, on && styles.chipOn]}>
                    <Text style={[styles.chipText, on && styles.chipTextOn]}>{label}</Text>
                  </Pressable>
                );
              })}
            </ScrollView>
          ) : null}
          {!matches.length ? <Body>{t('courseFinder.programmesNotAdded')}</Body> : null}
          {matches.length > 0 && !shown.length ? <Body>{t('courseFinder.noMatches')}</Body> : null}
          {groups
            ? groups.map((g, i) => (
                <FadeIn key={g.faculty ?? '-'} delay={Math.min(i, 6) * 40}>
                  <FacultySection group={g} startOpen={i === 0}>
                    {g.matches.map((m) => (
                      <TierCard key={m.programme} match={m} onPick={() => pick(m)} picking={picking === m.programme} />
                    ))}
                  </FacultySection>
                </FadeIn>
              ))
            : shown.map((m, i) => (
                <FadeIn key={m.programme} delay={Math.min(i, 6) * 40}>
                  <TierCard match={m} onPick={() => pick(m)} picking={picking === m.programme} />
                </FadeIn>
              ))}
        </View>
      ) : null}

      {here && tab === 1 ? (
        <View style={{ gap: 12 }}>
          <TestDateNote apply={here.apply} />
          <Card style={{ gap: 12 }}>
            <Overline>{t('courseFinder.applyDates')}</Overline>
            <ApplyWindows windows={here.apply.guide.windows} />
          </Card>
          <GuideCard guide={here.apply.guide} />
        </View>
      ) : null}
    </PhotoHero>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
  step: { fontFamily: fonts.bold, fontSize: 13, letterSpacing: 0.8, textTransform: 'uppercase', color: colors.accentDeep },
  titleRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  title: { flex: 1, fontFamily: fonts.display, fontSize: 28, lineHeight: 33, letterSpacing: -0.4, color: colors.ink },
  chipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  // "Not confirmed" said once, quietly: one line, not a box.
  quiet: { flexDirection: 'row', alignItems: 'center', gap: 6 },
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
});
