/**
 * Weekly Money Check-in Screen.
 * 1-minute check-in: enter this week's total spending or skip.
 * Tracks consecutive weekly streak with positive, welcoming tone.
 */
import { router } from 'expo-router';
import { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Card, IconTile, InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Body, Strong, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { formatDay } from '@/shared/lib/dates';
import { centsToInput, formatRand, parseRand } from '@/shared/lib/money';
import { Palette, useStyles } from '@/shared/theme/palette';
import { fonts, space, type } from '@/shared/theme/tokens';

import { moneyApi } from '../api/moneyApi';
import { AmountField } from '../components/AmountField';
import { CheckinStatus } from '../types';

export default function WeeklyCheckinScreen() {
  const styles = useStyles(makeStyles);
  const [status, setStatus] = useState<CheckinStatus | null>(null);
  const [amount, setAmount] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [failure, setFailure] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    moneyApi
      .checkinStatus()
      .then((st) => {
        setStatus(st);
        if (st.this_week && st.this_week.amount_cents != null) {
          setAmount(centsToInput(st.this_week.amount_cents));
        }
      })
      .catch((e) => setFailure(errorText(e, t('common.error'))));
  }, []);

  async function handleCheckin() {
    const cents = parseRand(amount);
    if (cents === null || cents < 0) {
      setError(t('money.amountInvalid'));
      return;
    }
    setBusy(true);
    setFailure(null);
    try {
      await moneyApi.submitCheckin({ amount_cents: cents, skipped: FalseSafe(false) });
      router.back();
    } catch (e) {
      setFailure(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  async function handleSkip() {
    setBusy(true);
    setFailure(null);
    try {
      await moneyApi.submitCheckin({ skipped: true });
      router.back();
    } catch (e) {
      setFailure(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  function FalseSafe(val: boolean) {
    return val;
  }

  return (
    <Screen
      back
      footer={
        <View style={{ gap: 8 }}>
          <Button
            title={t('money.checkin.submit')}
            variant="accent"
            onPress={handleCheckin}
            loading={busy}
            disabled={status === null}
          />
          <Button
            title={t('money.checkin.skip')}
            variant="secondary"
            onPress={handleSkip}
            disabled={busy || status === null}
          />
        </View>
      }>
      <Title>{t('money.checkin.title')}</Title>
      {status === null && !failure ? <Loading /> : null}
      {failure ? <ErrorBox message={failure} /> : null}

      {status ? (
        <View style={{ gap: 14 }}>
          <Card style={styles.streakCard}>
            <IconTile name="trending-up" size={44} />
            <View style={{ flex: 1, gap: 2 }}>
              <Strong style={styles.streakTitle}>{status.streak.line}</Strong>
              <Text style={styles.streakSub}>{t('money.checkin.cardSub')}</Text>
            </View>
          </Card>

          {status.checked_in_this_week && status.this_week ? (
            <InfoNote icon="check-circle">
              {status.this_week.skipped
                ? t('money.checkin.done') + ' (Skipped)'
                : t('money.checkin.done') + ` (${formatRand(status.this_week.amount_cents ?? 0)})`}
            </InfoNote>
          ) : null}

          <Card style={{ gap: 10 }}>
            <Body style={styles.windowNotice}>
              {t('money.checkin.amountHint', {
                start: formatDay(status.week_start),
                end: formatDay(status.week_end),
              })}
            </Body>
            <AmountField
              label={t('money.checkin.amount')}
              value={amount}
              onChange={(v) => {
                setAmount(v);
                setError(null);
              }}
              error={error ?? undefined}
            />
          </Card>
        </View>
      ) : null}

      <InfoNote icon="lock">{t('onboarding.privacyNever')}</InfoNote>
    </Screen>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    streakCard: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: space.md,
      backgroundColor: colors.accentTint,
      borderColor: colors.accentDeep,
    },
    streakTitle: {
      ...type.callout,
      color: colors.ink,
    },
    streakSub: {
      fontFamily: fonts.body,
      fontSize: 13,
      lineHeight: 18,
      color: colors.textMuted,
    },
    windowNotice: {
      color: colors.textMuted,
      fontSize: 14,
    },
  });
