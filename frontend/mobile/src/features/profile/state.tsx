/**
 * The signed-in student's profile and demo flag, loaded once when the signed-in
 * part of the app opens. Onboarding shows until a university is chosen.
 *
 * With the built-in test sign-in (EXPO_PUBLIC_USE_MOCK_API) there is no real
 * account to ask about, so nothing is loaded and onboarding is skipped.
 */
import { createContext, ReactNode, useContext, useEffect, useMemo, useState } from 'react';

import { USE_MOCK_AUTH } from '@/constants/config';

import { profileApi } from './api/profileApi';
import { StudentProfile } from './types';

type ProfileContextValue = {
  loading: boolean;
  profile: StudentProfile | null;
  demo: boolean;
  /** True with the built-in test sign-in: no real account behind it. */
  mock: boolean;
  needsOnboarding: boolean;
  setProfile: (profile: StudentProfile) => void;
};

const ProfileContext = createContext<ProfileContextValue | null>(null);

export function ProfileProvider({ children }: { children: ReactNode }) {
  const [loading, setLoading] = useState(!USE_MOCK_AUTH);
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [demo, setDemo] = useState(false);

  useEffect(() => {
    if (USE_MOCK_AUTH) return;
    Promise.all([profileApi.get(), profileApi.me()])
      .then(([p, me]) => {
        setProfile(p);
        setDemo(me.demo);
      })
      // Can't load it (offline): carry on into the app, whose screens say what's wrong.
      .catch(() => undefined)
      .finally(() => setLoading(false));
  }, []);

  const value = useMemo<ProfileContextValue>(
    () => ({
      loading,
      profile,
      demo,
      mock: USE_MOCK_AUTH,
      needsOnboarding: !USE_MOCK_AUTH && !loading && !!profile && !profile.university,
      setProfile,
    }),
    [loading, profile, demo],
  );

  return <ProfileContext.Provider value={value}>{children}</ProfileContext.Provider>;
}

export function useProfile(): ProfileContextValue {
  const value = useContext(ProfileContext);
  if (!value) throw new Error('useProfile must be used inside ProfileProvider');
  return value;
}
