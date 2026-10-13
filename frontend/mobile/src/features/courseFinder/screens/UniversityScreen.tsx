import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useCallback, useEffect, useState } from 'react';
import { StyleSheet, View } from 'react-native';

import { Card, InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { Body, Muted, Overline, Strong, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { colors } from '@/shared/theme/tokens';

import { courseFinderApi } from '../api/courseFinderApi';
import { ErrorBox, Loading } from '../components/Status';
import { useCourseFinder } from '../state';
import { UniversitySummary } from '../types';
import { errorText } from '../words';

/** Step 1: which university. Open to anyone, signed in or not. */
export default function UniversityScreen() {
  const cf = useCourseFinder();
  const [list, setList] = useState<UniversitySummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    courseFinderApi
      .universities()
      .then(setList)
      .catch((e) => setError(errorText(e)));
  }, []);

  useEffect(load, [load]);

  function retry() {
    setError(null);
    setList(null);
    load();
  }

  function choose(u: UniversitySummary) {
    cf.chooseUniversity(u);
    router.push('/course-finder/marks');
  }

  return (
    <Screen back>
      <View style={{ gap: 6 }}>
        <Overline>{t('courseFinder.step', { n: 1 })}</Overline>
        <Title>{t('courseFinder.title')}</Title>
        <Body>{t('courseFinder.intro')}</Body>
      </View>
      <InfoNote icon="lock">{`${t('courseFinder.nothingStored')} ${t('courseFinder.noAccount')}`}</InfoNote>

      <Strong>{t('courseFinder.universityPick')}</Strong>
      {error ? <ErrorBox message={error} onRetry={retry} /> : null}
      {!error && !list ? <Loading /> : null}
      {list && !list.length ? <Body>{t('courseFinder.noUniversities')}</Body> : null}
      {list?.map((u) => (
        <Card key={u.id} onPress={() => choose(u)} style={styles.card}>
          <View style={{ flex: 1, gap: 2 }}>
            <Strong>{u.name}</Strong>
            <Muted>{[u.city, t('courseFinder.programmes', { n: u.programmes })].filter(Boolean).join(' · ')}</Muted>
            {!u.confirmed && u.notice ? <Muted style={{ color: colors.marigoldDeep }}>{u.notice}</Muted> : null}
          </View>
          <Feather name="chevron-right" size={18} color={colors.textFaint} />
        </Card>
      ))}
    </Screen>
  );
}

const styles = StyleSheet.create({
  card: { flexDirection: 'row', alignItems: 'center', gap: 12 },
});
