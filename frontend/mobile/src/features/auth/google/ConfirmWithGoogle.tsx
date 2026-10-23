import { useState } from 'react';

import { Button } from '@/shared/components/Button';

import { useGoogleIdToken } from './useGoogleIdToken';

/**
 * For an account that signs in with Google only (no password): closing or deleting it is confirmed by signing in
 * with the same Google account again. The server checks it's the linked one. Render only when GOOGLE_READY.
 */
export function ConfirmWithGoogle({ title, onToken }: { title: string; onToken: (idToken: string) => Promise<void> }) {
  const { getIdToken } = useGoogleIdToken();
  const [busy, setBusy] = useState(false);

  async function go() {
    setBusy(true);
    try {
      const token = await getIdToken();
      if (token) await onToken(token);
    } finally {
      setBusy(false);
    }
  }

  return <Button title={title} variant="secondary" icon="user-check" onPress={go} loading={busy} />;
}
