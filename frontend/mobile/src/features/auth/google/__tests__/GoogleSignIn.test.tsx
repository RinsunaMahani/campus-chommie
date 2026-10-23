/**
 * Continue with Google: Google's token goes to the backend, with the 18-or-older and Privacy and Terms boxes only
 * when they were ticked; the backend's three answers (signed in, link with your password, finish sign-up) each go
 * to the right place, and closing Google's window does nothing. The token waits in memory for the next step only.
 */
import { beforeEach, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { router } from 'expo-router';

import { PRIVACY_POLICY } from '@/content/legal/privacyPolicy';
import { TERMS_OF_USE } from '@/content/legal/termsOfUse';
import { authApi } from '@/features/auth/api/authApi';
import { httpAuthApi } from '@/features/auth/api/httpAuthApi';

import { GoogleSignIn } from '../GoogleSignIn';
import { forgetGoogleToken, pendingGoogleToken } from '../pendingGoogle';

const signedIn = jest.fn();
const getIdToken = jest.fn<() => Promise<string | null>>();

jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));
jest.mock('expo-router', () => ({ router: { push: jest.fn(), replace: jest.fn(), back: jest.fn() } }));
jest.mock('@/features/auth/session/SessionProvider', () => ({ useSession: () => ({ signedIn }) }));
jest.mock('../useGoogleIdToken', () => ({ useGoogleIdToken: () => ({ getIdToken }) }));
jest.mock('@/shared/api/tokenStore', () => ({
  getTokens: async () => null,
  setTokens: async () => undefined,
  clearTokens: async () => undefined,
}));
jest.mock('@/shared/api/trustedPhone', () => ({
  getTrustedToken: async () => null,
  setTrustedToken: async () => undefined,
  phoneInfo: () => ({ platform: 'android', label: 'Test phone' }),
}));

const TOKEN = 'google-id-token-xxxxxxxxxxxxxxxx';
const profile = { email: 'nomsa@gmail.com', signedUpWith: 'google' as const, consent: null };

beforeEach(() => {
  jest.clearAllMocks();
  forgetGoogleToken();
  getIdToken.mockResolvedValue(TOKEN);
});

test('signed in straight away when Google says so', async () => {
  jest.spyOn(authApi, 'continueWithGoogle').mockResolvedValue({ kind: 'signed_in', profile });
  render(<GoogleSignIn consented={false} />);
  fireEvent.press(screen.getByText('Continue with Google'));
  await waitFor(() => expect(signedIn).toHaveBeenCalledWith(profile));
  expect(authApi.continueWithGoogle).toHaveBeenCalledWith(TOKEN, false);
  expect(pendingGoogleToken()).toBeNull();
});

test('a password account goes to linking, and a new one to the sign-up boxes, with the token kept', async () => {
  const cont = jest.spyOn(authApi, 'continueWithGoogle').mockResolvedValueOnce({ kind: 'link', email: 'thabo@gmail.com' });
  render(<GoogleSignIn consented={false} />);
  fireEvent.press(screen.getByText('Continue with Google'));
  await waitFor(() => expect(router.push).toHaveBeenCalledWith({ pathname: '/link-google', params: { email: 'thabo@gmail.com' } }));
  expect(pendingGoogleToken()).toBe(TOKEN);

  cont.mockResolvedValueOnce({ kind: 'needs_consent', email: 'nomsa@gmail.com' });
  fireEvent.press(screen.getByText('Continue with Google'));
  await waitFor(() => expect(router.push).toHaveBeenCalledWith({ pathname: '/google-sign-up', params: { email: 'nomsa@gmail.com' } }));
  expect(signedIn).not.toHaveBeenCalled();
});

test('closing Google’s window does nothing, and unticked boxes stop it before Google opens', async () => {
  const cont = jest.spyOn(authApi, 'continueWithGoogle');
  getIdToken.mockResolvedValueOnce(null);
  const { rerender } = render(<GoogleSignIn consented={false} />);
  fireEvent.press(screen.getByText('Continue with Google'));
  await waitFor(() => expect(getIdToken).toHaveBeenCalled());
  expect(cont).not.toHaveBeenCalled();

  getIdToken.mockClear();
  rerender(<GoogleSignIn consented ready={() => false} />);
  fireEvent.press(screen.getByText('Continue with Google'));
  expect(getIdToken).not.toHaveBeenCalled();
});

test('the backend’s answers map to the three outcomes, and the boxes are sent only when ticked', async () => {
  const bodies: unknown[] = [];
  const answers = [
    { status: 409, json: { success: false, code: 'GOOGLE_LINK_REQUIRED', message: 'x', data: { email: 'thabo@gmail.com' } } },
    { status: 422, json: { success: false, code: 'GOOGLE_SIGNUP_DETAILS_REQUIRED', message: 'x', data: { email: 'nomsa@gmail.com' } } },
    {
      status: 200,
      json: { success: true, data: { access_token: 'a', refresh_token: 'r', user: { id: '1', email: 'nomsa@gmail.com', status: 'active', signed_up_with: 'google' } } },
    },
    { status: 401, json: { success: false, code: 'INVALID_GOOGLE_TOKEN', message: 'Google sign-in failed. Please try again.' } },
  ];
  global.fetch = jest.fn((_url: string, init: { body?: string }) => {
    bodies.push(init.body ? JSON.parse(init.body) : undefined);
    const a = answers.shift()!;
    return Promise.resolve({ status: a.status, json: () => Promise.resolve(a.json) });
  }) as unknown as typeof fetch;

  expect(await httpAuthApi.continueWithGoogle(TOKEN, false)).toEqual({ kind: 'link', email: 'thabo@gmail.com' });
  expect(await httpAuthApi.continueWithGoogle(TOKEN, false)).toEqual({ kind: 'needs_consent', email: 'nomsa@gmail.com' });
  const done = await httpAuthApi.continueWithGoogle(TOKEN, true);
  expect(done.kind).toBe('signed_in');
  await expect(httpAuthApi.continueWithGoogle(TOKEN, false)).rejects.toMatchObject({ code: 'INVALID_GOOGLE_TOKEN' });

  expect(bodies[0]).toEqual({ id_token: TOKEN });
  expect(bodies[2]).toEqual({
    id_token: TOKEN,
    consent: { privacy_version: PRIVACY_POLICY.version, terms_version: TERMS_OF_USE.version, confirmed_18_or_older: true },
  });
});
