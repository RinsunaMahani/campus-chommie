import { Feather } from '@expo/vector-icons';
import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { StyleSheet, View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Card } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Body, Muted, Overline, Strong, Title } from '@/shared/components/Text';
import { TextField } from '@/shared/components/TextField';
import { t } from '@/shared/i18n';
import { colors } from '@/shared/theme/tokens';

import { marksApi } from '../api/marksApi';
import { Module } from '../types';

/** My marks: each module with where the student stands. Only the student sees them (owner-only). */
export default function MarksScreen() {
  const [modules, setModules] = useState<Module[] | null>(null);
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [target, setTarget] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useFocusEffect(
    useCallback(() => {
      marksApi
        .modules()
        .then((list) => {
          setModules(list);
          setError(null);
        })
        .catch((e) => setError(errorText(e, t('common.error'))));
    }, []),
  );

  async function add() {
    const goal = target.trim() ? Number(target.replace(',', '.')) : undefined;
    if (!code.trim()) return setFormError(t('marks.codeMissing'));
    if (goal !== undefined && !(goal >= 0 && goal <= 100)) return setFormError(t('marks.percentInvalid'));
    setBusy(true);
    setFormError(null);
    try {
      const created = await marksApi.addModule({ code: code.trim(), name: name.trim() || null, ...(goal !== undefined ? { target: goal } : {}) });
      setModules((list) => [...(list ?? []), created]);
      setCode('');
      setName('');
      setTarget('');
    } catch (e) {
      setFormError(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Screen back>
      <Title>{t('marks.title')}</Title>
      {error ? <ErrorBox message={error} /> : null}
      {!error && !modules ? <Loading /> : null}
      {modules && !modules.length ? <Body>{t('marks.empty')}</Body> : null}
      {modules?.map((m) => (
        <Card key={m.id} onPress={() => router.push({ pathname: '/marks/[id]', params: { id: m.id } })} style={styles.card}>
          <View style={{ flex: 1, gap: 4 }}>
            <Strong>{m.name ? `${m.code} · ${m.name}` : m.code}</Strong>
            <Muted>{m.standing.message}</Muted>
          </View>
          <Feather name="chevron-right" size={18} color={colors.textFaint} />
        </Card>
      ))}

      <Overline>{t('marks.addModule')}</Overline>
      <TextField label={t('marks.code')} value={code} onChangeText={setCode} autoCapitalize="characters" maxLength={20} />
      <TextField label={t('marks.name')} value={name} onChangeText={setName} maxLength={80} optional />
      <TextField label={t('marks.target')} value={target} onChangeText={setTarget} keyboardType="decimal-pad" maxLength={5} hint={t('marks.targetHint')} />
      {formError ? <ErrorBox message={formError} /> : null}
      <Button title={t('marks.addModule')} variant="secondary" icon="plus" onPress={add} loading={busy} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  card: { flexDirection: 'row', alignItems: 'center', gap: 12 },
});
