/**
 * Funding open now, soonest closing first, as cards that swipe: NSFAS and the
 * bursaries on the funding list; when none is open, those opening next. Each
 * opens the funder's own page. Funding is a separate application from the
 * university's, so it sits beside the results rather than inside them.
 */
import * as WebBrowser from 'expo-web-browser';
import { StyleSheet, Text, View } from 'react-native';

import { Tag } from '@/shared/components/Parts';
import { Overline } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { PressScale } from '@/shared/motion/PressScale';
import { SnapCarousel } from '@/shared/motion/SnapCarousel';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import { FundingCard } from '../types';
import { daysLeft, formatDay, inDays } from '../words';

const OPEN = ['open', 'closing_soon'];

export type FundingRow = { open: boolean; funders: FundingCard[] };

const soonest = (a: FundingCard, b: FundingCard) => (a.days ?? Infinity) - (b.days ?? Infinity);

/**
 * Open funders, the soonest closing first (those without a closing date after
 * them); or, when none is open, the ones opening next, the soonest first.
 */
export function fundingRow(funders: FundingCard[], most = 8): FundingRow {
  const open = funders.filter((f) => OPEN.includes(f.status)).sort(soonest).slice(0, most);
  if (open.length) return { open: true, funders: open };
  return { open: false, funders: funders.filter((f) => f.status === 'opens_later').sort(soonest).slice(0, most) };
}

/** "18 days left" while open; "Opens Fri 18 Sep 2026 · in 109 days" before. */
function when(f: FundingCard, open: boolean): string | null {
  if (open) return f.days != null ? daysLeft(f.days) : null;
  if (!f.opens) return null;
  const opens = t('courseFinder.fundingOpens', { date: formatDay(f.opens) });
  return f.days != null ? `${opens} · ${inDays(f.days)}` : opens;
}

export function ClosingSoon({ row }: { row: FundingRow }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const { open, funders } = row;
  if (!funders.length) return null;
  const title = open ? t('courseFinder.fundingNow') : t('courseFinder.fundingNext');
  return (
    <View style={{ gap: 10 }}>
      <Overline>{title}</Overline>
      <SnapCarousel
        items={funders}
        cardWidth={248}
        keyOf={(f) => f.id}
        label={title}
        render={(f) => (
          <PressScale
            accessibilityRole="link"
            accessibilityLabel={[f.name, f.heading, when(f, open) ?? f.label].filter(Boolean).join('. ')}
            disabled={!f.url}
            onPress={() => f.url && WebBrowser.openBrowserAsync(f.url)}
            style={styles.card}>
            <Tag label={f.label} tone={f.status === 'closing_soon' ? 'marigold' : open ? 'jade' : 'info'} />
            <Text style={styles.name} numberOfLines={2}>
              {f.short_name ?? f.name}
            </Text>
            {f.heading ? <Text style={styles.heading}>{f.heading}</Text> : null}
            {when(f, open) ? (
              <Text style={[styles.days, !open && { color: colors.textMuted }, f.status === 'closing_soon' && { color: colors.marigoldDeep }]}>
                {when(f, open)}
              </Text>
            ) : null}
          </PressScale>
        )}
      />
    </View>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
  card: {
    minHeight: 132,
    gap: 6,
    padding: 14,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.white,
  },
  name: { fontFamily: fonts.bold, fontSize: 16, lineHeight: 20, color: colors.text },
  heading: { fontFamily: fonts.medium, fontSize: 14, color: colors.textMuted },
  days: { fontFamily: fonts.bold, fontSize: 14, color: colors.jade, marginTop: 'auto' },
});
