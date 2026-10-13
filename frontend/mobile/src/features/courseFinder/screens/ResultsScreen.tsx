import { Redirect, router } from 'expo-router';
import { useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { Body, Overline, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { colors, fonts, radius } from '@/shared/theme/tokens';

import { courseFinderApi } from '../api/courseFinderApi';
import { checkRows } from '../marks';
import { ErrorBox } from '@/shared/components/Status';
import { TierCard } from '../components/TierCard';
import { useCourseFinder } from '../state';
import { Match, Tier } from '../types';
import { errorText } from '../words';

/** Step 3: every programme at the university, best matches first, each with its reasons and source. */
export default function ResultsScreen() {
  const cf = useCourseFinder();
  const [filter, setFilter] = useState<Tier | 'all'>('all');
  const [picking, setPicking] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const matches = useMemo(() => cf.answer?.matches ?? [], [cf.answer]);
  // One chip per tier the learner actually has, named as the server names it.
  const tiers = useMemo(() => {
    const seen = new Map<Tier, string>();
    for (const m of matches) if (!seen.has(m.tier)) seen.set(m.tier, m.label);
    return [...seen.entries()];
  }, [matches]);

  if (!cf.answer || !cf.university) return <Redirect href="/course-finder" />;
  const university = cf.university;
  const shown = filter === 'all' ? matches : matches.filter((m) => m.tier === filter);

  async function pick(match: Match) {
    setPicking(match.programme);
    setError(null);
    try {
      const plan = await courseFinderApi.plan(university.id, match.programme, checkRows(cf.rows).marks);
      cf.setPlan(plan);
      router.push('/course-finder/plan');
    } catch (e) {
      setError(errorText(e));
    } finally {
      setPicking(null);
    }
  }

  return (
    <Screen back>
      <View style={{ gap: 6 }}>
        <Overline>{t('courseFinder.step', { n: 3 })}</Overline>
        <Title>{t('courseFinder.results')}</Title>
        <Body>{t('courseFinder.resultsCount', { n: matches.length, university: cf.answer.university.name })}</Body>
      </View>
      {!cf.answer.university.confirmed && cf.answer.university.notice ? (
        <InfoNote icon="alert-circle">{cf.answer.university.notice}</InfoNote>
      ) : null}

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

      {error ? <ErrorBox message={error} /> : null}
      {!shown.length ? <Body>{t('courseFinder.noMatches')}</Body> : null}
      {shown.map((m) => (
        <TierCard key={m.programme} match={m} onPick={() => pick(m)} picking={picking === m.programme} />
      ))}
    </Screen>
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
  chipTextOn: { color: colors.white },
});
