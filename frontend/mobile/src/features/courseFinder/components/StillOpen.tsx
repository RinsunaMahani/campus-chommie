/**
 * The top of the plan: what a learner can still do today, built only from
 * the dates the plan carries. Applications and funding open now, those whose
 * dates the learner should check, what opens next, what isn't published yet
 * and what has closed, for every choice and national funder in the plan.
 * Choices with the same dates share a line.
 */
import { ComponentProps } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { Card, InfoNote, Tag } from '@/shared/components/Parts';
import { Overline, Strong } from '@/shared/components/Text';
import { MessageKey, t } from '@/shared/i18n';
import { colors, fonts } from '@/shared/theme/tokens';

import { ApplyWindow, Plan, PlanApply, Slot, WindowStatus } from '../types';
import { daysLeft, formatDay, inDays } from '../words';

type SectionId = 'now' | 'check' | 'next' | 'unpublished' | 'closed';
type Row = { key: string; who: string[]; detail: string; next: string | null };
export type Section = { id: SectionId; title: string; rows: { key: string; who: string; detail: string }[] };

const SECTION_OF: Record<WindowStatus, SectionId> = {
  open: 'now',
  closing_soon: 'now',
  late_open: 'now',
  // Not known to be open: the opening date isn't verified, or it may already have closed.
  check: 'check',
  opens_later: 'next',
  late_ahead: 'next',
  not_published: 'unpublished',
  closed: 'closed',
};

const TITLES: Record<SectionId, MessageKey> = {
  now: 'courseFinder.stillNow',
  check: 'courseFinder.stillCheckTitle',
  next: 'courseFinder.stillNext',
  unpublished: 'courseFinder.stillUnpublished',
  closed: 'courseFinder.stillClosed',
};

const TONES: Record<SectionId, ComponentProps<typeof Tag>['tone']> = { now: 'jade', check: 'info', next: 'info', unpublished: 'muted', closed: 'muted' };

/** "To start in 2027 · closes Fri 31 Jul 2026 · 18 days left": the window's heading, its next dates and a count. */
function detail(w: ApplyWindow): string {
  const parts = [w.heading];
  if (w.status === 'open' || w.status === 'closing_soon') {
    if (w.closes) parts.push(t('courseFinder.stillCloses', { date: formatDay(w.closes) }));
    // A programme that closes on one of several published dates may close on the earliest.
    else if (w.closes_one_of.length) parts.push(t('courseFinder.stillClosesBy', { date: formatDay([...w.closes_one_of].sort()[0]) }));
    if (w.days != null) parts.push(daysLeft(w.days));
  } else if (w.status === 'late_open' && w.late_closes) {
    parts.push(t('courseFinder.stillLateCloses', { date: formatDay(w.late_closes) }));
    if (w.days != null) parts.push(daysLeft(w.days));
  } else if (w.status === 'check') {
    // Why it needs checking is in the choice's own lines.
    if (w.closes) parts.push(t('courseFinder.stillCloses', { date: formatDay(w.closes) }));
    parts.push(t('courseFinder.stillCheck'));
  } else if (w.status === 'late_ahead' && w.late_opens && w.late_closes) {
    parts.push(t('courseFinder.stillLate', { from: formatDay(w.late_opens), to: formatDay(w.late_closes) }));
    if (w.days != null) parts.push(inDays(w.days));
  } else if (w.status === 'opens_later' && w.opens) {
    parts.push(t('courseFinder.stillOpens', { date: formatDay(w.opens) }));
    if (w.days != null) parts.push(inDays(w.days));
  }
  return parts.join(' · ');
}

/** The plan's windows sorted into what's open now, to check, coming up, not published and closed. */
export function stillOpen(plan: Plan): Section[] {
  const slots = [plan.goal, plan.bridge, plan.safe, ...plan.other_routes].filter((s): s is Slot => !!s);
  const found: { who: string; window: ApplyWindow }[] = [
    ...plan.apply.funding.flatMap((g) => g.windows.map((window) => ({ who: g.name, window }))),
    ...slots.flatMap((s) => s.apply.map((window) => ({ who: s.match.university_name, window }))),
  ];
  const rows = new Map<string, Row & { section: SectionId }>();
  for (const { who, window } of found) {
    const section = SECTION_OF[window.status];
    const text = detail(window);
    const key = `${section}|${text}`;
    const row = rows.get(key) ?? { key, section, who: [], detail: text, next: window.next_date };
    if (!row.who.includes(who)) row.who.push(who);
    if (window.next_date && (!row.next || window.next_date < row.next)) row.next = window.next_date;
    rows.set(key, row);
  }
  const all = [...rows.values()];
  return (['now', 'check', 'next', 'unpublished', 'closed'] as SectionId[])
    .map((id) => ({
      id,
      title: t(TITLES[id]),
      rows: all
        .filter((r) => r.section === id)
        // Soonest first; rows without a date keep the plan's order after them.
        .sort((a, b) => (a.next ?? '9999').localeCompare(b.next ?? '9999'))
        .map((r) => ({ key: r.key, who: r.who.join(', '), detail: r.detail })),
    }))
    .filter((s) => s.rows.length);
}

export function StillOpen({ plan }: { plan: Plan }) {
  const sections = stillOpen(plan);
  if (!sections.length) return null;
  return (
    <Card style={{ gap: 12 }}>
      <Overline>{t('courseFinder.stillTitle')}</Overline>
      {sections.map((s) => (
        <View key={s.id} style={{ gap: 8 }}>
          <Tag label={s.title} tone={TONES[s.id]} />
          {s.rows.map((r) => (
            <View key={r.key} style={{ gap: 2 }}>
              <Strong>{r.who}</Strong>
              <Text style={styles.detail}>{r.detail}</Text>
            </View>
          ))}
        </View>
      ))}
    </Card>
  );
}

/** Said whenever the plan's dates come from a preview's test date rather than today. */
export function TestDateNote({ apply }: { apply: PlanApply }) {
  if (!apply.test_date) return null;
  return <InfoNote icon="clock">{t('courseFinder.testDate', { date: formatDay(apply.today) })}</InfoNote>;
}

const styles = StyleSheet.create({
  detail: { fontFamily: fonts.body, fontSize: 13.5, lineHeight: 20, color: colors.textMuted },
});
