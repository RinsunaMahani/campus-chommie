/**
 * Where the user is in the journey.
 *
 *   signedOut  -> landing, create account, sign in, reset
 *   unverified -> account created, waiting for the email code
 *   active     -> signed in
 *
 * The root layout guards each route group on `status`, so moving between
 * stages is just a state change; the router redirects on its own.
 *
 * Saved in SecureStore so a reload keeps you where you were.
 */
import * as SecureStore from 'expo-secure-store';
import { createContext, ReactNode, useContext, useEffect, useMemo, useState } from 'react';

import { setSessionEndedHandler } from '@/shared/api/client';

import { authApi } from '../api/authApi';
import { consentNow, emptyProfile } from '../profile';
import { Profile } from '../types';

export type Status = 'signedOut' | 'unverified' | 'active';

export type SessionState = { status: Status; profile: Profile };

// Bump when Profile's shape changes, so an old saved session is dropped
// instead of crashing a screen that expects the new fields.
const STORAGE_KEY = 'campus-chommie.session.v1';

const initialState: SessionState = { status: 'signedOut', profile: emptyProfile };

type SessionContextValue = SessionState & {
  loaded: boolean;
  startEmailSignUp: (email: string) => void;
  emailVerified: () => void;
  startGoogleSignUp: (email: string, consented: boolean) => void;
  signedIn: (profile: Profile) => void;
  signOut: () => void;
};

const SessionContext = createContext<SessionContextValue | null>(null);

async function load(): Promise<SessionState | null> {
  try {
    const raw = await SecureStore.getItemAsync(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as SessionState) : null;
  } catch {
    return null;
  }
}

async function save(state: SessionState) {
  try {
    if (state.status === 'signedOut') await SecureStore.deleteItemAsync(STORAGE_KEY);
    else await SecureStore.setItemAsync(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Not fatal: the session just won't survive a reload.
  }
}

export function SessionProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<SessionState>(initialState);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    load().then((saved) => {
      if (saved) setState(saved);
      setLoaded(true);
    });
  }, []);

  useEffect(() => {
    if (loaded) save(state);
  }, [state, loaded]);

  // The server ended this session (signed out elsewhere, password changed,
  // new phone): go back to the landing screen.
  useEffect(() => {
    setSessionEndedHandler(() => setState(initialState));
    return () => setSessionEndedHandler(null);
  }, []);

  const value = useMemo<SessionContextValue>(
    () => ({
      ...state,
      loaded,
      // Consent was ticked on the create-account screen, so stamp it here.
      startEmailSignUp: (email) => setState({ status: 'unverified', profile: { ...emptyProfile, email, consent: consentNow() } }),
      emailVerified: () => setState((s) => ({ ...s, status: 'active' })),
      startGoogleSignUp: (email, consented) =>
        setState({
          status: 'active',
          profile: { ...emptyProfile, email, signedUpWith: 'google', consent: consented ? consentNow() : null },
        }),
      signedIn: (profile) => setState({ status: 'active', profile }),
      signOut: () => {
        authApi.logout(); // ends the session on the server; local sign-out never waits for it
        setState(initialState);
      },
    }),
    [state, loaded],
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession() {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error('useSession must be used inside <SessionProvider>');
  return ctx;
}
