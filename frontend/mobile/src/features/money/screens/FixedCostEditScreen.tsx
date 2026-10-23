/**
 * Add or change a fixed monthly cost (rent, transport, data, phone).
 * Paid on a set calendar day each month.
 */
import { router, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Title } from '@/shared/components/Text';
import { TextField } from '@/shared/components/TextField';
import { t } from '@/shared/i18n';
import { centsToInput, parseRand } from '@/shared/lib/money';

import { moneyApi } from '../api/moneyApi';
import { AmountField } from '../components/AmountField';

export default function FixedCostEditScreen() {
  const params = useLocalSearchParams<{ id?: string }>();
  const editing = !!params.id && params.id !== 'new';
  const [loaded, setLoaded] = useState(!editing);
  const [label, setLabel] = useState('');
  const [amount, setAmount] = useState('');
  const [day, setDay] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [failure, setFailure] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!editing) return;
    moneyApi
      .fixedCosts()
      .then((costs) => {
        const c = costs.find((x) => x.id === params.id);
        if (c) {
          setLabel(c.label);
          setAmount(centsToInput(c.amount_cents));
          setDay(String(c.day_of_month));
        }
        setLoaded(true);
      })
      .catch((e) => setFailure(errorText(e, t('common.error'))));
  }, [editing, params.id]);

  async function save() {
    const errs: Record<string, string> = {};
    if (!label.trim()) errs.label = t('money.labelMissing');
    const cents = parseRand(amount);
    if (cents === null || cents <= 0) errs.amount = t('money.amountInvalid');
    const dayNum = parseInt(day.trim(), 10);
    if (isNaN(dayNum) || dayNum < 1 || dayNum > 31) {
      errs.day = t('money.fixedCosts.dayOfMonthInvalid');
    }

    if (Object.keys(errs).length) {
      setErrors(errs);
      return;
    }

    setBusy(true);
    setFailure(null);
    try {
      const payload = {
        label: label.trim(),
        amount_cents: cents as number,
        day_of_month: dayNum,
      };
      if (editing && params.id) {
        await moneyApi.updateFixedCost(params.id, payload);
      } else {
        await moneyApi.addFixedCost(payload);
      }
      router.back();
    } catch (e) {
      setFailure(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    if (!params.id) return;
    setBusy(true);
    setFailure(null);
    try {
      await moneyApi.removeFixedCost(params.id);
      router.back();
    } catch (e) {
      setFailure(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Screen
      back
      footer={
        <View style={{ gap: 8 }}>
          <Button
            title={t('money.save')}
            variant="accent"
            onPress={save}
            loading={busy}
            disabled={!loaded}
          />
          {editing ? (
            <Button
              title={t('money.delete')}
              variant="danger"
              onPress={remove}
              loading={busy}
              disabled={!loaded}
            />
          ) : null}
        </View>
      }>
      <Title>{editing ? t('money.fixedCosts.changeTitle') : t('money.fixedCosts.addTitle')}</Title>
      {!loaded && !failure ? <Loading /> : null}
      {failure ? <ErrorBox message={failure} /> : null}

      <View style={{ gap: 14 }}>
        <TextField
          label={t('money.label')}
          value={label}
          onChangeText={(v) => {
            setLabel(v);
            setErrors((e) => ({ ...e, label: '' }));
          }}
          placeholder={t('money.fixedCosts.labelHint')}
          error={errors.label}
        />
        <AmountField
          label={t('money.amount')}
          value={amount}
          onChange={(v) => {
            setAmount(v);
            setErrors((e) => ({ ...e, amount: '' }));
          }}
          error={errors.amount}
        />
        <TextField
          label={t('money.fixedCosts.dayOfMonth')}
          value={day}
          onChangeText={(v) => {
            setDay(v);
            setErrors((e) => ({ ...e, day: '' }));
          }}
          keyboardType="number-pad"
          placeholder="1"
          hint={t('money.fixedCosts.dayOfMonthHint')}
          error={errors.day}
        />
      </View>
      <InfoNote icon="lock">{t('onboarding.privacyNever')}</InfoNote>
    </Screen>
  );
}
