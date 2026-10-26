import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { EmptyState } from '@/shared/components/EmptyState';
import { Card, ToggleRow } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Muted, Overline, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { formatDay } from '@/shared/lib/dates';
import { fonts, radius } from '@/shared/theme/tokens';

import { updatesApi } from '../api/updatesApi';
import { Switch, Update } from '../types';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';

/**
 * Updates: a rep's confirmed changes to a class, reminders for funding the
 * student saved, and account security alerts. A class update opens its class.
 * The switches turn topics off; security alerts always come.
 */
export default function UpdatesScreen() {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const [updates, setUpdates] = useState<Update[] | null>(null);
  const [switches, setSwitches] = useState<Switch[]>([]);
  const [error, setError] = useState<string | null>(null);

  useFocusEffect(
    useCallback(() => {
      Promise.all([updatesApi.list(), updatesApi.switches()])
        .then(([list, sw]) => {
          setUpdates(list);
          setSwitches(sw);
          setError(null);
        })
        .catch((e) => setError(errorText(e, t('common.error'))));
    }, []),
  );

  function open(u: Update) {
    if (!u.read_at) {
      updatesApi.read(u.id).catch(() => undefined);
      setUpdates((list) => (list ?? []).map((x) => (x.id === u.id ? { ...x, read_at: new Date().toISOString() } : x)));
    }
    if (u.link?.type === 'class') router.push({ pathname: '/classes/[id]', params: { id: u.link.id } });
    if (u.link?.type === 'funding') router.push({ pathname: '/course-finder/funding/[id]', params: { id: u.link.id } });
    if (u.link?.type === 'review') router.push('/review');
  }

  async function readAll() {
    try {
      await updatesApi.readAll();
      setUpdates((list) => (list ?? []).map((x) => ({ ...x, read_at: x.read_at ?? new Date().toISOString() })));
    } catch (e) {
      setError(errorText(e, t('common.error')));
    }
  }

  async function toggle(topic: string, on: boolean) {
    try {
      setSwitches(await updatesApi.setSwitch(topic, on));
    } catch (e) {
      setError(errorText(e, t('common.error')));
    }
  }

  const unread = (updates ?? []).filter((u) => !u.read_at).length;

  return (
    <Screen back>
      <Title>{t('updates.title')}</Title>
      {error ? <ErrorBox message={error} /> : null}
      {!error && !updates ? <Loading /> : null}
      {updates && !updates.length ? <EmptyState icon="bell" title={t('updates.noneTitle')} body={t('updates.none')} /> : null}
      {unread > 0 ? <Button title={t('updates.readAll')} variant="secondary" icon="check" onPress={readAll} /> : null}
      {updates?.map((u) => (
        <Pressable key={u.id} accessibilityRole="button" onPress={() => open(u)}>
          <Card style={{ gap: 4, ...(u.read_at ? {} : { borderColor: colors.accent }) }}>
            <View style={styles.head}>
              {u.read_at ? null : <View style={styles.dot} accessibilityLabel={t('alerts.unread', { n: 1 })} />}
              <Text style={styles.title}>{u.title}</Text>
            </View>
            <Text style={styles.body}>{u.body}</Text>
            <Muted>{formatDay(u.created_at.slice(0, 10))}</Muted>
          </Card>
        </Pressable>
      ))}

      {switches.length ? (
        <View style={{ gap: 8 }}>
          <Overline>{t('updates.switches')}</Overline>
          {switches.map((s) => (
            <ToggleRow key={s.topic} icon="bell" title={s.label} subtitle="" value={s.on} onChange={(on) => toggle(s.topic, on)} />
          ))}
          <Muted>{t('updates.switchesHint')}</Muted>
        </View>
      ) : null}
    </Screen>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  head: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  dot: { width: 8, height: 8, borderRadius: radius.pill, backgroundColor: colors.accent },
  title: { flex: 1, fontFamily: fonts.bold, fontSize: 15.5, color: colors.text },
  body: { fontFamily: fonts.body, fontSize: 14.5, lineHeight: 20, color: colors.text },
});
