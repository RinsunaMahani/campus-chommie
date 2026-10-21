import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { studentHeader } from '@/features/profile/components/HeaderTools';
import { useProfile } from '@/features/profile/state';
import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Card, InfoNote, ListRow, ToggleRow } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { Section } from '@/shared/components/Section';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Body, Overline, Strong } from '@/shared/components/Text';
import { MessageKey, t } from '@/shared/i18n';
import { formatRand } from '@/shared/lib/money';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius, space, type } from '@/shared/theme/tokens';

import { moneyApi } from '../api/moneyApi';
import { RunwayHero } from '../components/RunwayHero';
import { MoneyPlan, Summary, SummaryReady } from '../types';

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
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback((asLate: boolean) => {
    Promise.all([moneyApi.summary(asLate), moneyApi.plan()])
      .then(([s, p]) => {
        setSummary(s);
        setPlan(p);
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
          <RunwayHero summary={ready} />
          <Button title={t('money.afford.title')} variant="primary" icon="help-circle" onPress={() => router.push('/money/afford')} />

          <Card style={{ paddingVertical: space.xs }}>
            <Section
              first
              icon="calendar"
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
              title={t('money.goals.title')}
              summary={plan && plan.goals.length ? t('money.goals.summary', { n: plan.goals.length }) : t('money.goals.none')}>
              {plan?.goals.map((g) => (
                <Pressable key={g.id} accessibilityRole="button" onPress={() => router.push({ pathname: '/money/goal', params: { id: g.id } })} style={styles.goal}>
                  <View style={styles.goalHead}>
                    <Text style={[styles.potLabel, { flex: 1 }]}>{g.label}</Text>
                    <Text style={styles.potCents}>
                      {formatRand(g.saved_cents)} / {formatRand(g.amount_cents)}
                    </Text>
                  </View>
                  <View style={styles.track}>
                    <View style={[styles.fill, { width: `${Math.min(100, Math.round((g.saved_cents / g.amount_cents) * 100))}%` }]} />
                  </View>
                  <Text style={styles.potWhy}>{g.lines[0]}</Text>
                </Pressable>
              ))}
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
              <Button title={t('money.goals.add')} variant="secondary" icon="plus" compact onPress={() => router.push('/money/goal')} />
            </Section>

            <Section icon="shield" title={t('money.lifeFund')} summary={t(`money.lifeFund.${ready.life_fund.state}` as MessageKey)}>
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

      <Button title={t('money.logToday')} variant="secondary" icon="edit-3" onPress={() => router.push('/money/spending')} />

      <Card style={{ paddingVertical: 4 }}>
        <ListRow icon="sliders" title={t('money.settings')} subtitle={t('money.settingsSub')} onPress={() => router.push('/money/settings')} />
        <ListRow icon="download" title={t('money.income')} subtitle={t('money.incomeSub')} onPress={() => router.push('/money/income')} />
        <ListRow icon="calendar" title={t('money.payments')} subtitle={t('money.paymentsSub')} onPress={() => router.push('/money/payments')} />
        <ListRow icon="bar-chart-2" title={t('money.spending')} subtitle={t('money.spendingSub')} onPress={() => router.push('/money/spending')} />
        <ListRow icon="award" title={t('courseFinder.fundingTitle')} subtitle={t('courseFinder.fundingSub')} onPress={() => router.push('/course-finder/funding')} />
        <ListRow icon="map-pin" title={t('money.cheapThings')} subtitle={t('money.cheapThingsSub')} onPress={() => router.push('/money/cheap-things')} last />
      </Card>
    </Screen>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
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
