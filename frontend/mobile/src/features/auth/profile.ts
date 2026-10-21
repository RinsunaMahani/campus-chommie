import { PRIVACY_POLICY } from '@/content/legal/privacyPolicy';
import { TERMS_OF_USE } from '@/content/legal/termsOfUse';

import { Consent, Profile } from './types';

export const emptyProfile: Profile = {
  email: '',
  signedUpWith: 'email',
  consent: null,
};

/** Consent to the CURRENT versions, stamped now. */
export function consentNow(): Consent {
  return {
    privacyVersion: PRIVACY_POLICY.version,
    termsVersion: TERMS_OF_USE.version,
    acceptedAt: new Date().toISOString(),
  };
}

/** What a returning user looks like in the mock (sign in / link Google). */
export function demoProfile(email: string, signedUpWith: Profile['signedUpWith']): Profile {
  return { ...emptyProfile, email, signedUpWith, consent: consentNow() };
}
