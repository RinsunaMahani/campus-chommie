/**
 * How to apply, on today's date: each intake's window in words, the funding
 * a choice opens, and each university's and funder's own steps. A fact the
 * server doesn't have arrives as null with a "not verified yet" line, and
 * that line is shown: never a blank.
 */
import * as WebBrowser from 'expo-web-browser';
import { ComponentProps } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { Button } from '@/shared/components/Button';
import { Card, Tag } from '@/shared/components/Parts';
import { Body, Muted, Overline, Strong } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { formatRand } from '@/shared/lib/money';
import { colors, fonts } from '@/shared/theme/tokens';

import { ApplyWindow, Deadline, Group, Guide, PlanApply, SlotFunding, WindowStatus } from '../types';
import { daysLeft, formatDay } from '../words';
import { SourceLink } from './SourceLink';

type Tone = NonNullable<ComponentProps<typeof Tag>['tone']>;

const WINDOW_TONE: Record<WindowStatus, Tone> = {
  open: 'jade',
  closing_soon: 'marigold',
  late_open: 'marigold',
  check: 'info',
  opens_later: 'info',
  late_ahead: 'info',
  closed: 'muted',
  not_published: 'muted',
};

const OPEN_NOW: WindowStatus[] = ['open', 'closing_soon', 'late_open'];

function Lines({ lines }: { lines: string[] }) {
  return (
    <>
      {lines.map((line, i) => (
        <Text key={i} style={styles.line}>
          {line}
        </Text>
      ))}
    </>
  );
}

/** Each intake: "To start in 2027", its status in words, and its dates. */
export function ApplyWindows({ windows }: { windows: ApplyWindow[] }) {
  return (
    <View style={{ gap: 12 }}>
      {windows.map((w) => (
        <View key={`${w.intake}-${w.heading}`} style={{ gap: 4 }}>
          <View style={styles.headRow}>
            <Strong style={{ flexShrink: 1 }}>{w.heading}</Strong>
            <Tag label={w.label} tone={WINDOW_TONE[w.status] ?? 'info'} />
          </View>
          {w.days != null && OPEN_NOW.includes(w.status) ? <Text style={styles.countdown}>{daysLeft(w.days)}</Text> : null}
          <Lines lines={w.lines} />
          {w.source_url ? <SourceLink url={w.source_url} /> : null}
        </View>
      ))}
    </View>
  );
}

/** Funders whose fields match this choice: how many, how many open now, and the first few. */
export function SlotFundingBox({ funding }: { funding: SlotFunding }) {
  return (
    <View style={{ gap: 8 }}>
      <Overline>{t('courseFinder.fundingForChoice')}</Overline>
      <Lines lines={funding.lines} />
      {funding.funders.map((f) => (
        <View key={f.id} style={styles.funder}>
          <View style={styles.headRow}>
            <Text style={styles.funderName}>{f.name}</Text>
          </View>
          <Tag label={f.label} tone={f.status === 'open' ? 'jade' : f.status === 'closing_soon' ? 'marigold' : 'info'} />
          {f.lines[0] ? <Muted>{f.lines[0]}</Muted> : null}
        </View>
      ))}
    </View>
  );
}

function GroupBlock({ title, group }: { title: string; group: Group }) {
  if (!group || !group.items.length) return null;
  return (
    <View style={{ gap: 4 }}>
      <Overline>{title}</Overline>
      {group.items.map((item, i) => (
        <View key={i} style={styles.item}>
          <Text style={styles.bullet}>•</Text>
          <Text style={styles.itemText}>{item}</Text>
        </View>
      ))}
    </View>
  );
}

