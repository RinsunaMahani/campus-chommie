import { useCallback } from 'react';

import { GOOGLE_WEB_CLIENT_ID } from '@/constants/config';

/**
 * The installed app (APK): Google's own account picker, through the native Google Sign-In library. It returns an
 * ID token issued to our web client, which the backend verifies; Google never gives us the password. Loaded only
 * when used, so Expo Go (which hasn't the native module) never loads it. Null when the student backs out.
 */
export function useGoogleIdToken() {
  const getIdToken = useCallback(async (): Promise<string | null> => {
    const { GoogleSignin, isSuccessResponse } = await import('@react-native-google-signin/google-signin');
    GoogleSignin.configure({ webClientId: GOOGLE_WEB_CLIENT_ID });
    await GoogleSignin.hasPlayServices({ showPlayServicesUpdateDialog: true });
    await GoogleSignin.signOut().catch(() => undefined); // always let them choose the account
    const result = await GoogleSignin.signIn();
    return isSuccessResponse(result) ? result.data.idToken : null;
  }, []);
  return { getIdToken };
}
