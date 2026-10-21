import { router } from 'expo-router';
import { useState } from 'react';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox } from '@/shared/components/Status';
import { Title } from '@/shared/components/Text';
import { TextField } from '@/shared/components/TextField';
import { t } from '@/shared/i18n';

import { classesApi } from '../api/classesApi';

/** Join with an invite code, or become a rep with a rep code: the same box for both. */
export default function JoinClassScreen() {
  const [code, setCode] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function join() {
    setBusy(true);
    setError(null);
    try {
      const answer = await classesApi.join(code.trim());
      router.replace({ pathname: '/classes/[id]', params: { id: answer.class.id } });
    } catch (e) {
      setError(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Screen back footer={<Button title={t('classes.join')} variant="accent" onPress={join} loading={busy} disabled={!code.trim()} />}>
      <Title>{t('classes.join')}</Title>
      <TextField label={t('classes.code')} value={code} onChangeText={setCode} autoCapitalize="characters" autoCorrect={false} maxLength={40} hint={t('classes.codeHint')} />
      {error ? <ErrorBox message={error} /> : null}
    </Screen>
  );
}
