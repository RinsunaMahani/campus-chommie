import { Feather } from '@expo/vector-icons';
import { useCallback, useEffect, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { EmptyState } from '@/shared/components/EmptyState';
import { Card, InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Muted, Overline, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { addDays, formatDay, todaySast } from '@/shared/lib/dates';
import { centsToInput, formatRand, parseRand } from '@/shared/lib/money';
import { fonts, radius } from '@/shared/theme/tokens';

import { moneyApi } from '../api/moneyApi';
import { AmountField } from '../components/AmountField';
import { SpendingDay } from '../types';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';

/** One spending number a day: today's or yesterday's, and the last 30 days. */
export default function SpendingScreen() {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const today = todaySast();
  const yesterday = addDays(today, -1);
  const [day, setDay] = useState(today);
  const [amount, setAmount] = useState('');
  const [days, setDays] = useState<SpendingDay[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fieldError, setFieldError] = useState<string | undefined>(undefined);
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState(false);

  const load = useCallback(() => {
    moneyApi
      .spending(30)
      .then((list) => {
        setDays(list);
        // Today already logged: start from that number.
        const entry = list.find((x) => x.spent_on === todaySast());
        setAmount((typed) => typed || (entry ? centsToInput(entry.amount_cents) : ''));
      })
      .catch((e) => setError(errorText(e, t('common.error'))));
  }, []);

  useEffect(load, [load]);

  function pick(d: string) {
    setDay(d);
    setSaved(false);
    const entry = days?.find((x) => x.spent_on === d);
    setAmount(entry ? centsToInput(entry.amount_cents) : '');
  }

  async function save() {
    const cents = parseRand(amount);
    if (cents === null) return setFieldError(t('money.amountInvalid'));
    setBusy(true);
    setError(null);
    try {
      const entry = await moneyApi.setSpending(day, cents);
      setDays((list) => [entry, ...(list ?? []).filter((x) => x.spent_on !== entry.spent_on)].sort((a, b) => b.spent_on.localeCompare(a.spent_on)));
      setSaved(true);
    } catch (e) {
      setError(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  async function remove(d: string) {
    setError(null);
    try {
      await moneyApi.removeSpending(d);
      setDays((list) => (list ?? []).filter((x) => x.spent_on !== d));
      if (d === day) setAmount('');
    } catch (e) {
      setError(errorText(e, t('common.error')));
    }
  }

  const dayWord = day === today ? t('money.spendingToday') : t('money.spendingYesterday');

  return (
    <Screen back footer={<Button title={t('money.save')} variant="accent" onPress={save} loading={busy} />}>
      <View style={{ gap: 4 }}>
        <Title>{t('money.spending')}</Title>
        <Muted>{t('money.spendingSub')}</Muted>
      </View>
      <View style={styles.chips}>
        {[today, yesterday].map((d) => {
          const on = d === day;
          return (
            <Pressable key={d} accessibilityRole="button" accessibilityState={{ selected: on }} onPress={() => pick(d)} style={[styles.chip, on && styles.chipOn]}>
              <Text style={[styles.chipText, on && styles.chipTextOn]}>{d === today ? t('money.spendingToday') : t('money.spendingYesterday')}</Text>
            </Pressable>
          );
        })}
      </View>
      <AmountField
        label={t('money.spendingLog', { day: dayWord.toLowerCase() })}
        value={amount}
        onChange={(v) => {
          setAmount(v);
          setFieldError(undefined);
          setSaved(false);
        }}
        error={fieldError}
      />
      {saved ? <InfoNote icon="check" tone="ok">{t('money.saved')}</InfoNote> : null}
      {error ? <ErrorBox message={error} /> : null}

      <Overline>{t('money.spendingRecent')}</Overline>
      {!days && !error ? <Loading /> : null}
      {days && !days.length ? <EmptyState icon="edit-3" title={t('money.spendingEmptyTitle')} body={t('money.spendingEmpty')} /> : null}
      {days && days.length ? (
        <Card style={{ paddingVertical: 4 }}>
          {days.map((d, i) => (
            <View key={d.spent_on} style={[styles.row, i < days.length - 1 && styles.rule]}>
              <Text style={styles.day}>{formatDay(d.spent_on)}</Text>
              <Text style={styles.amount}>{formatRand(d.amount_cents)}</Text>
              <Pressable accessibilityRole="button" accessibilityLabel={`${t('money.delete')}: ${formatDay(d.spent_on)}`} onPress={() => remove(d.spent_on)} hitSlop={8}>
                <Feather name="x" size={16} color={colors.textMuted} />
              </Pressable>
            </View>
          ))}
        </Card>
      ) : null}
    </Screen>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  chips: { flexDirection: 'row', gap: 8 },
  chip: { paddingHorizontal: 16, paddingVertical: 9, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.line, backgroundColor: colors.white },
  chipOn: { backgroundColor: colors.ink, borderColor: colors.ink },
  chipText: { fontFamily: fonts.semibold, fontSize: 14.5, color: colors.ink },
  chipTextOn: { color: colors.pillText },
  row: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 11 },
  rule: { borderBottomWidth: 1, borderBottomColor: colors.line },
  day: { flex: 1, fontFamily: fonts.medium, fontSize: 15, color: colors.text },
  amount: { fontFamily: fonts.bold, fontSize: 15, color: colors.ink, fontVariant: ['tabular-nums'] },
});
