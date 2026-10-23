export type Consent = { privacyVersion: string; termsVersion: string; acceptedAt: string };

/**
 * What the app knows about the signed-in student: the account, and the
 * documents they agreed to. Nothing else is collected at sign-up.
 */
export type Profile = {
  email: string;
  signedUpWith: 'email' | 'google';
  consent: Consent | null;
};

export class AuthError extends Error {
  constructor(
    /** The server's stable code, e.g. INVALID_CODE, WEAK_PASSWORD, RATE_LIMITED, NETWORK. */
    public code: string,
    message: string,
  ) {
    super(message);
  }
}

/**
 * Sign-in is two-factor: the password, plus either a trusted phone or a
 * code sent to the email. On a new phone the first step returns a
 * challenge; the code screen finishes with verifySignIn.
 */
export type SignInResult = { kind: 'signed_in'; profile: Profile } | { kind: 'code_required'; challenge: string };

/**
 * Continue with Google: signed in; or a password account already uses the email (link it with the password once);
 * or a new account that still needs the 18-or-older and Privacy and Terms boxes.
 */
export type GoogleResult =
  | { kind: 'signed_in'; profile: Profile }
  | { kind: 'link'; email: string }
  | { kind: 'needs_consent'; email: string };

/** Everything the auth screens ask of the server: the mock or the real backend. */
export interface AuthApi {
  /** confirmed18OrOlder: accounts are for adults only; the server refuses anything but true. */
  createAccount(input: { email: string; password: string; consent: Consent; confirmed18OrOlder: boolean }): Promise<void>;
  verifyEmail(email: string, code: string): Promise<void>;
  resendCode(email: string): Promise<void>;
  /** idToken: Google's ID token. consented: the 18-or-older and Privacy and Terms boxes were ticked (sent with it). */
  continueWithGoogle(idToken: string, consented: boolean): Promise<GoogleResult>;
  linkGoogle(idToken: string, password: string): Promise<Profile>;
  signIn(email: string, password: string): Promise<SignInResult>;
  /** Second step on a new phone: the code from the email. This phone is trusted afterwards. */
  verifySignIn(email: string, challenge: string, code: string): Promise<Profile>;
  resendSignInCode(challenge: string): Promise<void>;
  /** Same answer whether or not the account exists, so nobody can fish for emails. */
  requestPasswordReset(email: string): Promise<void>;
  /** From the reset link: set a new password. */
  resetPassword(token: string, password: string): Promise<void>;
  /** End this phone's session on the server. */
  logout(): Promise<void>;
}
