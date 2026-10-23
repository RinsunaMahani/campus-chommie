import { router, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { AuthError, authApi } from '@/features/auth/api/authApi';
import { forgetGoogleToken, pendingGoogleToken } from '@/features/auth/google/pendingGoogle';
import { useSession } from '@/features/auth/session/SessionProvider';
import { AgeCheckbox } from '@/shared/components/AgeCheckbox';
import { Button } from '@/shared/components/Button';
import { ConsentCheckbox } from '@/shared/components/ConsentCheckbox';
import { IconTile } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { Body, Title } from '@/shared/components/Text';
import { Palette, useStyles } from '@/shared/theme/palette';
import { fonts } from '@/shared/theme/tokens';

/**
 * A new account through Google, from Sign in: the same two boxes as email sign-up (18 or older, and the Privacy
 * Policy and Terms) before the account is made. Nothing else is asked.
 */
export default function GoogleSignUpScreen() {
  const styles = useStyles(makeStyles);
  const { email = '' } = useLocalSearchParams<{ email: string }>();
  const { signedIn } = useSession();
  const [adult, setAdult] = useState(false);
  const [agreed, setAgreed] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function create() {
    const token = pendingGoogleToken();
    if (!token) {
      setError('Google sign-in timed out. Go back and continue with Google again.');
      return;
    }
    setBusy(true);
    setError('');
    try {
      const result = await authApi.continueWithGoogle(token, true);
      if (result.kind === 'signed_in') {
        forgetGoogleToken();
        signedIn(result.profile);
      } else router.replace({ pathname: '/link-google', params: { email: result.email } });
    } catch (e) {
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
          {error ? <Text style={styles.error}>{error}</Text> : null}
          <AgeCheckbox checked={adult} onChange={setAdult} error={false} />
          <ConsentCheckbox checked={agreed} onChange={setAgreed} error={false} />
          <Button title="Create account" onPress={create} loading={busy} disabled={!adult || !agreed} />
        </>
      }>
      <View style={{ gap: 14 }}>
        <IconTile name="user-plus" size={50} />
        <Title>New here?</Title>
        <Body>
          Create your Campus Chommie account with <Text style={styles.email}>{email}</Text>. Tick both boxes first.
        </Body>
      </View>
    </Screen>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    email: { fontFamily: fonts.bold, color: colors.ink },
    error: { fontFamily: fonts.medium, fontSize: 14, color: colors.garnet },
  });
