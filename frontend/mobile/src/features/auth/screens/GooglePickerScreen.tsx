import { FontAwesome, Feather } from '@expo/vector-icons';
import { router, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { GOOGLE_READY, USE_MOCK_AUTH } from '@/constants/config';
import { authApi } from '@/features/auth/api/authApi';
import { keepGoogleToken } from '@/features/auth/google/pendingGoogle';
import { useSession } from '@/features/auth/session/SessionProvider';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

/**
 * MOCK of Android's own Google account picker, for the mock backend only. The real flow is
 * features/auth/google/GoogleSignIn (Google's own picker); Campus Chommie gets name, email and photo, never the
 * password.
 */
const accounts = [
  { name: 'Lindiwe Mokoena', email: 'lindiwe.student@gmail.com', tint: '#1C2B1E' },
  { name: 'Lindiwe M', email: 'lmokoena.study@gmail.com', tint: '#6B6456' },
];

export default function GooglePicker() {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const { startGoogleSignUp } = useSession();
  // Set when coming from Create account, where the box was ticked.
  const { consent } = useLocalSearchParams<{ consent?: string }>();
  const [picked, setPicked] = useState<string | null>(null);

  // Real backend, but Google isn't set up in the app yet (next build):
  // say so plainly instead of showing a fake account picker.
  if (!USE_MOCK_AUTH && !GOOGLE_READY) {
    return (
      <View style={styles.backdrop}>
        <Pressable style={{ flex: 1 }} onPress={() => router.back()} accessibilityLabel="Close" />
        <SafeAreaView edges={['bottom']} style={styles.sheet}>
          <View style={styles.handle} />
          <View style={styles.header}>
            <FontAwesome name="google" size={18} color="#4285F4" />
            <Text style={styles.title}>Google sign-in is coming soon</Text>
          </View>
          <Text style={styles.foot}>For now, create your account with your email and a password.</Text>
          <Pressable onPress={() => router.back()} style={styles.account}>
            <Text style={styles.name}>Use my email instead</Text>
          </Pressable>
        </SafeAreaView>
      </View>
    );
  }

  async function pick(email: string) {
    setPicked(email);
    // Mock only: the picked email stands in for Google's token.
    const result = await authApi.continueWithGoogle(email, true);
    if (result.kind === 'link') {
      keepGoogleToken(email);
      router.replace({ pathname: '/link-google', params: { email } });
    } else {
      startGoogleSignUp(email, consent === '1'); // the signed-in screens open on their own
    }
  }

  return (
    <View style={styles.backdrop}>
      <Pressable style={{ flex: 1 }} onPress={() => router.back()} accessibilityLabel="Close" />
      <SafeAreaView edges={['bottom']} style={styles.sheet}>
        <View style={styles.handle} />
        <View style={styles.header}>
          <FontAwesome name="google" size={18} color="#4285F4" />
          <View>
            <Text style={styles.title}>Choose an account</Text>
            <Text style={styles.sub}>to continue to Campus Chommie</Text>
          </View>
        </View>
        {accounts.map((a) => (
          <Pressable
            key={a.email}
            onPress={() => pick(a.email)}
            disabled={!!picked}
            style={[styles.account, picked === a.email && styles.accountPicked]}>
            <View style={[styles.avatar, { backgroundColor: a.tint }]}>
              <Text style={styles.avatarText}>{a.name[0]}</Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.name}>{a.name}</Text>
              <Text style={styles.sub}>{a.email}</Text>
            </View>
            {picked === a.email ? <ActivityIndicator color={colors.ink} /> : null}
          </Pressable>
        ))}
        <Pressable style={styles.account} disabled>
          <View style={[styles.avatar, { backgroundColor: colors.iconTile }]}>
            <Feather name="plus" size={16} color={colors.textMuted} />
          </View>
          <Text style={styles.name}>Use another account</Text>
        </Pressable>
        <Text style={styles.foot}>
          Google shares your name, email and profile photo with Campus Chommie. Never your password.
        </Text>
      </SafeAreaView>
    </View>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
  backdrop: { flex: 1, backgroundColor: colors.overlay },
  sheet: {
    backgroundColor: colors.porcelain,
    borderTopLeftRadius: 22,
    borderTopRightRadius: 22,
    paddingHorizontal: 18,
    paddingBottom: 12,
    gap: 10,
  },
  handle: { alignSelf: 'center', width: 40, height: 4, borderRadius: 2, backgroundColor: colors.line, marginTop: 10 },
  header: { flexDirection: 'row', alignItems: 'center', gap: 10, marginVertical: 6 },
  title: { fontFamily: fonts.bold, fontSize: 16, color: colors.text },
  sub: { fontFamily: fonts.body, fontSize: 13.5, color: colors.textMuted },
  account: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    padding: 12,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.white,
  },
  accountPicked: { borderColor: colors.ink, borderWidth: 1.5 },
  avatar: { width: 38, height: 38, borderRadius: radius.sm, alignItems: 'center', justifyContent: 'center' },
  avatarText: { fontFamily: fonts.display, fontSize: 16, color: colors.pillText },
  name: { fontFamily: fonts.bold, fontSize: 15.5, color: colors.text },
  foot: { fontFamily: fonts.body, fontSize: 13, lineHeight: 17, color: colors.textMuted, marginTop: 4 },
});
