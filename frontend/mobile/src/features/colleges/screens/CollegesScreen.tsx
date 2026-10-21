/**
 * Colleges: public TVET colleges and DHET's registers of private institutions, searchable by name,
 * registration number or course ("electrician"), filtered by kind and province, a page at a time.
 * "Is this college registered?" sits on top: the check a learner needs before paying anyone.
 * Nothing is stored; a search is only a college's name or a course.
 */
import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useEffect, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';

import { errorText } from '@/features/courseFinder/words';
import { Button } from '@/shared/components/Button';
import { HeroScreen } from '@/shared/components/HeroScreen';
import { Card, InfoNote } from '@/shared/components/Parts';
import { ErrorBox } from '@/shared/components/Status';
import { Body, Muted, Strong } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { FadeIn } from '@/shared/motion/FadeIn';
import { SkeletonCards } from '@/shared/motion/Shimmer';
import { colors, fonts, radius } from '@/shared/theme/tokens';

import { collegesApi } from '../api/collegesApi';
import { CollegeRow } from '../CollegeRow';
import { CollegeCard, CollegeKind, CollegeListAnswer } from '../types';

const PROVINCES = ['Eastern Cape', 'Free State', 'Gauteng', 'KwaZulu-Natal', 'Limpopo', 'Mpumalanga', 'North West', 'Northern Cape', 'Western Cape'];
const MIN_CHARS = 3;
const WAIT_MS = 350;

export default function CollegesScreen() {
  const [typed, setTyped] = useState('');
  const [q, setQ] = useState('');
  const [kind, setKind] = useState<CollegeKind | undefined>(undefined);
  const [province, setProvince] = useState<string | undefined>(undefined);
  const [answer, setAnswer] = useState<CollegeListAnswer | null>(null);
  const [shown, setShown] = useState<CollegeCard[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  // Search a moment after typing stops, and only once there's enough to search for.
  useEffect(() => {
    const clean = typed.trim();
    const next = clean.length >= MIN_CHARS ? clean : '';
    const id = setTimeout(() => setQ(next), WAIT_MS);
    return () => clearTimeout(id);
  }, [typed]);

  useEffect(() => {
    let live = true;
    collegesApi
      .list({ q: q || undefined, kind, province })
      .then((a) => {
        if (!live) return;
        setError(null);
        setAnswer(a);
        setShown(a.colleges);
      })
      .catch((e) => live && setError(errorText(e)));
    return () => {
      live = false;
    };
  }, [q, kind, province, attempt]);

  async function more() {
    if (!answer) return;
    try {
      const next = await collegesApi.list({ q: q || undefined, kind, province, page: answer.page + 1 });
      setAnswer(next);
      setShown((s) => [...s, ...next.colleges]);
    } catch (e) {
      setError(errorText(e));
    }
  }

  const kinds: [CollegeKind | undefined, string][] = [
    [undefined, t('colleges.kindAll')],
    ['tvet', t('colleges.kindTvet')],
    ['private_higher_education', t('colleges.kindHigher')],
    ['private_college', t('colleges.kindPrivate')],
  ];

  return (
    <HeroScreen back title={t('colleges.title')} subtitle={t('colleges.sub')}>
      <Card onPress={() => router.push('/course-finder/colleges/check')} style={styles.checkCard}>
        <View style={styles.checkIcon}>
          <Feather name="shield" size={20} color={colors.ink} />
        </View>
        <View style={{ flex: 1, gap: 2 }}>
          <Strong style={styles.checkTitle}>{t('colleges.checkTitle')}</Strong>
          <Muted>{t('colleges.checkEntrySub')}</Muted>
        </View>
        <Feather name="chevron-right" size={18} color={colors.accentDeep} />
      </Card>

      <View style={styles.searchBox}>
        <Feather name="search" size={16} color={colors.textMuted} />
        <TextInput
          value={typed}
          onChangeText={setTyped}
          placeholder={t('colleges.search')}
          placeholderTextColor={colors.textFaint}
          accessibilityLabel={t('colleges.search')}
          autoCorrect={false}
          maxLength={120}
          returnKeyType="search"
          style={styles.searchInput}
        />
      </View>
      {typed.trim().length > 0 && typed.trim().length < MIN_CHARS ? <Muted>{t('colleges.searchHint')}</Muted> : null}

      <Chips items={kinds} value={kind} onChange={setKind} />
      <Chips items={[[undefined, t('colleges.provinceAll')], ...PROVINCES.map((p) => [p, p] as [string, string])]} value={province} onChange={setProvince} />

      {error ? (
        <ErrorBox
          message={error}
          onRetry={() => {
            setError(null);
            setAttempt((n) => n + 1);
          }}
        />
      ) : null}
      {!answer && !error ? <SkeletonCards count={4} /> : null}

      {answer ? (
        <View style={{ gap: 10 }}>
          <Body style={styles.summary}>{answer.summary}</Body>
          {!answer.confirmed && answer.notice ? <InfoNote icon="info">{answer.notice}</InfoNote> : null}
          {shown.map((c, i) => (
            <FadeIn key={c.id} delay={Math.min(i, 8) * 30}>
              <CollegeRow college={c} />
            </FadeIn>
          ))}
          {answer.page < answer.pages ? <Button title={t('colleges.more')} variant="secondary" icon="chevron-down" onPress={more} /> : null}
        </View>
      ) : null}
    </HeroScreen>
  );
}

function Chips<T extends string | undefined>({ items, value, onChange }: { items: [T, string][]; value: T; onChange: (v: T) => void }) {
  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chips}>
      {items.map(([v, label]) => {
        const on = v === value;
        return (
          <Pressable
            key={label}
            accessibilityRole="button"
            accessibilityState={{ selected: on }}
            onPress={() => onChange(v)}
            style={[styles.chip, on && styles.chipOn]}>
            <Text style={[styles.chipText, on && styles.chipTextOn]}>{label}</Text>
          </Pressable>
        );
      })}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  checkCard: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 14 },
  checkIcon: {
    width: 40,
    height: 40,
    borderRadius: radius.sm,
    backgroundColor: colors.iconTile,
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkTitle: { fontSize: 16, color: colors.text },
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
  searchInput: { flex: 1, height: 46, fontFamily: fonts.medium, fontSize: 16, color: colors.text },
  summary: { fontFamily: fonts.medium, fontSize: 15, color: colors.text },
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
