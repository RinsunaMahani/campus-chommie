import { makeRedirectUri } from 'expo-auth-session';
import * as Google from 'expo-auth-session/providers/google';
import { useCallback } from 'react';

import { GOOGLE_WEB_CLIENT_ID } from '@/constants/config';

/**
 * The web app: Google's sign-in window, asking for an ID token for our web client. It comes back to /oauthredirect
 * (registered in the Google Cloud client), where the root layout finishes the sign-in and closes the window. Null
 * when the student closes it.
 */
export function useGoogleIdToken() {
  const [request, , promptAsync] = Google.useIdTokenAuthRequest({
    webClientId: GOOGLE_WEB_CLIENT_ID,
    redirectUri: makeRedirectUri({ path: 'oauthredirect' }),
    selectAccount: true,
  });
  const getIdToken = useCallback(async (): Promise<string | null> => {
    if (!request) return null;
    const result = await promptAsync();
    return result.type === 'success' ? (result.params.id_token ?? null) : null;
  }, [request, promptAsync]);
  return { getIdToken };
}
