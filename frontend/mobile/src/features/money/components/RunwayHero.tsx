/**
 * The top of Money: how long the money lasts, in days first and big (research on "left to spend" apps: an exact
 * amount left nudges people to spend it, so days and a range come first and rands second), a bar from today to
 * the next payment with where the money runs out, and the balance and what's safe to spend under it.
 */
import { StyleSheet, Text, View } from 'react-native';

import { Card } from '@/shared/components/Parts';
import { t } from '@/shared/i18n';
import { formatRand } from '@/shared/lib/money';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius, space, type } from '@/shared/theme/tokens';

import { SummaryReady } from '../types';
import { formatDay } from '@/shared/lib/dates';

function daysBetween(from: string, to: string): number {
  return Math.round((Date.parse(`${to}T00:00:00Z`) - Date.parse(`${from}T00:00:00Z`)) / 86400000);
}

export function RunwayHero({ summary }: { summary: SummaryReady }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const r = summary.runway;
  const short = r.short_before_next;
  const tint = short ? colors.marigold : colors.accentDeep;
  const next = summary.next_payment;
  const toPay = next ? Math.max(1, daysBetween(summary.today, next.lands_on ?? next.expected_on)) : null;
  // The bar runs from today to the next payment; the money's part fills it, or all of it when it lasts.
  const fill = toPay == null ? 1 : r.days == null ? 1 : Math.min(1, r.days / toPay);
  const range =
    r.earliest_on && r.latest_on && r.earliest_on !== r.latest_on
      ? t('money.hero.range', { from: formatDay(r.earliest_on), to: formatDay(r.latest_on) })
      : r.runs_out_on
        ? t('money.hero.until', { date: formatDay(r.runs_out_on) })
        : null;
  return (
    <Card style={short ? { ...styles.card, borderColor: colors.marigold } : styles.card}>
      <Text style={styles.label}>{t('money.hero.lasts')}</Text>
      <Text style={[styles.big, { color: tint }]} accessibilityRole="header">
        {r.days == null ? t('money.hero.beyond') : t('money.hero.days', { n: r.days })}
      </Text>
      {range ? <Text style={styles.range}>{range}</Text> : null}
      {next ? (
        <View style={styles.barWrap} accessible accessibilityLabel={short ? t('money.hero.shortA11y') : t('money.hero.okA11y')}>
          <View style={styles.track}>
            <View style={[styles.fill, { width: `${Math.round(fill * 100)}%`, backgroundColor: tint }]} />
          </View>
          <View style={styles.barLabels}>
            <Text style={styles.barText}>{t('money.hero.today')}</Text>
            <Text style={styles.barText}>{t('money.hero.payday', { date: formatDay(next.lands_on ?? next.expected_on) })}</Text>
          </View>
        </View>
      ) : null}
      <View style={styles.stats}>
        <View style={styles.stat}>
          <Text style={styles.statValue}>{formatRand(summary.safe_to_spend.per_day_cents)}</Text>
          <Text style={styles.statLabel}>{t('money.hero.safe')}</Text>
        </View>
        <View style={styles.stat}>
          <Text style={styles.statValue}>{formatRand(summary.balance.cents)}</Text>
          <Text style={styles.statLabel}>{t('money.hero.balance')}</Text>
        </View>
      </View>
    </Card>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    card: { gap: space.sm, padding: space.lg },
    label: { fontFamily: fonts.semibold, ...type.label, color: colors.textMuted },
    big: { fontFamily: fonts.display, fontSize: 44, lineHeight: 50, letterSpacing: -1, fontVariant: ['tabular-nums'] },
    range: { fontFamily: fonts.medium, ...type.callout, color: colors.text },
    barWrap: { gap: 6, marginTop: space.xs },
    track: { height: 10, borderRadius: radius.pill, backgroundColor: colors.iconTile, overflow: 'hidden' },
    fill: { height: 10, borderRadius: radius.pill },
    barLabels: { flexDirection: 'row', justifyContent: 'space-between' },
    barText: { fontFamily: fonts.medium, fontSize: 13, color: colors.textMuted },
    stats: { flexDirection: 'row', gap: space.md, marginTop: space.sm, paddingTop: space.md, borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: colors.line },
    stat: { flex: 1, gap: 2 },
    statValue: { fontFamily: fonts.bold, fontSize: 20, lineHeight: 26, color: colors.ink, fontVariant: ['tabular-nums'] },
    statLabel: { fontFamily: fonts.medium, fontSize: 13, color: colors.textMuted },
  });
