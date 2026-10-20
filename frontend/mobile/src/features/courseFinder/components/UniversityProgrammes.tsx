/**
 * One university's programmes by faculty, used on the Courses tab and the university's Courses screen.
 * With the learner's marks: what they meet first, with our tiers and "choose as my goal" (as before).
 * Without marks: every programme by faculty with its minimum points as published, and a nudge to add marks.
 */
import { router } from 'expo-router';
import { useEffect, useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { InfoNote } from '@/shared/components/Parts';
import { ErrorBox } from '@/shared/components/Status';
import { Body, Muted } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { FadeIn } from '@/shared/motion/FadeIn';
import { SkeletonCards } from '@/shared/motion/Shimmer';
import { colors, fonts, radius } from '@/shared/theme/tokens';

import { courseFinderApi } from '../api/courseFinderApi';
import { groupByFaculty, hasFaculties } from '../faculties';
import { checkRows } from '../marks';
import { useCourseFinder } from '../state';
import { Match, ProgrammeRow, Tier } from '../types';
import { errorText } from '../words';
import { FacultySection } from './FacultySection';
import { FacultyProgrammes } from './ProgrammeList';
import { TierCard } from './TierCard';

export function UniversityProgrammes({ id }: { id: string }) {
  const cf = useCourseFinder();
  const sent = useMemo(() => checkRows(cf.rows), [cf.rows]);
  const withMarks = sent.marks.length > 0 && !Object.keys(sent.errors).length;
  return withMarks ? <WithMarks id={id} /> : <WithoutMarks id={id} />;
}

function WithoutMarks({ id }: { id: string }) {
  const [rows, setRows] = useState<ProgrammeRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let live = true;
    courseFinderApi
      .programmes({ university: id })
      .then((a) => live && setRows(a.programmes))
      .catch((e) => live && setError(errorText(e)));
    return () => {
      live = false;
    };
  }, [id, attempt]);

  return (
    <View style={{ gap: 12 }}>
      <Pressable accessibilityRole="button" onPress={() => router.push('/course-finder/marks')}>
        <InfoNote icon="edit-3">{t('courses.addMarks')}</InfoNote>
      </Pressable>
      {error ? (
        <ErrorBox
          message={error}
          onRetry={() => {
            setError(null);
            setAttempt((n) => n + 1);
          }}
        />
      ) : null}
      {!rows && !error ? <SkeletonCards count={3} /> : null}
      {rows && !rows.length ? <Body>{t('courseFinder.programmesNotAdded')}</Body> : null}
      {rows?.length ? <FacultyProgrammes rows={rows} /> : null}
    </View>
  );
}

function WithMarks({ id }: { id: string }) {
  const cf = useCourseFinder();
  const sent = useMemo(() => checkRows(cf.rows), [cf.rows]);
  const [filter, setFilter] = useState<Tier | 'all'>('all');
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [picking, setPicking] = useState<string | null>(null);
  const { answer, setAnswer, setPlan } = cf;
  const here = answer && answer.university.id === id ? answer : null;

  useEffect(() => {
    if (here) return;
    courseFinderApi
      .assess(id, sent.marks)
      .then(setAnswer)
      .catch((e) => setError(errorText(e)));
  }, [id, here, setAnswer, sent.marks, attempt]);

  const matches = useMemo(() => here?.matches ?? [], [here]);
  const tiers = useMemo(() => {
    const seen = new Map<Tier, string>();
    for (const m of matches) if (!seen.has(m.tier)) seen.set(m.tier, m.label);
    return [...seen.entries()];
  }, [matches]);
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
    <View style={{ gap: 12 }}>
      <Muted>{t('courses.withMarks')}</Muted>
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
      {here && !matches.length ? <Body>{t('courseFinder.programmesNotAdded')}</Body> : null}
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
  );
}

const styles = StyleSheet.create({
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
});
