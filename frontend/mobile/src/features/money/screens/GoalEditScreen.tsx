/**
 * Add or change a pot or goal: what it's for, kind (goal, family, stokvel, buffer, big purchase),
 * how much, how much is already aside, and by when (for date goals). Opened from one of the
 * university's fee dates, the name and date come filled in and marked as the university's; the amount always comes
 * from the student (their own fee statement), never from us.
 */
import { router, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { InfoNote, ToggleRow } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { SelectField, SelectOption } from '@/shared/components/SelectField';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { TextField } from '@/shared/components/TextField';
import { t } from '@/shared/i18n';
import { centsToInput, parseRand } from '@/shared/lib/money';

import { moneyApi } from '../api/moneyApi';
import { AmountField } from '../components/AmountField';
import { GoalInput, PotKind } from '../types';

const ISO = /^\d{4}-\d{2}-\d{2}$/;

const POT_OPTIONS: SelectOption<PotKind>[] = [
  { value: 'goal', label: 'Goal', subtitle: 'Target amount by a specific date', icon: 'target' },
  { value: 'family', label: 'Family', subtitle: 'Monthly amount you send home to family', icon: 'heart' },
  { value: 'stokvel', label: 'Stokvel', subtitle: 'Your monthly personal contribution', icon: 'users' },
  { value: 'buffer', label: 'Emergency buffer', subtitle: 'Target amount to keep aside', icon: 'shield' },
  { value: 'big_purchase', label: 'Big purchase', subtitle: 'Target amount by a date (optionally via stokvel)', icon: 'shopping-bag' },
];

export default function GoalEditScreen() {
  const params = useLocalSearchParams<{ id?: string; label?: string; due?: string; uni?: string; kind?: string }>();
  const editing = !!params.id && params.id !== 'new';
  const [loaded, setLoaded] = useState(!editing);
  const [kind, setKind] = useState<PotKind>((params.kind as PotKind) ?? 'goal');
  const [label, setLabel] = useState(params.label ?? '');
  const [amount, setAmount] = useState('');
  const [saved, setSaved] = useState('');
  const [due, setDue] = useState(params.due ?? '');
  const [fromUniversity, setFromUniversity] = useState(params.uni === '1');
  const [stokvelFunded, setStokvelFunded] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [failure, setFailure] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!editing) return;
    moneyApi
      .plan()
      .then(({ goals }) => {
        const g = goals.find((x) => x.id === params.id);
        if (g) {
          setLabel(g.label);
          setKind(g.kind ?? 'goal');
          setAmount(centsToInput(g.amount_cents));
          setSaved(g.saved_cents ? centsToInput(g.saved_cents) : '');
          setDue(g.due_on ?? '');
          setFromUniversity(g.from_university);
          setStokvelFunded(Boolean(g.stokvel_funded));
        }
        setLoaded(true);
      })
      .catch((e) => setFailure(errorText(e, t('common.error'))));
  }, [editing, params.id]);

  const hasDueDate = kind === 'goal' || kind === 'big_purchase';
  const isMonthly = kind === 'family' || kind === 'stokvel';

  async function save() {
    const amountCents = parseRand(amount);
    const savedCents = saved.trim() ? parseRand(saved) : 0;
    const found: Record<string, string> = {};
    if (!label.trim()) found.label = t('money.goal.labelMissing');
    if (amountCents == null || amountCents <= 0) found.amount = t('money.afford.priceInvalid');
    if (savedCents == null || (amountCents != null && savedCents > amountCents)) found.saved = t('money.goal.savedTooMuch');
    if (hasDueDate && !ISO.test(due)) found.due = t('money.goal.dateFormat');
    setErrors(found);
    if (Object.keys(found).length) return;

    const input: GoalInput = {
      label: label.trim(),
      kind,
      amount_cents: amountCents!,
      saved_cents: savedCents!,
      due_on: hasDueDate ? due : null,
      from_university: fromUniversity,
      stokvel_funded: kind === 'big_purchase' ? stokvelFunded : false,
    };
    setBusy(true);
    setFailure(null);
    try {
      if (editing) await moneyApi.changeGoal(params.id as string, input);
      else await moneyApi.addGoal(input);
      router.back();
    } catch (e) {
      setFailure(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    setBusy(true);
    try {
      await moneyApi.removeGoal(params.id as string);
      router.back();
    } catch (e) {
      setFailure(errorText(e, t('common.error')));
      setBusy(false);
    }
  }

  const labelPlaceholder =
    kind === 'family'
      ? 'Family support'
      : kind === 'stokvel'
        ? 'December stokvel'
        : kind === 'buffer'
          ? 'Emergency buffer'
          : t('money.goal.labelExample');

  const amountLabel = isMonthly ? t('money.pots.amountMonthly') : t('money.pots.amountTarget');
  const amountHint = fromUniversity
    ? t('money.goal.amountHint')
    : kind === 'family'
      ? 'What you send home each month'
      : kind === 'stokvel'
        ? 'Your personal monthly contribution'
        : undefined;

  return (
    <Screen
      back
      title={editing ? t('money.pots.changeTitle') : t('money.pots.addTitle')}
      footer={
        <View style={{ flexDirection: 'row', gap: 10 }}>
          {editing ? <Button compact title={t('timetable.delete')} variant="secondary" icon="trash-2" onPress={remove} disabled={busy} /> : null}
          <Button compact title={t('timetable.save')} variant="primary" onPress={save} loading={busy} disabled={!loaded} />
        </View>
      }>
      {!loaded && !failure ? <Loading /> : null}
      {failure ? <ErrorBox message={failure} /> : null}
      {fromUniversity ? <InfoNote icon="info">{t('money.goal.fromUniversity')}</InfoNote> : null}
      {!fromUniversity ? (
        <SelectField<PotKind>
          label={t('money.pots.kind')}
          sheetTitle={t('money.pots.kind')}
          options={POT_OPTIONS}
          value={kind}
          onChange={setKind}
        />
      ) : null}
      <TextField label={t('money.goal.label')} value={label} onChangeText={setLabel} maxLength={80} error={errors.label} placeholder={labelPlaceholder} />
      <AmountField label={amountLabel} value={amount} onChange={setAmount} error={errors.amount} hint={amountHint} />
      <AmountField label={t('money.goal.saved')} value={saved} onChange={setSaved} error={errors.saved} />
      {hasDueDate ? (
        <TextField label={t('money.goal.due')} value={due} onChangeText={setDue} maxLength={10} placeholder="2027-03-31" keyboardType="numbers-and-punctuation" error={errors.due} />
      ) : null}
      {kind === 'big_purchase' ? (
        <ToggleRow
          icon="users"
          title={t('money.pots.stokvelFunded')}
          subtitle={t('money.pots.stokvelFundedHint')}
          value={stokvelFunded}
          onChange={setStokvelFunded}
        />
      ) : null}
    </Screen>
  );
}
