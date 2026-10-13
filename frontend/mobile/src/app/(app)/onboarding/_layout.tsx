import { Stack } from 'expo-router';

import { colors } from '@/shared/theme/tokens';

/** Onboarding: the privacy notice, then university and campus. */
export default function OnboardingLayout() {
  return <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.porcelain } }} />;
}
