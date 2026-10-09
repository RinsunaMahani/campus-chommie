/**
 * App-wide settings read from EXPO_PUBLIC_* environment variables
 * (frontend/mobile/.env, git-ignored). Only PUBLIC values belong here: anything in
 * the app bundle can be read by anyone who installs it.
 */

/** Slogan under the logo on the landing screen. */
export const SLOGAN = 'From choosing a course to graduating.';

/** Where the backend lives (on a phone: your PC's IP, not localhost). */
export const API_BASE_URL: string = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:5000/api/v1';

/** The real backend (false) or the built-in mock (true, the default), for sign-in. */
export const USE_MOCK_AUTH: boolean = process.env.EXPO_PUBLIC_USE_MOCK_API !== 'false';

/** Google sign-in in the app needs a native module + client IDs (next build). */
export const GOOGLE_READY = false;
