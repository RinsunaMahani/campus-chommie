import { Href, router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { studentHeader } from '@/features/profile/components/HeaderTools';
import { useProfile } from '@/features/profile/state';
import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Card, InfoNote, ListRow, Tag, ToggleRow } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { Section } from '@/shared/components/Section';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Body, Overline, Strong } from '@/shared/components/Text';
import { MessageKey, t } from '@/shared/i18n';
import { formatRand } from '@/shared/lib/money';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius, space, type } from '@/shared/theme/tokens';

import { moneyApi } from '../api/moneyApi';
import { MoneyHealthCard } from '../components/MoneyHealthCard';
import { RunwayHero } from '../components/RunwayHero';
import { CheckinStatus, FixedCost, MoneyHealth, MoneyPlan, Summary, SummaryReady } from '../types';

// The wallet's index route; the generated route types list it as /wallet/index.
const WALLET = '/wallet' as Href;

/**
 * The Money tab, number first (research: Copilot, Nubank, the "left to spend" study): how many days the money
 * lasts, big, with a bar to the next payday; then the one main action, "Can I afford this?"; then the rest in
 * sections that open on tap: the payday plan, goals and the university's fee dates, the life fund, planning for
 * a late payment, and how it's all worked out. It reloads whenever the tab comes back into view.
 */
