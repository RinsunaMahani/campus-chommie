import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';

import { studentHeader } from '@/features/profile/components/HeaderTools';
import { useProfile } from '@/features/profile/state';
import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Card, InfoNote, ListRow } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Body, Strong } from '@/shared/components/Text';
import { t } from '@/shared/i18n';

import { moneyApi } from '../api/moneyApi';
import { LifeFundCard, NextPaymentCard, RunwayCard, SafeToSpendCard } from '../components/MoneyCards';
import { Summary } from '../types';

/**
 * The Money tab: the balance now and how long it lasts, what's safe to spend,
 * the life fund, and the next payment with the "two weeks late" plan. It reloads
 * whenever the tab comes back into view, so a new number shows straight away.
 */
export default function MoneyScreen() {
  const { mock } = useProfile();
  const [late, setLate] = useState(false);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback((asLate: boolean) => {
    moneyApi
      .summary(asLate)
      .then((s) => {
        setSummary(s);
        setError(null);
      })
      .catch((e) => setError(errorText(e, t('common.error'))))
      .finally(() => setRefreshing(false));
  }, []);

  useFocusEffect(
    useCallback(() => {
      if (!mock) load(late);
    }, [load, late, mock]),
  );

  if (mock) {
    return (
      <Screen tab title={t('money.title')}>
        <InfoNote icon="info">{t('money.mockNotice')}</InfoNote>
      </Screen>
    );
  }

  return (
    <Screen
      tab
      onRefresh={() => {
        setRefreshing(true);
        load(late);
      }}
      refreshing={refreshing}
      title={t('money.title')}
      {...studentHeader()}>

      {error ? <ErrorBox message={error} onRetry={() => load(late)} /> : null}
      {!error && !summary ? <Loading /> : null}
      {summary && !summary.ready ? (
        <Card style={{ gap: 10 }}>
          <Strong>{t('money.setupTitle')}</Strong>
          <Body>{t('money.setupIntro')}</Body>
          {summary.lines.map((line, i) => (
            <Body key={i}>{line}</Body>
          ))}
          <Button title={t('money.settings')} variant="accent" onPress={() => router.push('/money/settings')} />
        </Card>
      ) : null}
      {summary && summary.ready ? (
        <>
          <RunwayCard summary={summary} />
          <SafeToSpendCard summary={summary} />
          <LifeFundCard summary={summary} />
          <NextPaymentCard summary={summary} onLate={setLate} />
          {summary.notes.map((note, i) => (
            <InfoNote key={i} icon="info">
              {note}
            </InfoNote>
          ))}
        </>
      ) : null}

      <Button title={t('money.logToday')} variant="accent" icon="edit-3" onPress={() => router.push('/money/spending')} />

      <Card style={{ paddingVertical: 4 }}>
        <ListRow icon="sliders" title={t('money.settings')} subtitle={t('money.settingsSub')} onPress={() => router.push('/money/settings')} />
        <ListRow icon="download" title={t('money.income')} subtitle={t('money.incomeSub')} onPress={() => router.push('/money/income')} />
        <ListRow icon="calendar" title={t('money.payments')} subtitle={t('money.paymentsSub')} onPress={() => router.push('/money/payments')} />
        <ListRow icon="bar-chart-2" title={t('money.spending')} subtitle={t('money.spendingSub')} onPress={() => router.push('/money/spending')} />
        <ListRow icon="award" title={t('courseFinder.fundingTitle')} subtitle={t('courseFinder.fundingSub')} onPress={() => router.push('/course-finder/funding')} />
        <ListRow icon="map-pin" title={t('money.cheapThings')} subtitle={t('money.cheapThingsSub')} onPress={() => router.push('/money/cheap-things')} last />
      </Card>
    </Screen>
  );
}
