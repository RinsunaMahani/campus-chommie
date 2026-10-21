import { router } from 'expo-router';
import { useRef, useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { GOOGLE_READY } from '@/constants/config';
import { Button } from '@/shared/components/Button';
import { GoogleButton, OrDivider } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { Body, Title } from '@/shared/components/Text';
import { TextField } from '@/shared/components/TextField';
import { isEmail } from '@/shared/lib/validation';
import { AuthError, authApi } from '@/features/auth/api/authApi';
import { setPendingSignIn } from '@/features/auth/session/pendingSignIn';
import { useSession } from '@/features/auth/session/SessionProvider';
import { colors, fonts, radius } from '@/shared/theme/tokens';

// The fictional demo students (backend/data/demo/personas.yaml). Tapping one fills in the email only: the shared
// password is in the judges' notes, never in the app, because anything in the app ships inside the APK.
const DEMO_STUDENTS = [
  { email: 'naledi.demo@example.com', label: 'Naledi', note: 'short money, heavy week' },
  { email: 'sipho.demo@example.com', label: 'Sipho', note: 'heavy week now' },
  { email: 'thabo.demo@example.com', label: 'Thabo', note: 'class rep' },
];

export default function SignIn() {
  const { signedIn, startEmailSignUp } = useSession();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const passwordRef = useRef<TextInput>(null);

  async function submit() {
    if (!isEmail(email)) {
      setError('Enter a valid email address');
      return;
    }
    setBusy(true);
    setError('');
    try {
      const normalized = email.trim().toLowerCase();
      const result = await authApi.signIn(normalized, password);
      if (result.kind === 'code_required') {
        // New phone: the password was right, now the code from the email.
        setPendingSignIn({ email: normalized, challenge: result.challenge });
        setPassword('');
        router.push('/sign-in-code');
        return;
      }
      signedIn(result.profile);
    } catch (e) {
      if (e instanceof AuthError && e.code === 'EMAIL_NOT_VERIFIED') {
        // Right password, email never confirmed: the server just sent a new code.
        startEmailSignUp(email.trim().toLowerCase());
        router.push('/verify-email');
        return;
      }
      setError(e instanceof AuthError ? e.message : 'Something went wrong. Try again.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <Screen
      back
      footer={
        <>
          <Button title="Sign in" onPress={submit} loading={busy} />
          <Pressable onPress={() => router.replace('/create-account')} style={styles.alt}>
            <Text style={styles.altText}>
              New here? <Text style={styles.altLink}>Create an account</Text>
            </Text>
          </Pressable>
        </>
      }>
      <View style={{ gap: 8 }}>
        <Title>Welcome back</Title>
        <Body>Sign in to your account.</Body>
      </View>
      {GOOGLE_READY ? (
        <>
          <GoogleButton onPress={() => router.push('/google')} />
          <OrDivider />
        </>
      ) : null}
      <TextField
        label="Email address"
        icon="mail"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        autoComplete="email"
        keyboardType="email-address"
        returnKeyType="next"
        onSubmitEditing={() => passwordRef.current?.focus()}
      />
      <TextField
        ref={passwordRef}
        label="Password"
        password
        value={password}
        onChangeText={setPassword}
        autoComplete="current-password"
        returnKeyType="done"
        onSubmitEditing={submit}
        error={error}
      />
      <Pressable onPress={() => router.push({ pathname: '/forgot-password', params: { email } })}>
        <Text style={styles.link}>Forgot password?</Text>
      </Pressable>
      <View style={styles.demo}>
        <Text style={styles.demoTitle}>Try a demo student (fictional data)</Text>
        <View style={styles.demoRow}>
          {DEMO_STUDENTS.map((d) => (
            <Pressable
              key={d.email}
              accessibilityRole="button"
              accessibilityLabel={`Fill in ${d.label}'s demo email: ${d.note}`}
              onPress={() => {
                setEmail(d.email);
                setError('');
                passwordRef.current?.focus();
              }}
              style={({ pressed }) => [styles.demoChip, pressed && { opacity: 0.8 }]}>
              <Text style={styles.demoName}>{d.label}</Text>
              <Text style={styles.demoNote}>{d.note}</Text>
            </Pressable>
          ))}
        </View>
        <Text style={styles.demoHint}>{"Then type the demo password from the judges' notes."}</Text>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  link: { fontFamily: fonts.bold, fontSize: 13, color: colors.ink },
  alt: { alignItems: 'center', paddingVertical: 4 },
  altText: { fontFamily: fonts.body, fontSize: 13, color: colors.textMuted },
  altLink: { fontFamily: fonts.bold, color: colors.ink },
  demo: { gap: 8, paddingTop: 8 },
  demoTitle: { fontFamily: fonts.semibold, fontSize: 13, color: colors.textMuted },
  demoRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  demoChip: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.white,
  },
  demoName: { fontFamily: fonts.bold, fontSize: 13.5, color: colors.ink },
  demoNote: { fontFamily: fonts.body, fontSize: 11.5, color: colors.textMuted },
  demoHint: { fontFamily: fonts.body, fontSize: 12, color: colors.textMuted },
});
