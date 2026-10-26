/**
 * Home's "Your week in review": shown on the student's check-in day (this week) and for the two days after it
 * (last week), with the week's headline. Hidden on other days and when the server can't be reached.
 */
import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';

import { Card, ListRow } from '@/shared/components/Parts';
import { t } from '@/shared/i18n';

import { reviewApi } from '../api/reviewApi';
import { WeekReview } from '../types';

export function HomeReviewCard() {
  const [review, setReview] = useState<WeekReview | null>(null);

  useFocusEffect(
    useCallback(() => {
      reviewApi
        .mine('auto')
        .then(setReview)
        .catch(() => setReview(null));
    }, []),
  );

  if (!review?.ready) return null;
  return (
    <Card style={{ paddingVertical: 4 }}>
      <ListRow
        tone="mint"
        icon="bar-chart-2"
        title={t(review.week === 'last' ? 'review.homeLast' : 'review.homeThis')}
        subtitle={review.headline}
        onPress={() => router.push({ pathname: '/review', params: { week: review.week } })}
        last
      />
    </Card>
  );
}
