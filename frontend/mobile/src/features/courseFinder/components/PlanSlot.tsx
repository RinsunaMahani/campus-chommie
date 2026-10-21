/**
 * One choice in the three-choice plan: the programme as the learner matches
 * it, the slot's lines (for a route into the goal they start with its
 * guarantee, conditions, places and added years; campus_engine/bridges.py),
 * how to apply for it on today's date, and the funding its fields point to.
 */
import { View } from 'react-native';

import { Card } from '@/shared/components/Parts';
import { Body, Muted, Overline, Strong } from '@/shared/components/Text';
import { t } from '@/shared/i18n';

import { Slot } from '../types';
import { ApplyWindows, SlotFundingBox } from './ApplyBox';
import { SourceLink } from './SourceLink';
import { TierBadge, WhyLines } from './TierCard';

type Props = {
  /** "1. Your goal"; none for a list of other routes under one heading. */
  title?: string;
  slot: Slot | null;
  /** What to say when the plan has nothing for this choice. */
  empty: string;
  /** The university the plan is for: a choice elsewhere says where. */
  planUniversity?: string;
};

export function PlanSlot({ title, slot, empty, planUniversity }: Props) {
  const routeSource = slot?.bridge?.source_url;
  return (
    <View style={{ gap: 8 }}>
      {title ? <Overline>{title}</Overline> : null}
      {!slot ? (
        <Card>
          <Body>{empty}</Body>
        </Card>
      ) : (
        <Card style={{ gap: 12 }}>
          <TierBadge tier={slot.match.tier} label={slot.match.label} />
          <View style={{ gap: 2 }}>
            <Strong>{slot.match.programme_name}</Strong>
            {planUniversity && slot.match.university !== planUniversity ? (
              <Muted>{t('courseFinder.atUniversity', { university: slot.match.university_name })}</Muted>
            ) : null}
          </View>
          <WhyLines lines={slot.notes.length ? slot.notes : slot.match.explanation} />
          <SourceLink url={slot.match.source_url} />
          {routeSource && routeSource !== slot.match.source_url ? <SourceLink url={routeSource} /> : null}
          {slot.apply.length ? (
            <View style={{ gap: 8 }}>
              <Overline>{t('courseFinder.apply')}</Overline>
              <ApplyWindows windows={slot.apply} />
            </View>
          ) : null}
          {slot.funding ? <SlotFundingBox funding={slot.funding} /> : null}
          {!slot.match.confirmed && slot.match.notice ? <Muted>{slot.match.notice}</Muted> : null}
        </Card>
      )}
    </View>
  );
}
