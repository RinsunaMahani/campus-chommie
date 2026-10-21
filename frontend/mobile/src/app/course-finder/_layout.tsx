import { Stack } from 'expo-router';

import { CourseFinderProvider } from '@/features/courseFinder/state';
import { usePalette } from '@/shared/theme/palette';

/** Find my course: open to everyone, signed in or not. Its answers live here, in memory, for one visit. */
export default function CourseFinderLayout() {
  const colors = usePalette();
  return (
    <CourseFinderProvider>
      <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.porcelain } }} />
    </CourseFinderProvider>
  );
}
