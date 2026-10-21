import { Stack } from 'expo-router';
import { ActivityIndicator, View } from 'react-native';

import { ProfileProvider, useProfile } from '@/features/profile/state';
import { night, PaletteProvider, usePalette } from '@/shared/theme/palette';

export const unstable_settings = {
  // Deep links into a screen still get the tabs underneath for Back.
  initialRouteName: '(tabs)',
};

/**
 * Signed in: the tabs, plus the screens opened from them (account security,
 * My money's settings, ...). Until the student has chosen a university, only
 * onboarding is reachable; choosing one opens the tabs by itself. The student's side is black (the night
 * palette): one colour per job, so the content stands out.
 */
export default function AppLayout() {
  return (
    <PaletteProvider palette={night}>
      <ProfileProvider>
        <AppStack />
      </ProfileProvider>
    </PaletteProvider>
  );
}

function AppStack() {
  const colors = usePalette();
  const { loading, needsOnboarding } = useProfile();
  if (loading) {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.porcelain }}>
        <ActivityIndicator color={colors.ink} />
      </View>
    );
  }
  return (
    <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.porcelain } }}>
      <Stack.Protected guard={needsOnboarding}>
        <Stack.Screen name="onboarding" />
      </Stack.Protected>
      <Stack.Protected guard={!needsOnboarding}>
        <Stack.Screen name="(tabs)" />
      </Stack.Protected>
    </Stack>
  );
}
