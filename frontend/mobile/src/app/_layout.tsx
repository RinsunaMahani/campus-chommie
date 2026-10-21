import { Fraunces_600SemiBold, Fraunces_700Bold } from '@expo-google-fonts/fraunces';
import {
  PlusJakartaSans_400Regular,
  PlusJakartaSans_500Medium,
  PlusJakartaSans_600SemiBold,
  PlusJakartaSans_700Bold,
  PlusJakartaSans_800ExtraBold,
} from '@expo-google-fonts/plus-jakarta-sans';
import { useFonts } from 'expo-font';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { StatusBar } from 'expo-status-bar';
import { useEffect } from 'react';

import { SessionProvider, useSession } from '@/features/auth/session/SessionProvider';
import { usePalette } from '@/shared/theme/palette';

export { ErrorBoundary } from 'expo-router';

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  return (
    <SessionProvider>
      <RootNavigator />
    </SessionProvider>
  );
}

/**
 * One route group per stage of the journey. Only the group matching the
 * session status is reachable; when the status changes the router moves
 * the user on by itself (no manual redirects).
 */
function RootNavigator() {
  const colors = usePalette();
  const { status, loaded } = useSession();
  const [fontsLoaded, fontError] = useFonts({
    PlusJakartaSans_400Regular,
    PlusJakartaSans_500Medium,
    PlusJakartaSans_600SemiBold,
    PlusJakartaSans_700Bold,
    PlusJakartaSans_800ExtraBold,
    Fraunces_600SemiBold,
    Fraunces_700Bold,
  });

  const ready = loaded && (fontsLoaded || !!fontError);

  useEffect(() => {
    if (ready) SplashScreen.hideAsync();
  }, [ready]);

  if (!ready) return null;

  return (
    <>
      <StatusBar style="dark" />
      <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.porcelain } }}>
        <Stack.Protected guard={status === 'signedOut' || status === 'unverified'}>
          <Stack.Screen name="(auth)" />
        </Stack.Protected>
        <Stack.Protected guard={status === 'active'}>
          <Stack.Screen name="(app)" />
        </Stack.Protected>
        {/* Legal pages and the course finder are reachable from every stage. */}
        <Stack.Screen name="(legal)" />
        <Stack.Screen name="course-finder" />
      </Stack>
    </>
  );
}
