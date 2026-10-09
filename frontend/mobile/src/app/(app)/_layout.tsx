import { Stack } from 'expo-router';

import { colors } from '@/shared/theme/tokens';

export const unstable_settings = {
  // Deep links into a screen still get the tabs underneath for Back.
  initialRouteName: '(tabs)',
};

/** Signed in: the tabs, plus the screens opened from them (account security, ...). */
export default function AppLayout() {
  return <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.porcelain } }} />;
}
