/**
 * A Google ID token waiting for the next step (the password that links it, or the sign-up boxes). In memory only,
 * never stored or logged; forgotten once the step succeeds. Google's tokens last about an hour, so a stale one
 * fails on the server and the student starts again.
 */
let pending: string | null = null;

export function keepGoogleToken(token: string): void {
  pending = token;
}

export function pendingGoogleToken(): string | null {
  return pending;
}

export function forgetGoogleToken(): void {
  pending = null;
}
