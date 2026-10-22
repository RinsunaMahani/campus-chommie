/**
 * The top of Money: how long the money lasts, in days first and big (research on "left to spend" apps: an exact
 * amount left nudges people to spend it, so days and a range come first and rands second), a bar from today to
 * the next payment with where the money runs out, and the balance and what's safe to spend under it.
 * Daylight paper: a hero area, so it sits on Rinsuna's wallpaper with white words (the forest palette inside),
 * a cream bar, and an amber "Runs short" pill when the money runs out before payday.
 */
import { StyleSheet, Text, View } from 'react-native';

import { Wallpaper } from '@/shared/components/Wallpaper';
import { t } from '@/shared/i18n';
import { formatRand } from '@/shared/lib/money';
import { forest, Palette, paper, PaletteProvider, useStyles } from '@/shared/theme/palette';
import { fonts, radius, space, type } from '@/shared/theme/tokens';

import { SummaryReady } from '../types';
import { formatDay } from '@/shared/lib/dates';

function daysBetween(from: string, to: string): number {
  return Math.round((Date.parse(`${to}T00:00:00Z`) - Date.parse(`${from}T00:00:00Z`)) / 86400000);
}

export function RunwayHero({ summary }: { summary: SummaryReady }) {
  return (
    <PaletteProvider palette={forest}>
      <Runway summary={summary} />
    </PaletteProvider>
  );
}

function Runway({ summary }: { summary: SummaryReady }) {
  const styles = useStyles(makeStyles);
  const r = summary.runway;
  const short = r.short_before_next;
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
    <View style={styles.card}>
      <Wallpaper />
      <View style={styles.labelRow}>
        <Text style={styles.label}>{t('money.hero.lasts')}</Text>
        {short ? (
          <View style={styles.pill}>
            <Text style={styles.pillText}>{t('home.shortBeforePay')}</Text>
          </View>
        ) : null}
      </View>
      <Text style={styles.big} accessibilityRole="header">
        {r.days == null ? t('money.hero.beyond') : t('money.hero.days', { n: r.days })}
      </Text>
      {range ? <Text style={styles.range}>{range}</Text> : null}
      {next ? (
        <View style={styles.barWrap} accessible accessibilityLabel={short ? t('money.hero.shortA11y') : t('money.hero.okA11y')}>
          <View style={styles.track}>
            <View style={[styles.fill, { width: `${Math.round(fill * 100)}%` }]} />
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
    </View>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    // The forest palette is in force here: words in onAccent (white), soft white boxes for the two amounts.
    card: {
      gap: space.sm,
      padding: space.lg,
      borderRadius: radius.lg,
      overflow: 'hidden',
      boxShadow: '0 6px 18px rgba(28, 43, 30, 0.08)',
    },
    labelRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: space.sm },
    label: { flex: 1, fontFamily: fonts.semibold, ...type.label, color: colors.onAccentSoft },
    // The pill keeps the paper's amber, which reads on the wallpaper too.
    pill: { paddingHorizontal: 10, paddingVertical: 3, borderRadius: radius.pill, backgroundColor: paper.marigoldTint },
    pillText: { fontFamily: fonts.bold, fontSize: 13, lineHeight: 18, color: paper.marigold },
    big: { fontFamily: fonts.display, fontSize: 44, lineHeight: 50, letterSpacing: -1, color: colors.onAccent, fontVariant: ['tabular-nums'] },
    range: { fontFamily: fonts.medium, ...type.callout, color: colors.onAccentSoft },
    barWrap: { gap: 6, marginTop: space.xs },
    track: { height: 10, borderRadius: radius.pill, backgroundColor: 'rgba(0, 0, 0, 0.28)', overflow: 'hidden' },
    fill: { height: 10, borderRadius: radius.pill, backgroundColor: paper.marigoldTint },
    barLabels: { flexDirection: 'row', justifyContent: 'space-between' },
    barText: { fontFamily: fonts.medium, fontSize: 13, color: colors.onAccentSoft },
    stats: { flexDirection: 'row', gap: space.sm, marginTop: space.sm },
    stat: {
      flex: 1,
      gap: 2,
      padding: space.md,
      borderRadius: radius.md,
      backgroundColor: colors.onAccentTint,
      borderWidth: 1,
      borderColor: 'rgba(255, 255, 255, 0.22)',
    },
    statValue: { fontFamily: fonts.display, fontSize: 22, lineHeight: 28, color: colors.onAccent, fontVariant: ['tabular-nums'] },
    statLabel: { fontFamily: fonts.medium, fontSize: 13, color: colors.onAccentSoft },
  });
