/**
 * One programme as the learner matches it: the tier in words (colour and an
 * icon only add to it), the "why" lines, the source, and the notice while
 * nobody has checked the university's data.
 */
import { Feather } from '@expo/vector-icons';
import { ComponentProps } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { Button } from '@/shared/components/Button';
import { Card } from '@/shared/components/Parts';
import { Muted, Overline, Strong } from '@/shared/components/Text';
import { UniMonogram } from '@/shared/components/UniMonogram';
import { t } from '@/shared/i18n';
import { colors, fonts, radius } from '@/shared/theme/tokens';

import { Match, Tier } from '../types';
import { SourceLink } from '@/shared/components/SourceLink';

type IconName = ComponentProps<typeof Feather>['name'];

const LOOK: Record<Tier, { icon: IconName; bg: string; fg: string }> = {
  competitive: { icon: 'check-circle', bg: colors.jadeTint, fg: colors.jade },
  meets_minimum: { icon: 'check', bg: colors.accentTint, fg: colors.accentDeep },
  reach: { icon: 'trending-up', bg: colors.marigoldTint, fg: colors.marigoldDeep },
  not_yet: { icon: 'x-circle', bg: colors.garnetTint, fg: colors.garnet },
  unverified: { icon: 'help-circle', bg: colors.iconTile, fg: colors.textMuted },
};

/** The tier's label, as the server words it. */
export function TierBadge({ tier, label }: { tier: Tier; label: string }) {
  const look = LOOK[tier] ?? LOOK.unverified;
  return (
    <View style={[styles.badge, { backgroundColor: look.bg }]}>
      <Feather name={look.icon} size={13} color={look.fg} />
      <Text style={[styles.badgeText, { color: look.fg }]}>{label}</Text>
    </View>
  );
}

/** The plain-words reasons, one per line. */
export function WhyLines({ lines }: { lines: string[] }) {
  if (!lines.length) return null;
  return (
    <View style={{ gap: 4 }}>
      <Overline>{t('courseFinder.why')}</Overline>
      {lines.map((line, i) => (
        <View key={i} style={styles.line}>
          <Text style={styles.bullet}>•</Text>
          <Text style={styles.lineText}>{line}</Text>
        </View>
      ))}
    </View>
  );
}

type Props = {
  match: Match;
  /** Name the university too (a list across universities). */
  showUniversity?: boolean;
  onPick?: () => void;
  picking?: boolean;
};

export function TierCard({ match, showUniversity, onPick, picking }: Props) {
  return (
    <Card style={{ gap: 10 }}>
      <TierBadge tier={match.tier} label={match.label} />
      <View style={styles.title}>
        {showUniversity ? <UniMonogram id={match.university} size={36} /> : null}
        <View style={{ flex: 1, gap: 2 }}>
          <Strong>{match.programme_name}</Strong>
          {showUniversity ? <Muted>{match.university_name}</Muted> : null}
        </View>
      </View>
      <WhyLines lines={match.explanation} />
      <SourceLink url={match.source_url} />
      {!match.confirmed && match.notice ? <Muted>{match.notice}</Muted> : null}
      {onPick ? <Button title={t('courseFinder.pickGoal')} variant="secondary" onPress={onPick} loading={picking} /> : null}
    </Card>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    alignSelf: 'flex-start',
    borderRadius: radius.pill,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  badgeText: { fontFamily: fonts.bold, fontSize: 13 },
  title: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  line: { flexDirection: 'row', gap: 8 },
  bullet: { fontFamily: fonts.bold, fontSize: 15, lineHeight: 20, color: colors.textFaint },
  lineText: { flex: 1, fontFamily: fonts.body, fontSize: 14.5, lineHeight: 20, color: colors.text },
});
