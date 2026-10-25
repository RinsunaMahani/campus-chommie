import { Feather } from '@expo/vector-icons';
import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { StyleSheet, View } from 'react-native';

import { studentHeader } from '@/features/profile/components/HeaderTools';
import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { EmptyState } from '@/shared/components/EmptyState';
import { Card, Tag } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Muted, Strong } from '@/shared/components/Text';
import { t } from '@/shared/i18n';

import { classesApi } from '../api/classesApi';
import { ClassSummary } from '../types';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';

/** The student's classes, as rep or student, with counts only: nobody is ever listed. */
export default function ClassesScreen() {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const [classes, setClasses] = useState<ClassSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useFocusEffect(
    useCallback(() => {
      classesApi
        .mine()
        .then((list) => {
          setClasses(list);
          setError(null);
        })
        .catch((e) => setError(errorText(e, t('common.error'))));
    }, []),
  );

  return (
    <Screen
      back
      title={t('classes.title')}
      {...studentHeader(false)}
      footer={
        <View style={{ flexDirection: 'row', gap: 10 }}>
          <Button compact title={t('classes.create')} variant="secondary" icon="plus" onPress={() => router.push('/classes/new')} />
          <Button compact title={t('classes.join')} variant="accent" icon="log-in" onPress={() => router.push('/classes/join')} />
        </View>
      }>
      {error ? <ErrorBox message={error} /> : null}
      {!error && !classes ? <Loading /> : null}
      {classes && !classes.length ? <EmptyState icon="users" title={t('classes.emptyTitle')} body={t('classes.empty')} /> : null}
      {classes?.map((c) => (
        <Card key={c.id} onPress={() => router.push({ pathname: '/classes/[id]', params: { id: c.id } })} style={styles.card}>
          <View style={{ flex: 1, gap: 4 }}>
            <Strong>{c.module_name ? `${c.module_code} · ${c.module_name}` : c.module_code}</Strong>
            <Muted>{t('classes.counts', { members: c.members, reps: c.reps })}</Muted>
            <Tag label={c.role === 'rep' ? t('classes.rep') : t('classes.student')} tone={c.role === 'rep' ? 'jade' : 'muted'} />
          </View>
          <Feather name="chevron-right" size={18} color={colors.textFaint} />
        </Card>
      ))}
    </Screen>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  card: { flexDirection: 'row', alignItems: 'center', gap: 12 },
});