/** One university's or funder's own steps: fee, documents, what happens next, its page. */
export function GuideCard({ guide }: { guide: Guide }) {
  const url = guide.url;
  return (
    <Card style={{ gap: 12 }}>
      <Strong>{guide.name}</Strong>
      {guide.how ? <Body>{guide.how}</Body> : null}
      <Lines lines={guide.lines} />
      {guide.kind === 'funder' && guide.windows.length ? <ApplyWindows windows={guide.windows} /> : null}
      {guide.fee_cents != null ? (
        <View style={{ gap: 2 }}>
          <Overline>{t('courseFinder.fee')}</Overline>
          <Strong>{guide.fee_cents === 0 ? t('courseFinder.noFee') : formatRand(guide.fee_cents)}</Strong>
          {guide.fee_note ? <Muted>{guide.fee_note}</Muted> : null}
        </View>
      ) : null}
      <GroupBlock title={t('courseFinder.applyWho')} group={guide.who_can_apply} />
      <GroupBlock title={t('courseFinder.applyDocuments')} group={guide.documents} />
      <GroupBlock title={t('courseFinder.applyTips')} group={guide.tips} />
      <GroupBlock title={t('courseFinder.warnings')} group={guide.warnings} />
      {guide.after.length ? (
        <View style={{ gap: 4 }}>
          <Overline>{t('courseFinder.applyAfter')}</Overline>
          {guide.after.map((a, i) => (
            <Text key={i} style={styles.line}>
              {a.text}
            </Text>
          ))}
        </View>
      ) : null}
      {guide.contact ? <Muted>{guide.contact}</Muted> : null}
      {url ? <Button title={t('courseFinder.applyOpen')} variant="secondary" icon="external-link" onPress={() => WebBrowser.openBrowserAsync(url)} /> : null}
      <SourceLink url={guide.source_url} />
      {!guide.confirmed && guide.notice ? <Muted>{guide.notice}</Muted> : null}
    </Card>
  );
}

function DeadlineRow({ d }: { d: Deadline }) {
  return (
    <View style={styles.deadline}>
      <View style={styles.headRow}>
        <Strong style={{ flexShrink: 1 }}>{formatDay(d.date)}</Strong>
        <Tag label={daysLeft(d.days)} tone={d.days <= 7 ? 'marigold' : 'info'} />
      </View>
      <Text style={styles.line}>{d.text}</Text>
      <SourceLink url={d.source_url} />
    </View>
  );
}

/** The plan's "how to apply": every date still ahead, then each university's and funder's steps. */
export function ApplyGuide({ apply }: { apply: PlanApply }) {
  return (
    <View style={{ gap: 12 }}>
      <Card style={{ gap: 12 }}>
        <Overline>{t('courseFinder.applyDates')}</Overline>
        {apply.deadlines.length ? apply.deadlines.map((d, i) => <DeadlineRow key={`${d.date}-${i}`} d={d} />) : <Body>{t('courseFinder.applyNoDates')}</Body>}
      </Card>
      {apply.universities.map((g) => (
        <GuideCard key={`u-${g.id}`} guide={g} />
      ))}
      {apply.funding.length ? <Overline>{t('courseFinder.applyFunding')}</Overline> : null}
      {apply.funding.map((g) => (
        <GuideCard key={`f-${g.id}`} guide={g} />
      ))}
      {apply.notes.length ? (
        <View style={{ gap: 4 }}>
          <Overline>{t('courseFinder.goodToKnow')}</Overline>
          <Lines lines={apply.notes} />
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  headRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 8, flexWrap: 'wrap' },
  line: { fontFamily: fonts.body, fontSize: 13.5, lineHeight: 20, color: colors.text },
  countdown: { fontFamily: fonts.bold, fontSize: 12.5, color: colors.marigoldDeep },
  funder: { gap: 4, paddingTop: 8, borderTopWidth: 1, borderTopColor: colors.line },
  funderName: { flex: 1, fontFamily: fonts.semibold, fontSize: 14, color: colors.text },
  item: { flexDirection: 'row', gap: 8 },
  bullet: { fontFamily: fonts.bold, fontSize: 14, lineHeight: 20, color: colors.textFaint },
  itemText: { flex: 1, fontFamily: fonts.body, fontSize: 13.5, lineHeight: 20, color: colors.text },
  deadline: { gap: 4, paddingTop: 10, borderTopWidth: 1, borderTopColor: colors.line },
});
