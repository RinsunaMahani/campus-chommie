import { Redirect, router } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { SLOGAN } from '@/constants/config';
import { useSession } from '@/features/auth/session/SessionProvider';
import { BrandMark, Wordmark } from '@/shared/components/Brand';
import { Wallpaper } from '@/shared/components/Wallpaper';
import { Button } from '@/shared/components/Button';
import { t } from '@/shared/i18n';
import { colors, fonts } from '@/shared/theme/tokens';

/** Landing: the logo, the slogan, two ways in, the course finder (no account needed), and the legal links. */
export default function WelcomeScreen() {
  const { status } = useSession();
  // Closed the app before typing the email code: carry on from there.
  if (status === 'unverified') return <Redirect href="/verify-email" />;

  return (
    <View style={styles.fill}>
      <Wallpaper />
      <StatusBar style="light" />
      <SafeAreaView style={styles.safe}>
        <View style={styles.center}>
          <BrandMark size={112} />
          {/* 32 px: "Campus Chommie" stays on one line on a 360 px phone. */}
          <Wordmark size={32} />
          <Text style={styles.slogan}>{SLOGAN}</Text>
        </View>

        <View style={styles.actions}>
          <Button title="Get started" variant="accent" onPress={() => router.push('/create-account')} />
          <Pressable accessibilityRole="button" onPress={() => router.push('/sign-in')} style={styles.link}>
            <Text style={styles.linkText}>I already have an account</Text>
          </Pressable>
          <Button title={t('courseFinder.title')} variant="secondary" icon="compass" onPress={() => router.push('/course-finder')} />
          <Text style={styles.finderNote}>{t('courseFinder.noAccount')}</Text>
        </View>

        <View style={styles.legal}>
          <Pressable accessibilityRole="link" onPress={() => router.push('/privacy-policy')} hitSlop={8}>
            <Text style={styles.legalText}>Privacy Policy</Text>
          </Pressable>
          <Text style={styles.legalDot}>·</Text>
          <Pressable accessibilityRole="link" onPress={() => router.push('/terms-of-use')} hitSlop={8}>
            <Text style={styles.legalText}>Terms of Use</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  fill: { flex: 1 },
  safe: { flex: 1, paddingHorizontal: 22 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 14 },
  slogan: { fontFamily: fonts.medium, fontSize: 16, color: colors.textMuted, textAlign: 'center' },
  actions: { gap: 4 },
  link: { alignItems: 'center', paddingVertical: 16 },
  linkText: { fontFamily: fonts.bold, fontSize: 14.5, color: colors.ink },
  finderNote: { fontFamily: fonts.medium, fontSize: 12.5, color: colors.textMuted, textAlign: 'center', paddingTop: 6, paddingBottom: 10 },
  legal: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 10, paddingBottom: 14 },
  legalText: { fontFamily: fonts.medium, fontSize: 12.5, color: colors.textMuted, textDecorationLine: 'underline' },
  legalDot: { color: colors.textFaint },
});
