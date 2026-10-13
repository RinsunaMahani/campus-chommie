import { Stack } from 'expo-router';

import { CourseFinderProvider } from '@/features/courseFinder/state';
import { colors } from '@/shared/theme/tokens';

/** Find my course: open to everyone, signed in or not. Its answers live here, in memory, for one visit. */
export default function CourseFinderLayout() {
  return (
    <CourseFinderProvider>
      <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.porcelain } }} />
    </CourseFinderProvider>
  );
}
