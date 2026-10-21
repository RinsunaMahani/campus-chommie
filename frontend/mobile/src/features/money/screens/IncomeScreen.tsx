import { Feather } from '@expo/vector-icons';
import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { StyleSheet, View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Card, Tag } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Body, Muted, Strong, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { formatRand } from '@/shared/lib/money';
import { colors } from '@/shared/theme/tokens';

import { moneyApi } from '../api/moneyApi';
import { IncomeSource } from '../types';
import { reliabilityLabel, scheduleText } from '../words';

/** Money coming in: each source, when it comes and how reliable it is. Tap one to change it. */
export default function IncomeScreen() {
  const [sources, setSources] = useState<IncomeSource[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useFocusEffect(
    useCallback(() => {
      moneyApi
        .incomeSources()
        .then((list) => {
          setSources(list);
          setError(null);
        })
        .catch((e) => setError(errorText(e, t('common.error'))));
    }, []),
  );

  return (
    <Screen back footer={<Button title={t('money.incomeAdd')} variant="accent" icon="plus" onPress={() => router.push('/money/income-edit')} />}>
      <View style={{ gap: 4 }}>
        <Title>{t('money.income')}</Title>
        <Muted>{t('money.incomeSub')}</Muted>
      </View>
      {error ? <ErrorBox message={error} /> : null}
      {!error && !sources ? <Loading /> : null}
      {sources && !sources.length ? <Body>{t('money.incomeEmpty')}</Body> : null}
      {sources?.map((s) => (
        <Card key={s.id} onPress={() => router.push({ pathname: '/money/income-edit', params: { id: s.id } })} style={styles.card}>
          <View style={{ flex: 1, gap: 4 }}>
            <Strong>{s.label}</Strong>
            <Body>{`${formatRand(s.amount_cents)} · ${scheduleText(s)}`}</Body>
            <Tag label={reliabilityLabel(s.reliability)} tone={s.reliability === 'on_time' ? 'jade' : s.reliability === 'not_sure' ? 'muted' : 'marigold'} />
          </View>
          <Feather name="chevron-right" size={18} color={colors.textFaint} />
        </Card>
      ))}
    </Screen>
  );
}

const styles = StyleSheet.create({
  card: { flexDirection: 'row', alignItems: 'center', gap: 12 },
});
