/**
 * "Can I afford this?": the student types a price and sees, in one coloured word and a line or two, what buying
 * it today does to how long their money lasts, and when it would be fine instead. Nothing is stored: the price
 * goes to the server once and is dropped.
 */
import { Feather } from '@expo/vector-icons';
import { ComponentProps, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Card } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox } from '@/shared/components/Status';
import { t } from '@/shared/i18n';
import { parseRand } from '@/shared/lib/money';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, space, type } from '@/shared/theme/tokens';

import { moneyApi } from '../api/moneyApi';
import { AmountField } from '../components/AmountField';
import { AffordAnswer } from '../types';

type IconName = ComponentProps<typeof Feather>['name'];

export default function AffordScreen() {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const [price, setPrice] = useState('');
  const [answer, setAnswer] = useState<AffordAnswer | null>(null);
  const [problem, setProblem] = useState<string | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function check() {
    const cents = parseRand(price);
    if (cents == null || cents <= 0) {
      setProblem(t('money.afford.priceInvalid'));
      return;
    }
    setProblem(undefined);
    setBusy(true);
    setError(null);
    try {
      setAnswer(await moneyApi.afford(cents));
    } catch (e) {
      setError(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  const look: Record<AffordAnswer['verdict'], { word: string; colour: string; icon: IconName }> = {
    yes: { word: t('money.afford.yes'), colour: colors.jade, icon: 'check-circle' },
    tight: { word: t('money.afford.tight'), colour: colors.marigold, icon: 'alert-circle' },
    not_now: { word: t('money.afford.notNow'), colour: colors.garnet, icon: 'clock' },
  };
  const days = (n: number | null) => (n == null ? t('money.hero.beyond') : t('money.hero.days', { n }));

  return (
    <Screen back title={t('money.afford.title')} subtitle={t('money.afford.sub')}
      footer={<Button title={t('money.afford.check')} variant="primary" icon="search" onPress={check} loading={busy} />}>
      <AmountField label={t('money.afford.price')} value={price} onChange={(v) => { setPrice(v); setAnswer(null); }} error={problem} />
      {error ? <ErrorBox message={error} /> : null}
      {answer ? (
        <Card style={{ ...styles.card, borderColor: look[answer.verdict].colour }}>
          <View style={styles.verdict}>
            <Feather name={look[answer.verdict].icon} size={28} color={look[answer.verdict].colour} />
            <Text style={[styles.word, { color: look[answer.verdict].colour }]} accessibilityRole="header">
              {look[answer.verdict].word}
            </Text>
          </View>
          {answer.lines.map((line, i) => (
            <Text key={i} style={styles.line}>
              {line}
            </Text>
          ))}
          <View style={styles.compare}>
            <View style={{ flex: 1 }}>
              <Text style={styles.compareLabel}>{t('money.afford.without')}</Text>
              <Text style={styles.compareValue}>{days(answer.days_before)}</Text>
            </View>
            <Feather name="arrow-right" size={18} color={colors.textMuted} />
            <View style={{ flex: 1, alignItems: 'flex-end' }}>
              <Text style={styles.compareLabel}>{t('money.afford.with')}</Text>
              <Text style={[styles.compareValue, { color: look[answer.verdict].colour }]}>{days(answer.days_after)}</Text>
            </View>
          </View>
        </Card>
      ) : null}
      <Text style={styles.note}>{t('money.afford.private')}</Text>
    </Screen>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    card: { gap: space.md, padding: space.lg, borderWidth: 1.5 },
    verdict: { flexDirection: 'row', alignItems: 'center', gap: space.sm },
    word: { fontFamily: fonts.display, fontSize: 30, lineHeight: 36 },
    line: { fontFamily: fonts.body, ...type.body, color: colors.text },
    compare: { flexDirection: 'row', alignItems: 'center', gap: space.md, paddingTop: space.md, borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: colors.line },
    compareLabel: { fontFamily: fonts.medium, fontSize: 13, color: colors.textMuted },
    compareValue: { fontFamily: fonts.bold, fontSize: 20, lineHeight: 26, color: colors.ink },
    note: { fontFamily: fonts.medium, ...type.label, color: colors.textMuted },
  });
