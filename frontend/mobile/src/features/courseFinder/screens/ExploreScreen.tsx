/**
 * Explore: universities and colleges, side by side behind a toggle. Universities with their campus photo,
 * fee and where applications stand today (search by name or city); colleges as DHET lists them, with the
 * registration check.
 */
import { useEffect, useMemo, useState } from 'react';
import { StyleSheet, TextInput, View } from 'react-native';
import { Feather } from '@expo/vector-icons';

import { CollegesBody } from '@/features/colleges/screens/CollegesScreen';
import { HeroScreen } from '@/shared/components/HeroScreen';
import { InfoNote } from '@/shared/components/Parts';
import { Segmented } from '@/shared/components/Segmented';
import { ErrorBox } from '@/shared/components/Status';
import { Muted } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { FadeIn } from '@/shared/motion/FadeIn';
import { SkeletonCards } from '@/shared/motion/Shimmer';
import { colors, fonts, radius } from '@/shared/theme/tokens';

import { courseFinderApi } from '../api/courseFinderApi';
import { UniversityCard } from '../components/UniversityCard';
import { UniversityCardInfo } from '../types';
import { errorText } from '../words';

type Side = 'universities' | 'colleges';

export default function ExploreScreen() {
  const [side, setSide] = useState<Side>('universities');
  return (
    <HeroScreen
      tab
      title={t('explore.title')}
      subtitle={t('explore.sub')}
      band={
        <Segmented<Side>
          options={[
            ['universities', t('explore.universities')],
            ['colleges', t('explore.colleges')],
          ]}
          value={side}
          onChange={setSide}
        />
      }>
      {side === 'universities' ? <Universities /> : <CollegesBody />}
    </HeroScreen>
  );
}

function Universities() {
  const [all, setAll] = useState<UniversityCardInfo[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [q, setQ] = useState('');

  useEffect(() => {
    courseFinderApi
      .universities()
      .then(setAll)
      .catch((e) => setError(errorText(e)));
  }, [attempt]);

  const shown = useMemo(() => {
    const words = q.trim().toLowerCase().split(/\s+/).filter(Boolean);
    if (!all || !words.length) return all ?? [];
    return all.filter((u) => {
      const text = `${u.name} ${u.id} ${u.city ?? ''}`.toLowerCase();
      return words.every((w) => text.includes(w));
    });
  }, [all, q]);

  return (
    <View style={{ gap: 12 }}>
      <View style={styles.searchBox}>
        <Feather name="search" size={16} color={colors.textMuted} />
        <TextInput
          value={q}
          onChangeText={setQ}
          placeholder={t('explore.search')}
          placeholderTextColor={colors.textFaint}
          accessibilityLabel={t('explore.search')}
          autoCorrect={false}
          maxLength={60}
          style={styles.searchInput}
        />
      </View>
      {error ? (
        <ErrorBox
          message={error}
          onRetry={() => {
            setError(null);
            setAttempt((n) => n + 1);
          }}
        />
      ) : null}
      {!all && !error ? <SkeletonCards count={3} /> : null}
      {all && all[0] && !all[0].confirmed && all[0].notice ? <InfoNote icon="info">{all[0].notice}</InfoNote> : null}
      {all && !shown.length ? <Muted>{t('explore.none')}</Muted> : null}
      {shown.map((u, i) => (
        <FadeIn key={u.id} delay={Math.min(i, 6) * 30}>
          <UniversityCard u={u} />
        </FadeIn>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
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
});
