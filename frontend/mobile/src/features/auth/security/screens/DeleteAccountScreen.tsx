import { Feather } from '@expo/vector-icons';
import { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { useSession } from '@/features/auth/session/SessionProvider';
import { AuthError } from '@/features/auth/types';
import { Button } from '@/shared/components/Button';
import { Screen } from '@/shared/components/Screen';
import { Title } from '@/shared/components/Text';
import { TextField } from '@/shared/components/TextField';
import { t } from '@/shared/i18n';
import { colors, fonts, radius } from '@/shared/theme/tokens';

import { securityApi } from '../api/securityApi';

/**
 * POPIA: delete the account and everything kept about the student (DELETE
 * /me). The password is asked again, so someone who just picked up the phone
 * can't. Demo accounts are refused by the server, which says so.
 */
export default function DeleteAccountScreen() {
  const { signOut } = useSession();
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function remove() {
    if (!password) return setError(t('delete.passwordMissing'));
    setBusy(true);
    setError('');
    try {
      await securityApi.deleteAccount(password);
      signOut(); // the account is gone on the server
    } catch (e) {
      setError(e instanceof AuthError ? e.message : t('common.error'));
      setBusy(false);
    }
  }

  return (
    <Screen back footer={<Button title={t('delete.button')} variant="danger" onPress={remove} loading={busy} />}>
      <Title>{t('delete.title')}</Title>
      <View style={styles.box}>
        {(['delete.what1', 'delete.what2', 'delete.what3', 'delete.what4'] as const).map((key) => (
          <View key={key} style={styles.row}>
            <Feather name="alert-circle" size={15} color={colors.garnet} style={{ marginTop: 2 }} />
            <Text style={styles.text}>{t(key)}</Text>
          </View>
        ))}
      </View>
      <TextField label={t('delete.password')} password value={password} onChangeText={setPassword} autoComplete="current-password" error={error} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  box: { backgroundColor: colors.garnetTint, borderRadius: radius.md, padding: 14, gap: 10 },
  row: { flexDirection: 'row', gap: 10 },
  text: { flex: 1, fontFamily: fonts.medium, fontSize: 14.5, lineHeight: 19, color: colors.text },
});
