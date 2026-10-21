import { router } from 'expo-router';
import { useState } from 'react';

import { useProfile } from '@/features/profile/state';
import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox } from '@/shared/components/Status';
import { Title } from '@/shared/components/Text';
import { TextField } from '@/shared/components/TextField';
import { t } from '@/shared/i18n';
import { todaySast } from '@/shared/lib/dates';

import { classesApi } from '../api/classesApi';

/** Start a class for one module on the student's campus, this year: they become its first rep. */
export default function NewClassScreen() {
  const { profile } = useProfile();
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function create() {
    if (!profile?.university) return;
    setBusy(true);
    setError(null);
    try {
      const created = await classesApi.create({
        university: profile.university,
        campus: profile.campus,
        module_code: code.trim(),
        module_name: name.trim() || null,
        year: Number(todaySast().slice(0, 4)),
      });
      router.replace({ pathname: '/classes/[id]', params: { id: created.id } });
    } catch (e) {
      setError(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Screen back footer={<Button title={t('classes.create')} variant="accent" onPress={create} loading={busy} disabled={!code.trim()} />}>
      <Title>{t('classes.create')}</Title>
      <TextField label={t('classes.moduleCode')} value={code} onChangeText={setCode} autoCapitalize="characters" maxLength={20} hint={t('classes.moduleCodeHint')} />
      <TextField label={t('classes.moduleName')} value={name} onChangeText={setName} maxLength={80} optional />
      <InfoNote icon="info">{t('classes.createHint')}</InfoNote>
      {error ? <ErrorBox message={error} /> : null}
    </Screen>
  );
}
