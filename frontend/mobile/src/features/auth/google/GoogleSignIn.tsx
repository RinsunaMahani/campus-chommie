import { router } from 'expo-router';
import { useState } from 'react';
import { StyleSheet, Text } from 'react-native';

import { AuthError, authApi } from '@/features/auth/api/authApi';
import { useSession } from '@/features/auth/session/SessionProvider';
import { GoogleButton } from '@/shared/components/Parts';
import { Palette, useStyles } from '@/shared/theme/palette';
import { fonts } from '@/shared/theme/tokens';

import { keepGoogleToken } from './pendingGoogle';
import { useGoogleIdToken } from './useGoogleIdToken';

/**
 * "Continue with Google": Google's own sign-in gives an ID token, the backend checks it, and then either the
 * student is in; or the email already has a password account (they link it once with the password); or it's a new
 * account that still needs the 18-or-older and Privacy and Terms boxes. Render only when GOOGLE_READY.
 *
 * consented: the boxes on Create account are ticked. ready(): checked before Google opens (Create account shows
 * the boxes' errors and stops when they aren't ticked).
 */
export function GoogleSignIn({ consented, ready }: { consented: boolean; ready?: () => boolean }) {
  const styles = useStyles(makeStyles);
  const { signedIn } = useSession();
  const { getIdToken } = useGoogleIdToken();
  const [error, setError] = useState('');

  async function go() {
    if (ready && !ready()) return;
    setError('');
    try {
      const token = await getIdToken();
      if (!token) return; // they closed Google's window
      const result = await authApi.continueWithGoogle(token, consented);
      if (result.kind === 'signed_in') {
        signedIn(result.profile);
        return;
      }
      keepGoogleToken(token);
      const pathname = result.kind === 'link' ? '/link-google' : '/google-sign-up';
      router.push({ pathname, params: { email: result.email } });
    } catch (e) {
      setError(e instanceof AuthError ? e.message : 'Google sign-in didn’t work. Try again, or use your email.');
    }
  }

  return (
    <>
      <GoogleButton onPress={go} />
      {error ? <Text style={styles.error}>{error}</Text> : null}
    </>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    error: { fontFamily: fonts.medium, fontSize: 14, color: colors.garnet },
  });
