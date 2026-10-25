/**
 * Your week in review: what's behind you, what's coming, how your marks moved and how your spending compares with
 * your usual. The week is the one your money check-in uses. Opens on the week Home offers (this week on your
 * check-in day, last week for the two days after); the tabs switch between the two. Every line comes from the
 * server in words; nothing here is worked out on the phone.
 */
import { router, useFocusEffect, useLocalSearchParams } from 'expo-router';
import { useCallback, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Card, IconTile, InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Muted, Overline, Strong, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { formatDay } from '@/shared/lib/dates';
import { SlidingTabs } from '@/shared/motion/SlidingTabs';
import { Palette, useStyles } from '@/shared/theme/palette';
import { fonts, space, type } from '@/shared/theme/tokens';

import { reviewApi } from '../api/reviewApi';
import { SpendingWeeks } from '../components/SpendingWeeks';
import { ReviewLine, WeekReview, WhichWeek } from '../types';

const ARROW: Record<string, string> = { up: '↑', down: '↓', same: '→', first: '•' };

export default function WeekReviewScreen() {
  const styles = useStyles(makeStyles);
  const params = useLocalSearchParams<{ week?: string }>();
  const [week, setWeek] = useState<WhichWeek>(params.week === 'this' || params.week === 'last' ? params.week : 'auto');
  const [review, setReview] = useState<WeekReview | null>(null);
  const [failure, setFailure] = useState<string | null>(null);

  const load = useCallback((which: WhichWeek) => {
    reviewApi
      .mine(which)
      .then((r) => {
        setFailure(null);
        setReview(r);
      })
      .catch((e) => setFailure(errorText(e, t('common.error'))));
  }, []);

  useFocusEffect(
    useCallback(() => {
      load(week);
    }, [load, week]),
  );

  const shown: 'this' | 'last' = review?.week ?? 'this';
  const pick = (index: number) => {
    const next = index === 0 ? 'this' : 'last';
    if (next === shown) return;
    setReview(null);
    setWeek(next);
  };

  return (
    <Screen back>
      <Title>{t('review.title')}</Title>
      <SlidingTabs tabs={[t('review.thisWeek'), t('review.lastWeek')]} index={shown === 'this' ? 0 : 1} onChange={pick} />
      {failure ? <ErrorBox message={failure} onRetry={() => load(week)} /> : null}
      {!review && !failure ? <Loading /> : null}

      {review ? (
        <View style={{ gap: space.md }}>
          <Card style={styles.headline}>
            <IconTile name="bar-chart-2" size={44} />
            <View style={{ flex: 1, gap: 2 }}>
              <Strong style={styles.headlineText}>{review.headline}</Strong>
              <Muted>
                {t(review.finished ? 'review.span' : 'review.spanSoFar', {
                  start: formatDay(review.week_start),
                  end: formatDay(review.week_end),
                })}
              </Muted>
            </View>
          </Card>

          <Section title={t('review.done')} lines={review.done} empty={t(review.week === 'last' ? 'review.doneEmptyLast' : 'review.doneEmpty')} />
          <Section title={t('review.coming')} lines={review.coming} empty={t('review.comingEmpty')} />

          {review.marks.length ? (
            <View style={{ gap: space.sm }}>
              <Overline>{t('review.marks')}</Overline>
              <Card style={{ gap: space.sm }}>
                {review.marks.map((m) => (
                  <View key={m.code} style={styles.line}>
                    <Text style={styles.arrow} accessibilityElementsHidden importantForAccessibility="no">
                      {ARROW[m.direction]}
                    </Text>
                    <Text style={styles.lineText}>{m.text}</Text>
                  </View>
                ))}
              </Card>
            </View>
          ) : null}

          <View style={{ gap: space.sm }}>
            <Overline>{t('review.spending')}</Overline>
            <Card style={{ gap: space.md }}>
              <Text style={styles.lineText}>{review.spending.text}</Text>
              {review.spending.weeks.some((w) => w != null) ? <SpendingWeeks weeks={review.spending.weeks} /> : null}
              {review.spending.spent_cents == null && review.week === 'this' ? (
                <Button title={t('money.checkin.title')} variant="secondary" compact onPress={() => router.push('/money/checkin')} />
              ) : null}
            </Card>
          </View>

          {review.support ? (
            <Card style={{ gap: space.sm }}>
              <Text style={styles.lineText}>{review.support}</Text>
              <Button title={t('review.openSupport')} variant="secondary" compact onPress={() => router.push('/support')} />
            </Card>
          ) : null}

          <InfoNote icon="lock">{t('review.private')}</InfoNote>
        </View>
      ) : null}
    </Screen>
  );
}

function Section({ title, lines, empty }: { title: string; lines: ReviewLine[]; empty: string }) {
  const styles = useStyles(makeStyles);
  return (
    <View style={{ gap: space.sm }}>
      <Overline>{title}</Overline>
      <Card style={{ gap: space.sm }}>
        {lines.length ? (
          lines.map((l, i) => (
            <View key={i} style={styles.line}>
              <Text style={styles.arrow} accessibilityElementsHidden importantForAccessibility="no">
                •
              </Text>
              <Text style={styles.lineText}>{l.text}</Text>
            </View>
          ))
        ) : (
          <Muted>{empty}</Muted>
        )}
      </Card>
    </View>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    headline: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: space.md,
      backgroundColor: colors.accentTint,
      borderColor: colors.accentDeep,
    },
    headlineText: { ...type.callout, color: colors.ink },
    line: { flexDirection: 'row', gap: space.sm, alignItems: 'flex-start' },
    arrow: { fontFamily: fonts.bold, fontSize: 15, lineHeight: 21, color: colors.accentDeep, width: 14 },
    lineText: { flex: 1, fontFamily: fonts.body, fontSize: 15, lineHeight: 21, color: colors.ink },
  });
