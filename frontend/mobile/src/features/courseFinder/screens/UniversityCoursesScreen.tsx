/** One university's courses, by faculty, on their own screen (from the university's overview). */
import { useLocalSearchParams } from 'expo-router';

import { HeroScreen } from '@/shared/components/HeroScreen';
import { t } from '@/shared/i18n';

import { UniversityProgrammes } from '../components/UniversityProgrammes';
import { useCourseFinder } from '../state';

export default function UniversityCoursesScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const cf = useCourseFinder();
  const name = cf.points?.universities.find((u) => u.university === id)?.university_name ?? (id ?? '').toUpperCase();
  return (
    <HeroScreen back overline={name} title={t('university.courses')}>
      {id ? <UniversityProgrammes id={id} /> : null}
    </HeroScreen>
  );
}
