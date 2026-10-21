/**
 * The cards of the Money tab. Each shows the server's own plain-words lines;
 * the app adds only the big number, the state in words, and colour that never
 * stands alone.
 */
import { Feather } from '@expo/vector-icons';
import { ComponentProps } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { Card, ToggleRow } from '@/shared/components/Parts';
import { Money, Muted, Overline, Strong } from '@/shared/components/Text';
import { MessageKey, t } from '@/shared/i18n';
import { formatDay } from '@/shared/lib/dates';
import { formatRand } from '@/shared/lib/money';
import { fonts, radius } from '@/shared/theme/tokens';

import { LifeFundState, SummaryReady } from '../types';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';

type IconName = ComponentProps<typeof Feather>['name'];

function Lines({ lines, muted }: { lines: string[]; muted?: boolean }) {
  const styles = useStyles(makeStyles);
  return (
    <>
      {lines.map((line, i) => (
        <Text key={i} style={[styles.line, muted && styles.muted]}>
          {line}
        </Text>
      ))}
    </>
  );
}

/** The balance now and how long it lasts. A runway that ends before the next payment is marked in words and colour. */
export function RunwayCard({ summary }: { summary: SummaryReady }) {
  const styles = useStyles(makeStyles);
  const { balance, runway, pace } = summary;
  const short = runway.short_before_next;
  return (
    <Card style={{ gap: 12, ...(short ? styles.warn : {}) }}>
      <View style={{ gap: 2 }}>
        <Overline>{t('money.balanceNow')}</Overline>
        <Money>{formatRand(balance.cents)}</Money>
        <Lines lines={balance.lines} muted />
      </View>
      <View style={styles.rule} />
      <View style={{ gap: 4 }}>
        <Overline>{t('money.runway')}</Overline>
        <Lines lines={runway.lines} />
        {pace ? <Lines lines={pace.lines} muted /> : null}
      </View>
    </Card>
  );
}

/** What can go on extras each day, after essentials and the life-fund reserve. */
export function SafeToSpendCard({ summary }: { summary: SummaryReady }) {
  const styles = useStyles(makeStyles);
  const safe = summary.safe_to_spend;
  return (
    <Card style={{ gap: 6 }}>
      <Overline>{t('money.safeToSpend')}</Overline>
      <Strong style={styles.big}>{t('money.perDay', { amount: formatRand(safe.per_day_cents) })}</Strong>
      <Lines lines={safe.lines} />
    </Card>
  );
}

const fundLook = (colors: Palette): Record<LifeFundState, { icon: IconName; bg: string; fg: string }> => ({
  green: { icon: 'sun', bg: colors.jadeTint, fg: colors.jade },
  amber: { icon: 'alert-triangle', bg: colors.marigoldTint, fg: colors.marigoldDeep },
  paused: { icon: 'pause-circle', bg: colors.garnetTint, fg: colors.garnet },
});

/** The life fund's state in words (green to go out, amber to go easy, paused), with why and when it comes back. */
export function LifeFundCard({ summary }: { summary: SummaryReady }) {
  const styles = useStyles(makeStyles);
  const fund = summary.life_fund;
  const looks = fundLook(usePalette());
  const look = looks[fund.state] ?? looks.amber;
  return (
    <Card style={{ gap: 8 }}>
      <Overline>{t('money.lifeFund')}</Overline>
      <View style={[styles.badge, { backgroundColor: look.bg }]}>
        <Feather name={look.icon} size={14} color={look.fg} />
        <Text style={[styles.badgeText, { color: look.fg }]}>{t(`money.lifeFund.${fund.state}` as MessageKey)}</Text>
      </View>
      <Text style={styles.line}>{fund.reason}</Text>
      {fund.resume_hint ? <Muted>{fund.resume_hint}</Muted> : null}
      {summary.this_week ? <Muted>{`${t('money.thisWeek')}: ${summary.this_week.reason}`}</Muted> : null}
    </Card>
  );
}

/** The next payment, and planning for it to arrive two weeks late. */
export function NextPaymentCard({
  summary,
  onLate,
}: {
  summary: SummaryReady;
  onLate: (late: boolean) => void;
}) {
  const styles = useStyles(makeStyles);
  const next = summary.next_payment;
  return (
    <Card style={{ gap: 10 }}>
      <Overline>{t('money.nextPayment')}</Overline>
      {next ? (
        <View style={{ gap: 2 }}>
          <Strong>{next.label}</Strong>
          <Text style={styles.amount}>{formatRand(next.amount_cents)}</Text>
          <Muted>{t('money.landsOn', { date: formatDay(next.lands_on ?? next.expected_on) })}</Muted>
        </View>
      ) : (
        <Muted>{t('money.paymentsEmpty')}</Muted>
      )}
      {next ? (
        <ToggleRow
          icon="clock"
          title={t('money.late')}
          subtitle={t('money.lateHint', { n: summary.late_days })}
          value={summary.late}
          onChange={onLate}
        />
      ) : null}
    </Card>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  warn: { borderColor: colors.marigold, backgroundColor: colors.marigoldTint },
  rule: { height: 1, backgroundColor: colors.line },
  line: { fontFamily: fonts.body, fontSize: 14, lineHeight: 21, color: colors.text },
  muted: { fontSize: 12.5, lineHeight: 18, color: colors.textMuted },
  big: { fontFamily: fonts.display, fontSize: 22, lineHeight: 28 },
  amount: { fontFamily: fonts.display, fontSize: 20, color: colors.ink },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    alignSelf: 'flex-start',
    borderRadius: radius.pill,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  badgeText: { fontFamily: fonts.bold, fontSize: 12.5 },
});
