import { Stack } from 'expo-router';

import { usePalette } from '@/shared/theme/palette';

export default function AuthLayout() {
  const colors = usePalette();
  return (
    <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.porcelain } }}>
      <Stack.Screen name="index" />
      <Stack.Screen
        name="google"
        options={{ presentation: 'transparentModal', animation: 'fade', contentStyle: { backgroundColor: 'transparent' } }}
      />
    </Stack>
  );
}
