import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { EmptyState } from '@/shared/components/EmptyState';
import { Card, Tag } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Body, Muted, Strong, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { formatDay } from '@/shared/lib/dates';
import { formatRand } from '@/shared/lib/money';

import { moneyApi } from '../api/moneyApi';
import { Payment } from '../types';

/** Expected payments, from a month back to four months ahead: tap one when it arrives. */
export default function PaymentsScreen() {
  const [payments, setPayments] = useState<Payment[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  useFocusEffect(
    useCallback(() => {
      moneyApi
        .payments()
        .then((list) => {
          setPayments(list);
          setError(null);
        })
        .catch((e) => setError(errorText(e, t('common.error'))));
    }, []),
  );

  async function setReceived(p: Payment, received: boolean) {
    setBusy(p.id);
    setError(null);
    try {
      const updated = await moneyApi.setReceived(p.id, received);
      setPayments((list) => (list ?? []).map((x) => (x.id === updated.id ? updated : x)));
    } catch (e) {
      setError(errorText(e, t('common.error')));
    } finally {
      setBusy(null);
    }
  }

  return (
    <Screen back>
      <View style={{ gap: 4 }}>
        <Title>{t('money.payments')}</Title>
        <Muted>{t('money.paymentsSub')}</Muted>
      </View>
      {error ? <ErrorBox message={error} /> : null}
      {!error && !payments ? <Loading /> : null}
      {payments && !payments.length ? (
        <EmptyState
          icon="calendar"
          title={t('money.paymentsEmptyTitle')}
          body={t('money.paymentsEmpty')}
          action={{ label: t('money.incomeAdd'), onPress: () => router.push('/money/income-edit') }}
        />
      ) : null}
      {payments?.map((p) => (
        <Card key={p.id} style={{ gap: 8 }}>
          <Strong>{p.label}</Strong>
          <Body>{`${formatRand(p.amount_cents)} · ${t('money.expected', { date: formatDay(p.expected_on) })}`}</Body>
          {p.received ? (
            <Tag label={p.received_on ? `${t('money.received')}: ${formatDay(p.received_on)}` : t('money.received')} tone="jade" />
          ) : p.overdue ? (
            <Tag label={t('money.overdue')} tone="marigold" />
          ) : null}
          <Button
            title={p.received ? t('money.undoReceived') : t('money.markReceived')}
            variant={p.received ? 'secondary' : 'primary'}
            icon={p.received ? 'rotate-ccw' : 'check'}
            onPress={() => setReceived(p, !p.received)}
            loading={busy === p.id}
          />
        </Card>
      ))}
    </Screen>
  );
}
