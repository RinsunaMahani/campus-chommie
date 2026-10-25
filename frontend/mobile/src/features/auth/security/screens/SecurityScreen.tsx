import { Feather } from '@expo/vector-icons';
import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';

import { AuthError } from '@/features/auth/types';
import { studentHeader } from '@/features/profile/components/HeaderTools';
import { Button } from '@/shared/components/Button';
import { Card, IconTile, ListRow, Tag } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { t } from '@/shared/i18n';
import { Overline } from '@/shared/components/Text';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts } from '@/shared/theme/tokens';

import { securityApi, SignedInPhone } from '../api/securityApi';

function when(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-ZA', { day: 'numeric', month: 'short' }) + ', ' + d.toLocaleTimeString('en-ZA', { hour: '2-digit', minute: '2-digit' });
}

/** Phones shown before "Show N more": this one, then the most recently used. */
const SHOWN = 4;

/** This phone first, then the most recently used. */
export function phoneOrder(phones: SignedInPhone[]): SignedInPhone[] {
  return [...phones].sort((a, b) => Number(b.this_phone) - Number(a.this_phone) || b.last_used_at.localeCompare(a.last_used_at));
}

/** Home -> Account security: where you're signed in (this phone and the latest few, the rest a tap away), your
 * password, your data, your account. */
export default function SecurityScreen() {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const [phones, setPhones] = useState<SignedInPhone[] | null>(null);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [all, setAll] = useState(false);

  const load = useCallback(() => {
    securityApi
      .phones()
      .then(setPhones)
      .catch((e) => setMessage(e instanceof AuthError ? e.message : "Couldn't load your phones."));
  }, []);
  useFocusEffect(load);

  const others = (phones ?? []).filter((p) => !p.this_phone).length;

  async function signOutOthers() {
    setBusy(true);
    try {
      const n = await securityApi.signOutOthers();
      setMessage(n ? `Signed out of ${n} other phone${n > 1 ? 's' : ''}.` : 'No other phones were signed in.');
      load();
    } catch (e) {
      setMessage(e instanceof AuthError ? e.message : 'Something went wrong. Try again.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <Screen back title="Security" {...studentHeader(false)}>
      <Overline>Where you&apos;re signed in</Overline>
      {!phones ? (
        <ActivityIndicator color={colors.accent} />
      ) : (
        <Card style={{ gap: 12 }}>
          {(all ? phoneOrder(phones) : phoneOrder(phones).slice(0, SHOWN)).map((p) => (
            <View key={p.id} style={styles.phone}>
              <IconTile name="smartphone" size={36} />
              <View style={{ flex: 1 }}>
                <Text style={styles.phoneName}>{p.label || (p.platform === 'ios' ? 'iPhone' : 'Android phone')}</Text>
                <Text style={styles.phoneSub}>Last used {when(p.last_used_at)}</Text>
              </View>
              {p.this_phone ? <Tag label="This phone" tone="jade" /> : null}
            </View>
          ))}
          {phones.length > SHOWN ? (
            <Pressable accessibilityRole="button" onPress={() => setAll((a) => !a)} hitSlop={6} style={styles.more}>
              <Text style={styles.moreText}>{all ? 'Show fewer' : `Show ${phones.length - SHOWN} more`}</Text>
              <Feather name={all ? 'chevron-up' : 'chevron-down'} size={16} color={colors.accentDeep} />
            </Pressable>
          ) : null}
          {others > 0 ? <Button title="Sign out other phones" variant="secondary" icon="log-out" onPress={signOutOthers} loading={busy} /> : null}
        </Card>
      )}

      {message ? (
        <View style={styles.note}>
          <Feather name="info" size={14} color={colors.ink} />
          <Text style={styles.noteText}>{message}</Text>
        </View>
      ) : null}

      <Overline>Password and data</Overline>
      <Card style={{ paddingVertical: 4 }}>
        <ListRow icon="key" title="Change password" subtitle="Your other phones will be signed out" onPress={() => router.push('/change-password')} />
        <ListRow icon="user-x" title={t('delete.title')} subtitle={t('delete.sub')} onPress={() => router.push('/delete-account')} />
        <ListRow icon="trash-2" title="Close my account" subtitle="Ends every session on every phone" danger onPress={() => router.push('/close-account')} last />
      </Card>
    </Screen>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
  phone: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  phoneName: { fontFamily: fonts.bold, fontSize: 15.5, color: colors.text },
  phoneSub: { fontFamily: fonts.body, fontSize: 13.5, color: colors.textMuted, marginTop: 2 },
  more: { flexDirection: 'row', alignItems: 'center', gap: 4, alignSelf: 'flex-start', paddingVertical: 4 },
  moreText: { fontFamily: fonts.bold, fontSize: 14.5, color: colors.accentDeep },
  note: { flexDirection: 'row', gap: 8, backgroundColor: colors.iconTile, borderRadius: 10, padding: 12 },
  noteText: { flex: 1, fontFamily: fonts.medium, fontSize: 14, color: colors.text },
});
