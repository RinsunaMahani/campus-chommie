import { useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { ActivityIndicator, View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Screen } from '@/shared/components/Screen';
import { SelectField } from '@/shared/components/SelectField';
import { Body, Muted, Overline, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { takeUniversity } from '@/shared/lib/chosenUniversity';
import { colors } from '@/shared/theme/tokens';

import { profileApi } from '../api/profileApi';
import { useProfile } from '../state';
import { Campus, UniversityChoice } from '../types';

/**
 * Onboarding, step 2: university and campus. Saving it ends onboarding: the
 * signed-in layout then opens the tabs by itself.
 */
export default function CampusScreen() {
  const { university: universityParam } = useLocalSearchParams<{ university?: string }>();
  const { setProfile } = useProfile();
  const [universities, setUniversities] = useState<UniversityChoice[] | null>(null);
  const [university, setUniversity] = useState<string | null>(null);
  const [campuses, setCampuses] = useState<Campus[] | null>(null);
  const [campus, setCampus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    profileApi
      .universities()
      .then((list) => {
        setUniversities(list);
        // From the course finder: a route parameter, or the id it remembered before sign-up.
        const wanted = universityParam ?? takeUniversity();
        if (wanted && list.some((u) => u.id === wanted)) {
          chooseUniversity(wanted);
        }
      })
      .catch((e) => setError(errorText(e, t('common.error'))));
  }, [universityParam]);

  function chooseUniversity(id: string) {
    setUniversity(id);
    setCampus(null);
    setCampuses(null);
    setError(null);
    profileApi
      .campuses(id)
      .then((list) => {
        setCampuses(list);
        // One campus: nothing to choose.
        if (list.length === 1) setCampus(list[0].id);
      })
      .catch((e) => setError(errorText(e, t('common.error'))));
  }

  async function finish() {
    if (!university) return setError(t('onboarding.needUniversity'));
    if (campuses && campuses.length > 1 && !campus) return setError(t('onboarding.needCampus'));
    setBusy(true);
    setError(null);
    try {
      setProfile(await profileApi.save(university, campus));
    } catch (e) {
      setError(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Screen back footer={<Button title={t('onboarding.finish')} variant="accent" onPress={finish} loading={busy} />}>
      <View style={{ gap: 6 }}>
        <Overline>{t('onboarding.step', { n: 2 })}</Overline>
        <Title>{t('onboarding.campusTitle')}</Title>
        <Body>{t('onboarding.campusIntro')}</Body>
      </View>
      {universities ? (
        <SelectField
          label={t('onboarding.university')}
          placeholder={t('onboarding.pickUniversity')}
          value={university}
          options={universities.map((u) => ({ value: u.id, label: u.name }))}
          onChange={chooseUniversity}
        />
      ) : !error ? (
        <ActivityIndicator color={colors.ink} />
      ) : null}
      {university && campuses && campuses.length > 0 ? (
        <SelectField
          label={t('onboarding.campus')}
          placeholder={t('onboarding.pickCampus')}
          value={campus}
          options={campuses.map((c) => ({ value: c.id, label: c.name, subtitle: c.note ?? undefined }))}
          onChange={setCampus}
        />
      ) : null}
      {error ? <Muted style={{ color: colors.garnet }}>{error}</Muted> : null}
    </Screen>
  );
}
