import { Stack } from 'expo-router';
import { ActivityIndicator, View } from 'react-native';

import { ProfileProvider, useProfile } from '@/features/profile/state';
import { colors } from '@/shared/theme/tokens';

export const unstable_settings = {
  // Deep links into a screen still get the tabs underneath for Back.
  initialRouteName: '(tabs)',
};

/**
 * Signed in: the tabs, plus the screens opened from them (account security,
 * My money's settings, ...). Until the student has chosen a university, only
 * onboarding is reachable; choosing one opens the tabs by itself.
 */
export default function AppLayout() {
  return (
    <ProfileProvider>
      <AppStack />
    </ProfileProvider>
  );
}

function AppStack() {
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
