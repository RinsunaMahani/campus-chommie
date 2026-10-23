/**
 * App-wide settings read from EXPO_PUBLIC_* environment variables
 * (frontend/mobile/.env, git-ignored). Only PUBLIC values belong here: anything in
 * the app bundle can be read by anyone who installs it.
 */

import Constants, { ExecutionEnvironment } from 'expo-constants';
import { Platform } from 'react-native';

/** Slogan under the logo on the landing screen. */
export const SLOGAN = 'From choosing a course to graduating.';

/** Where the backend lives (on a phone: your PC's IP, not localhost). */
export const API_BASE_URL: string = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:5000/api/v1';

/** The real backend (false) or the built-in mock (true, the default), for sign-in. */
export const USE_MOCK_AUTH: boolean = process.env.EXPO_PUBLIC_USE_MOCK_API !== 'false';


/**
 * Continue with Google: the Google Cloud project's WEB client ID (public). The web app signs in with it, and the
 * APK asks Google for an ID token issued to it too, so the backend's GOOGLE_CLIENT_IDS needs only this one. The
 * APK also needs an Android client in the same project (package name and the signing key's SHA-1); its ID isn't
 * used in code.
 */
export const GOOGLE_WEB_CLIENT_ID: string = process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID ?? '';

/** The button shows only where Google sign-in can work: a client ID, on the web or an installed build (not Expo Go,
 * which hasn't the native module). Never a "coming soon" button. */
export const GOOGLE_READY: boolean =
  GOOGLE_WEB_CLIENT_ID.length > 0 && (Platform.OS === 'web' || Constants.executionEnvironment !== ExecutionEnvironment.StoreClient);
