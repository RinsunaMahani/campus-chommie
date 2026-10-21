import { Stack } from 'expo-router';
import { usePalette } from '@/shared/theme/palette';



/** Onboarding: the privacy notice, then university and campus. */
export default function OnboardingLayout() {
  const colors = usePalette();
  return <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.porcelain } }} />;
}
