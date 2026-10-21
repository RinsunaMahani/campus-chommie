/**
 * Add or change a goal: what it's for, how much, how much is already aside, and by when. Opened from one of the
 * university's fee dates, the name and date come filled in and marked as the university's; the amount always comes
 * from the student (their own fee statement), never from us.
 */
import { router, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { TextField } from '@/shared/components/TextField';
import { t } from '@/shared/i18n';
import { centsToInput, parseRand } from '@/shared/lib/money';

import { moneyApi } from '../api/moneyApi';
import { AmountField } from '../components/AmountField';

const ISO = /^\d{4}-\d{2}-\d{2}$/;

export default function GoalEditScreen() {
  const params = useLocalSearchParams<{ id?: string; label?: string; due?: string; uni?: string }>();
  const editing = !!params.id && params.id !== 'new';
  const [loaded, setLoaded] = useState(!editing);
  const [label, setLabel] = useState(params.label ?? '');
  const [amount, setAmount] = useState('');
  const [saved, setSaved] = useState('');
  const [due, setDue] = useState(params.due ?? '');
  const [fromUniversity, setFromUniversity] = useState(params.uni === '1');
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
          setAmount(centsToInput(g.amount_cents));
          setSaved(g.saved_cents ? centsToInput(g.saved_cents) : '');
          setDue(g.due_on);
          setFromUniversity(g.from_university);
        }
        setLoaded(true);
      })
      .catch((e) => setFailure(errorText(e, t('common.error'))));
  }, [editing, params.id]);

  async function save() {
    const amountCents = parseRand(amount);
    const savedCents = saved.trim() ? parseRand(saved) : 0;
    const found: Record<string, string> = {};
    if (!label.trim()) found.label = t('money.goal.labelMissing');
    if (amountCents == null || amountCents <= 0) found.amount = t('money.afford.priceInvalid');
    if (savedCents == null || (amountCents != null && savedCents > amountCents)) found.saved = t('money.goal.savedTooMuch');
    if (!ISO.test(due)) found.due = t('money.goal.dateFormat');
    setErrors(found);
    if (Object.keys(found).length) return;
    const input = { label: label.trim(), amount_cents: amountCents!, saved_cents: savedCents!, due_on: due, from_university: fromUniversity };
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

  return (
    <Screen
      back
      title={editing ? t('money.goal.changeTitle') : t('money.goal.addTitle')}
      footer={
        <View style={{ flexDirection: 'row', gap: 10 }}>
          {editing ? <Button compact title={t('timetable.delete')} variant="secondary" icon="trash-2" onPress={remove} disabled={busy} /> : null}
          <Button compact title={t('timetable.save')} variant="primary" onPress={save} loading={busy} disabled={!loaded} />
        </View>
      }>
      {!loaded && !failure ? <Loading /> : null}
      {failure ? <ErrorBox message={failure} /> : null}
      {fromUniversity ? <InfoNote icon="info">{t('money.goal.fromUniversity')}</InfoNote> : null}
      <TextField label={t('money.goal.label')} value={label} onChangeText={setLabel} maxLength={80} error={errors.label} placeholder={t('money.goal.labelExample')} />
      <AmountField label={t('money.goal.amount')} value={amount} onChange={setAmount} error={errors.amount} hint={fromUniversity ? t('money.goal.amountHint') : undefined} />
      <AmountField label={t('money.goal.saved')} value={saved} onChange={setSaved} error={errors.saved} />
      <TextField label={t('money.goal.due')} value={due} onChangeText={setDue} maxLength={10} placeholder="2027-03-31" keyboardType="numbers-and-punctuation" error={errors.due} />
    </Screen>
  );
}
