import { router, useLocalSearchParams } from 'expo-router';
import { useEffect, useMemo, useState } from 'react';
import { View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Screen } from '@/shared/components/Screen';
import { SelectField } from '@/shared/components/SelectField';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Title } from '@/shared/components/Text';
import { TextField } from '@/shared/components/TextField';
import { t } from '@/shared/i18n';
import { dayInMonth, formatMonth, monthsFrom } from '@/shared/lib/dates';
import { centsToInput, parseRand } from '@/shared/lib/money';

import { moneyApi } from '../api/moneyApi';
import { AmountField } from '../components/AmountField';
import { IncomeInput, Reliability } from '../types';
import { RELIABILITY, reliabilityLabel } from '../words';

type Schedule = 'monthly' | 'once';

/** Add or change money coming in: what it is, how much, when, and how reliable. */
export default function IncomeEditScreen() {
  const { id } = useLocalSearchParams<{ id?: string }>();
  const months = useMemo(() => monthsFrom(0, 12), []);
  const [loaded, setLoaded] = useState(!id);
  const [label, setLabel] = useState('');
  const [amount, setAmount] = useState('');
  const [schedule, setSchedule] = useState<Schedule>('monthly');
  const [day, setDay] = useState('');
  const [month, setMonth] = useState<string>(months[0]);
  const [reliability, setReliability] = useState<Reliability>('not_sure');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [failure, setFailure] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!id) return;
    moneyApi
      .incomeSources()
      .then((list) => {
        const s = list.find((x) => x.id === id);
        if (s) {
          setLabel(s.label);
          setAmount(centsToInput(s.amount_cents));
          setReliability(s.reliability);
          if (s.day_of_month != null) {
            setSchedule('monthly');
            setDay(String(s.day_of_month));
          } else if (s.expected_on) {
            setSchedule('once');
            setDay(String(Number(s.expected_on.slice(8, 10))));
            setMonth(s.expected_on.slice(0, 7));
          }
        }
        setLoaded(true);
      })
      .catch((e) => setFailure(errorText(e, t('common.error'))));
  }, [id]);

  async function save() {
    const found: Record<string, string> = {};
    const cents = parseRand(amount);
    const dayNumber = Number(day);
    if (!label.trim()) found.label = t('money.labelMissing');
    if (cents === null || cents === 0) found.amount = t('money.amountInvalid');
    if (!/^\d{1,2}$/.test(day) || dayNumber < 1 || dayNumber > 31) found.day = t('money.dayInvalid');
    const date = schedule === 'once' && !found.day ? dayInMonth(month, dayNumber) : null;
    if (schedule === 'once' && !found.day && !date) found.day = t('money.dayInvalid');
    setErrors(found);
    if (Object.keys(found).length) return;

    const input: IncomeInput = {
      label: label.trim(),
      amount_cents: cents as number,
      day_of_month: schedule === 'monthly' ? dayNumber : null,
      expected_on: schedule === 'once' ? date : null,
      reliability,
    };
    setBusy(true);
    setFailure(null);
    try {
      if (id) await moneyApi.updateIncome(id, input);
      else await moneyApi.addIncome(input);
      router.back();
    } catch (e) {
      setFailure(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    if (!id) return;
    setBusy(true);
    try {
      await moneyApi.removeIncome(id);
      router.back();
    } catch (e) {
      setFailure(errorText(e, t('common.error')));
      setBusy(false);
    }
  }

  return (
    <Screen
      back
      footer={
        <View style={{ flexDirection: 'row', gap: 10 }}>
          {id ? <Button compact title={t('money.delete')} variant="secondary" icon="trash-2" onPress={remove} disabled={busy} /> : null}
          <Button compact title={t('money.save')} variant="accent" onPress={save} loading={busy} disabled={!loaded} />
        </View>
      }>
      <Title>{t('money.income')}</Title>
      {!loaded && !failure ? <Loading /> : null}
      {failure ? <ErrorBox message={failure} /> : null}
      <TextField label={t('money.label')} value={label} onChangeText={setLabel} maxLength={60} hint={t('money.labelHint')} error={errors.label} />
      <AmountField label={t('money.amount')} value={amount} onChange={setAmount} error={errors.amount} />
      <SelectField
        label={t('money.schedule')}
        value={schedule}
        options={[
          { value: 'monthly', label: t('money.monthly') },
          { value: 'once', label: t('money.once') },
        ]}
        onChange={(v) => setSchedule(v as Schedule)}
      />
      <TextField
        label={t('money.day')}
        value={day}
        onChangeText={(v) => setDay(v.replace(/[^0-9]/g, '').slice(0, 2))}
        keyboardType="number-pad"
        maxLength={2}
        placeholder="25"
        error={errors.day}
      />
      {schedule === 'once' ? (
        <SelectField label={t('money.month')} value={month} options={months.map((m) => ({ value: m, label: formatMonth(m) }))} onChange={setMonth} />
      ) : null}
      <SelectField
        label={t('money.reliability')}
        value={reliability}
        options={RELIABILITY.map((r) => ({ value: r, label: reliabilityLabel(r) }))}
        onChange={(v) => setReliability(v as Reliability)}
      />
    </Screen>
  );
}
