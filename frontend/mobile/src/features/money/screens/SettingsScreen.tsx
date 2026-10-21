import { router } from 'expo-router';
import { useEffect, useState } from 'react';
import { View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Muted, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { formatDay, todaySast } from '@/shared/lib/dates';
import { centsToInput, parseRand } from '@/shared/lib/money';

import { moneyApi } from '../api/moneyApi';
import { AmountField } from '../components/AmountField';
import { Settings } from '../types';

type Field = 'balance' | 'essentials' | 'reserve';

/**
 * Balance and budget. The balance is true on a day: a new one is today's; an
 * unchanged one keeps its own day, so the app keeps counting spending and
 * payments from when it was really true.
 */
export default function SettingsScreen() {
  const [saved, setSaved] = useState<Settings | null | undefined>(undefined);
  const [values, setValues] = useState<Record<Field, string>>({ balance: '', essentials: '', reserve: '' });
  const [errors, setErrors] = useState<Partial<Record<Field, string>>>({});
  const [failure, setFailure] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    moneyApi
      .settings()
      .then((s) => {
        setSaved(s);
        if (s) {
          setValues({
            balance: centsToInput(s.balance_cents),
            essentials: centsToInput(s.essentials_per_day_cents),
            reserve: centsToInput(s.life_fund_reserve_cents),
          });
        }
      })
      .catch((e) => setFailure(errorText(e, t('common.error'))));
  }, []);

  function set(field: Field, text: string) {
    setValues((v) => ({ ...v, [field]: text }));
    setErrors((e) => ({ ...e, [field]: undefined }));
  }

  async function save() {
    const cents = {
      balance: parseRand(values.balance),
      essentials: parseRand(values.essentials),
      reserve: values.reserve.trim() ? parseRand(values.reserve) : 0,
    };
    const bad = (Object.keys(cents) as Field[]).filter((f) => cents[f] === null);
    if (bad.length) {
      setErrors(Object.fromEntries(bad.map((f) => [f, t('money.amountInvalid')])));
      return;
    }
    const balance = cents.balance as number;
    const sameBalance = saved != null && saved.balance_cents === balance;
    setBusy(true);
    setFailure(null);
    try {
      await moneyApi.saveSettings({
        balance_cents: balance,
        balance_on: sameBalance && saved ? saved.balance_on : todaySast(),
        essentials_per_day_cents: cents.essentials as number,
        life_fund_reserve_cents: cents.reserve as number,
      });
      router.back();
    } catch (e) {
      setFailure(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Screen back footer={<Button title={t('money.save')} variant="accent" onPress={save} loading={busy} disabled={saved === undefined} />}>
      <Title>{t('money.settings')}</Title>
      {saved === undefined && !failure ? <Loading /> : null}
      {failure ? <ErrorBox message={failure} /> : null}
      <View style={{ gap: 14 }}>
        <AmountField label={t('money.balance')} value={values.balance} onChange={(v) => set('balance', v)} hint={t('money.balanceHint')} error={errors.balance} />
        {saved ? <Muted>{t('money.balanceAsOf', { date: formatDay(saved.balance_on) })}</Muted> : null}
        <AmountField label={t('money.essentials')} value={values.essentials} onChange={(v) => set('essentials', v)} hint={t('money.essentialsHint')} error={errors.essentials} />
        <AmountField label={t('money.reserve')} value={values.reserve} onChange={(v) => set('reserve', v)} hint={t('money.reserveHint')} error={errors.reserve} />
      </View>
      <InfoNote icon="lock">{t('onboarding.privacyNever')}</InfoNote>
    </Screen>
  );
}
