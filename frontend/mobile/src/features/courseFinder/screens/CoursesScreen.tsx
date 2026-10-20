/**
 * The Courses tab: pick a university to see its programmes by faculty (with your marks: what you meet
 * first), or search every programme by name or faculty. Never one long flat list.
 */
import { Feather } from '@expo/vector-icons';
import { useEffect, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';

import { Button } from '@/shared/components/Button';
import { HeroScreen } from '@/shared/components/HeroScreen';
import { ErrorBox } from '@/shared/components/Status';
import { Body, Muted } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { SkeletonCards } from '@/shared/motion/Shimmer';
import { colors, fonts, radius } from '@/shared/theme/tokens';

import { courseFinderApi } from '../api/courseFinderApi';
import { SearchResults } from '../components/ProgrammeList';
import { UniversityProgrammes } from '../components/UniversityProgrammes';
import { ProgrammeListAnswer, ProgrammeRow, UniversityCardInfo } from '../types';
import { errorText } from '../words';

const MIN_CHARS = 3;
const WAIT_MS = 350;

export default function CoursesScreen() {
  const [unis, setUnis] = useState<UniversityCardInfo[]>([]);
  const [uni, setUni] = useState<string | null>(null);
  const [typed, setTyped] = useState('');
  const [q, setQ] = useState('');

  useEffect(() => {
    courseFinderApi.universities().then(setUnis).catch(() => setUnis([]));
  }, []);

  useEffect(() => {
    const clean = typed.trim();
    const id = setTimeout(() => setQ(clean.length >= MIN_CHARS ? clean : ''), WAIT_MS);
    return () => clearTimeout(id);
  }, [typed]);

  return (
    <HeroScreen tab title={t('courses.title')} subtitle={t('courses.sub')}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chips}>
        {[[null, t('courses.all')] as const, ...unis.map((u) => [u.id, u.id.toUpperCase()] as const)].map(([id, label]) => {
          const on = id === uni;
          return (
            <Pressable
              key={id ?? 'all'}
              accessibilityRole="button"
              accessibilityLabel={id ? unis.find((u) => u.id === id)?.name ?? label : label}
              accessibilityState={{ selected: on }}
              onPress={() => setUni(id)}
              style={[styles.chip, on && styles.chipOn]}>
              <Text style={[styles.chipText, on && styles.chipTextOn]}>{label}</Text>
            </Pressable>
          );
        })}
      </ScrollView>

      <View style={styles.searchBox}>
        <Feather name="search" size={16} color={colors.textMuted} />
        <TextInput
          value={typed}
          onChangeText={setTyped}
          placeholder={t('courses.search')}
          placeholderTextColor={colors.textFaint}
          accessibilityLabel={t('courses.search')}
          autoCorrect={false}
          maxLength={120}
          returnKeyType="search"
          style={styles.searchInput}
        />
      </View>
      {typed.trim().length > 0 && typed.trim().length < MIN_CHARS ? <Muted>{t('colleges.searchHint')}</Muted> : null}

      {q ? <Search q={q} university={uni} /> : uni ? <UniversityProgrammes id={uni} /> : <Body>{t('courses.pick')}</Body>}
    </HeroScreen>
  );
}

function Search({ q, university }: { q: string; university: string | null }) {
  const [answer, setAnswer] = useState<ProgrammeListAnswer | null>(null);
  const [rows, setRows] = useState<ProgrammeRow[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let live = true;
    courseFinderApi
      .programmes({ q, university: university ?? undefined })
      .then((a) => {
        if (!live) return;
        setError(null);
        setAnswer(a);
        setRows(a.programmes);
      })
      .catch((e) => live && setError(errorText(e)));
    return () => {
      live = false;
    };
  }, [q, university]);

  async function more() {
    if (!answer) return;
    try {
      const next = await courseFinderApi.programmes({ q, university: university ?? undefined, page: answer.page + 1 });
      setAnswer(next);
      setRows((r) => [...r, ...next.programmes]);
    } catch (e) {
      setError(errorText(e));
    }
  }

  if (error) return <ErrorBox message={error} />;
  if (!answer) return <SkeletonCards count={3} />;
  return (
    <View style={{ gap: 12 }}>
      <Body style={styles.summary}>{answer.summary}</Body>
      <SearchResults rows={rows} />
      {answer.page < answer.pages ? <Button title={t('courses.more')} variant="secondary" icon="chevron-down" onPress={more} /> : null}
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
  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    height: 48,
    paddingHorizontal: 12,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.white,
  },
  searchInput: { flex: 1, height: 46, fontFamily: fonts.medium, fontSize: 15, color: colors.text },
  summary: { fontFamily: fonts.medium, fontSize: 14, color: colors.text },
});
