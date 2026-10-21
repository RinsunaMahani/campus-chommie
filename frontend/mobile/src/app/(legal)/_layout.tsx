import { Stack } from 'expo-router';

import { usePalette } from '@/shared/theme/palette';

/** Legal pages: open to everyone, signed in or not. */
export default function LegalLayout() {
  const colors = usePalette();
  return <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.porcelain } }} />;
}