export default function MoneyScreen() {
  const { mock } = useProfile();
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const [late, setLate] = useState(false);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [plan, setPlan] = useState<MoneyPlan | null>(null);
  const [checkin, setCheckin] = useState<CheckinStatus | null>(null);
  const [fixedCosts, setFixedCosts] = useState<FixedCost[]>([]);
  const [health, setHealth] = useState<MoneyHealth | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback((asLate: boolean) => {
    Promise.all([
      moneyApi.summary(asLate),
      moneyApi.plan(),
      moneyApi.checkinStatus().catch(() => null),
      moneyApi.fixedCosts().catch(() => []),
      moneyApi.health().catch(() => null),
    ])
      .then(([s, p, c, fcs, h]) => {
        setSummary(s);
        setPlan(p);
        if (c) setCheckin(c);
        if (fcs) setFixedCosts(fcs);
        if (h) setHealth(h);
        setError(null);
      })
      .catch((e) => setError(errorText(e, t('common.error'))))
      .finally(() => setRefreshing(false));
  }, []);

  useFocusEffect(
    useCallback(() => {
      if (!mock) load(late);
    }, [load, late, mock]),
  );

  if (mock) {
    return (
      <Screen tab title={t('money.title')}>
        <InfoNote icon="info">{t('money.mockNotice')}</InfoNote>
      </Screen>
    );
  }

  const ready: SummaryReady | null = summary && summary.ready ? summary : null;
  return (
    <Screen
      tab
      onRefresh={() => {
        setRefreshing(true);
        load(late);
      }}
      refreshing={refreshing}
      title={t('money.title')}
      {...studentHeader()}>
      {error ? <ErrorBox message={error} onRetry={() => load(late)} /> : null}
      {!error && !summary ? <Loading /> : null}
      {summary && !summary.ready ? (
        <Card style={{ gap: 10 }}>
          <Strong>{t('money.setupTitle')}</Strong>
          <Body>{t('money.setupIntro')}</Body>
          <Button title={t('money.settings')} variant="primary" onPress={() => router.push('/money/settings')} />
        </Card>
      ) : null}

      {ready ? (
        <>
          {checkin ? (
            <Pressable
              accessibilityRole="button"
              onPress={() => router.push('/money/checkin')}
              style={styles.checkinBanner}>
              <Text style={styles.checkinEmoji}>🔥</Text>
              <View style={{ flex: 1, gap: 2 }}>
                <Strong style={styles.checkinTitle}>{checkin.streak.line}</Strong>
                <Text style={styles.checkinSub}>
                  {checkin.checked_in_this_week
                    ? t('money.checkin.done')
                    : t('money.checkin.cardSub')}
                </Text>
              </View>
              <Button
                title={checkin.checked_in_this_week ? 'View' : t('money.checkin.submit')}
                variant={checkin.checked_in_this_week ? 'secondary' : 'primary'}
                compact
                onPress={() => router.push('/money/checkin')}
              />
            </Pressable>
          ) : null}

          <RunwayHero summary={ready} />
          <Button title={t('money.afford.title')} variant="primary" icon="help-circle" onPress={() => router.push('/money/afford')} />

          {health ? <MoneyHealthCard health={health} /> : null}

          <Card style={{ paddingVertical: space.xs }}>
            <Section
              first
              icon="calendar"
              tint={colors.accentDeep}
              tile={colors.accentTint}
              title={t('money.plan.title')}
              summary={plan?.payday ? t('money.plan.summary', { day: plan.payday.day, free: formatRand(plan.payday.free_cents) }) : t('money.plan.none')}>
              {plan?.payday ? (
                <>
                  {plan.payday.pots.map((pot) => (
                    <View key={pot.label} style={styles.pot}>
                      <View style={{ flex: 1, gap: 2 }}>
                        <Text style={styles.potLabel}>{pot.label}</Text>
                        <Text style={styles.potWhy}>{pot.why}</Text>
                      </View>
                      <Text style={styles.potCents}>{formatRand(pot.cents)}</Text>
                    </View>
                  ))}
                  <View style={styles.pot}>
                    <Text style={[styles.potLabel, { flex: 1, color: colors.accentDeep }]}>{t('money.plan.free')}</Text>
                    <Text style={[styles.potCents, { color: colors.accentDeep }]}>{formatRand(plan.payday.free_cents)}</Text>
                  </View>
                </>
              ) : null}
              {plan?.lines.map((line, i) => (
                <Body key={i}>{line}</Body>
              ))}
            </Section>

            <Section
              icon="target"
              tint={colors.classColours[2]}
              tile={`${colors.classColours[2]}1F`}
              title={t('money.pots.title')}
              summary={plan && plan.goals.length ? t('money.pots.summary', { n: plan.goals.length }) : t('money.pots.empty')}>
              {plan && plan.goals.length === 0 ? (
                <View style={{ gap: space.sm, paddingVertical: space.xs }}>
                  <Body style={{ color: colors.textMuted }}>{t('money.pots.empty')}</Body>
                  <Button title={t('money.pots.add')} variant="secondary" icon="plus" compact onPress={() => router.push('/money/goal')} />
                </View>
              ) : null}
              {plan?.goals.map((g) => {
                const kindBadge =
                  g.kind === 'family'
                    ? { label: 'Family', tone: 'info' as const }
                    : g.kind === 'stokvel'
                      ? { label: 'Stokvel', tone: 'jade' as const }
                      : g.kind === 'buffer'
                        ? { label: 'Buffer', tone: 'marigold' as const }
                        : g.kind === 'big_purchase'
                          ? { label: g.stokvel_funded ? 'Big purchase · stokvel' : 'Big purchase', tone: 'info' as const }
                          : { label: 'Goal', tone: 'muted' as const };
                const percent = Math.min(100, Math.round((g.saved_cents / Math.max(1, g.amount_cents)) * 100));
                return (
                  <Pressable key={g.id} accessibilityRole="button" onPress={() => router.push({ pathname: '/money/goal', params: { id: g.id } })} style={styles.goal}>
                    <View style={styles.goalHead}>
                      <View style={{ flex: 1, flexDirection: 'row', alignItems: 'center', gap: space.xs, flexWrap: 'wrap' }}>
                        <Text style={styles.potLabel}>{g.label}</Text>
                        <Tag label={kindBadge.label} tone={kindBadge.tone} />
                      </View>
                      <Text style={styles.potCents}>
                        {formatRand(g.saved_cents)} / {formatRand(g.amount_cents)}
                      </Text>
                    </View>
                    <View style={styles.track}>
                      <View style={[styles.fill, { width: `${percent}%` }]} />
                    </View>
                    <Text style={styles.potWhy}>{g.lines[0]}</Text>
                  </Pressable>
                );
              })}
              {plan && plan.goals.length > 0 ? (
                <Button title={t('money.pots.add')} variant="secondary" icon="plus" compact onPress={() => router.push('/money/goal')} />
              ) : null}
              {plan?.university_dates.length ? <Overline>{t('money.goals.fromUniversity')}</Overline> : null}
              {plan?.university_dates.map((d) => (
                <View key={`${d.name}${d.on}`} style={styles.pot}>
                  <View style={{ flex: 1, gap: 2 }}>
                    <Text style={styles.potLabel}>{d.name}</Text>
                    <Text style={styles.potWhy}>{d.day}</Text>
                  </View>
                  <Pressable
                    accessibilityRole="button"
                    accessibilityLabel={t('money.goals.planFor', { name: d.name })}
                    onPress={() => router.push({ pathname: '/money/goal', params: { label: d.name, due: d.on, uni: '1' } })}
                    hitSlop={8}>
                    <Text style={styles.link}>{t('money.goals.plan')}</Text>
                  </Pressable>
                </View>
              ))}
            </Section>

            <Section
              icon="file-text"
              tint={colors.classColours[1]}
              tile={`${colors.classColours[1]}1F`}
              title={t('money.fixedCosts.title')}
              summary={
                fixedCosts.length
                  ? t('money.fixedCosts.summary', { n: fixedCosts.length })
                  : t('money.fixedCosts.empty')
              }>
              {fixedCosts.length === 0 ? (
                <View style={{ gap: space.sm, paddingVertical: space.xs }}>
                  <Body style={{ color: colors.textMuted }}>{t('money.fixedCosts.empty')}</Body>
                  <Button
                    title={t('money.fixedCosts.add')}
                    variant="secondary"
                    icon="plus"
                    compact
                    onPress={() => router.push('/money/fixed-cost')}
                  />
                </View>
              ) : null}
              {fixedCosts.map((c) => (
                <Pressable
                  key={c.id}
                  accessibilityRole="button"
                  onPress={() => router.push({ pathname: '/money/fixed-cost', params: { id: c.id } })}
                  style={styles.pot}>
                  <View style={{ flex: 1, gap: 2 }}>
                    <Text style={styles.potLabel}>{c.label}</Text>
                    <Text style={styles.potWhy}>{`Day ${c.day_of_month} of each month`}</Text>
                  </View>
                  <Text style={styles.potCents}>{formatRand(c.amount_cents)}</Text>
                </Pressable>
              ))}
              {fixedCosts.length > 0 ? (
                <Button
                  title={t('money.fixedCosts.add')}
                  variant="secondary"
                  icon="plus"
                  compact
                  onPress={() => router.push('/money/fixed-cost')}
                />
              ) : null}
            </Section>

            <Section
              icon="shield"
              tint={colors.marigold}
              tile={colors.marigoldTint}
              title={t('money.lifeFund')}
              summary={t('money.lifeFund.sub')}
              aside={
                <Tag
                  label={t(`money.lifeFund.${ready.life_fund.state}` as MessageKey)}
                  tone={ready.life_fund.state === 'green' ? 'jade' : 'marigold'}
                />
              }>
              <Body>{ready.life_fund.reason}</Body>
              {ready.life_fund.resume_hint ? <Body>{ready.life_fund.resume_hint}</Body> : null}
              {ready.this_week ? <Body>{`${t('money.thisWeek')}: ${ready.this_week.reason}`}</Body> : null}
            </Section>

            {ready.next_payment ? (
              <Section icon="clock" title={t('money.late')} summary={late ? t('money.lateOn') : t('money.lateHint', { n: ready.late_days })} defaultOpen={late}>
                <ToggleRow icon="clock" title={t('money.late')} subtitle={t('money.lateHint', { n: ready.late_days })} value={late} onChange={setLate} />
              </Section>
            ) : null}

            <Section icon="info" title={t('money.how.title')} summary={t('money.how.summary')}>
              {[...ready.runway.lines, ...(ready.pace?.lines ?? []), ...ready.safe_to_spend.lines, ...ready.balance.lines, ...ready.notes].map((line, i) => (
                <Body key={i}>{line}</Body>
              ))}
            </Section>
          </Card>
        </>
      ) : null}

      <Button title={t('money.logToday')} variant="soft" icon="edit-3" onPress={() => router.push('/money/spending')} />

      <Card style={{ paddingVertical: 4 }}>
        <ListRow tone="mint" icon="check-square" title={t('money.checkin.title')} subtitle={checkin ? checkin.streak.line : t('money.checkin.cardSub')} onPress={() => router.push('/money/checkin')} />
        <ListRow tone="mint" icon="repeat" title={t('money.fixedCosts.title')} subtitle={t('money.fixedCosts.summary', { n: fixedCosts.length })} onPress={() => router.push('/money/fixed-cost')} />
        <ListRow tone="mint" icon="sliders" title={t('money.settings')} subtitle={t('money.settingsSub')} onPress={() => router.push('/money/settings')} />
        <ListRow tone="mint" icon="download" title={t('money.income')} subtitle={t('money.incomeSub')} onPress={() => router.push('/money/income')} />
        <ListRow tone="mint" icon="calendar" title={t('money.payments')} subtitle={t('money.paymentsSub')} onPress={() => router.push('/money/payments')} />
        <ListRow tone="mint" icon="bar-chart-2" title={t('money.spending')} subtitle={t('money.spendingSub')} onPress={() => router.push('/money/spending')} />
        <ListRow tone="mint" icon="award" title={t('courseFinder.fundingTitle')} subtitle={t('courseFinder.fundingSub')} onPress={() => router.push('/course-finder/funding')} />
        <ListRow tone="mint" icon="credit-card" title={t('wallet.title')} subtitle={t('wallet.entrySub')} onPress={() => router.push(WALLET)} />
        <ListRow tone="mint" icon="map-pin" title={t('money.cheapThings')} subtitle={t('money.cheapThingsSub')} onPress={() => router.push('/money/cheap-things')} last />
      </Card>
    </Screen>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    checkinBanner: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: space.md,
      backgroundColor: colors.white,
      borderRadius: radius.lg,
      borderWidth: 1,
      borderColor: colors.line,
      padding: space.md,
    },
    checkinEmoji: {
      fontSize: 24,
    },
    checkinTitle: {
      ...type.callout,
      color: colors.ink,
    },
    checkinSub: {
      fontFamily: fonts.body,
      fontSize: 13,
      lineHeight: 18,
      color: colors.textMuted,
    },
    pot: { flexDirection: 'row', alignItems: 'center', gap: space.md, paddingVertical: space.xs },
    potLabel: { fontFamily: fonts.bold, ...type.callout, color: colors.ink },
    potWhy: { fontFamily: fonts.medium, fontSize: 13, lineHeight: 18, color: colors.textMuted },
    potCents: { fontFamily: fonts.bold, fontSize: 16, color: colors.ink, fontVariant: ['tabular-nums'] },
    goal: { gap: 6, paddingVertical: space.xs },
    goalHead: { flexDirection: 'row', alignItems: 'center', gap: space.sm },
    track: { height: 8, borderRadius: radius.pill, backgroundColor: colors.iconTile, overflow: 'hidden' },
    fill: { height: 8, borderRadius: radius.pill, backgroundColor: colors.accentDeep },
    link: { fontFamily: fonts.bold, fontSize: 15, color: colors.accentDeep },
  });
