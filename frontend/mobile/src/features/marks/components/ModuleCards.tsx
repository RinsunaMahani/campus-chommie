/** Where a student stands in a module, and where they're heading: the server's own sentences, with the numbers big. */
import { StyleSheet, Text } from 'react-native';

import { Card } from '@/shared/components/Parts';
import { Muted, Overline } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { percent } from '@/shared/lib/dates';
import { colors, fonts } from '@/shared/theme/tokens';

import { Module } from '../types';

export function StandingCard({ module }: { module: Module }) {
  const s = module.standing;
  return (
    <Card style={{ gap: 6 }}>
      <Overline>{t('marks.standing')}</Overline>
      {s.current != null ? <Text style={styles.big}>{`${percent(s.current)}%`}</Text> : null}
      <Text style={styles.line}>{s.message}</Text>
      <Muted>{t('marks.targetIs', { n: percent(module.target) })}</Muted>
    </Card>
  );
}

export function ProjectionCard({ module }: { module: Module }) {
  const p = module.projection;
  if (!p) return null;
  return (
    <Card style={{ gap: 6 }}>
      <Overline>{t('marks.projection')}</Overline>
      {p.projected != null ? <Text style={[styles.big, p.below_target && styles.below]}>{t('marks.projected', { n: Math.round(p.projected) })}</Text> : null}
      {p.low != null && p.high != null ? <Muted>{t('marks.range', { low: Math.round(p.low), high: Math.round(p.high) })}</Muted> : null}
      <Text style={styles.line}>{p.message}</Text>
    </Card>
  );
}

const styles = StyleSheet.create({
  big: { fontFamily: fonts.display, fontSize: 28, lineHeight: 34, color: colors.ink },
  line: { fontFamily: fonts.body, fontSize: 14, lineHeight: 21, color: colors.text },
  below: { color: colors.marigoldDeep },
});
