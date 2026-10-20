/**
 * Find my course's Home: one small job per card, nothing long. Your points (or "add my marks"), what
 * closes soon across universities and funders, and the way into courses, universities and colleges, and
 * the registration check. No account; nothing kept on a server.
 */
import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useEffect, useMemo, useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';

import { Button } from '@/shared/components/Button';
import { HeroScreen } from '@/shared/components/HeroScreen';
import { Card, ListRow, Tag } from '@/shared/components/Parts';
import { Body, Muted, Overline, Strong } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { colors, fonts } from '@/shared/theme/tokens';

import { courseFinderApi } from '../api/courseFinderApi';
import { checkRows } from '../marks';
import { useCourseFinder } from '../state';
import { UpcomingDeadline } from '../types';

export default function FinderHomeScreen() {
  const cf = useCourseFinder();
  const ready = useMemo(() => {
    const sent = checkRows(cf.rows);
    return sent.marks.length > 0 && !Object.keys(sent.errors).length;
  }, [cf.rows]);
  const [deadlines, setDeadlines] = useState<UpcomingDeadline[] | null>(null);

  useEffect(() => {
    courseFinderApi
      .deadlines()
      .then((d) => setDeadlines(d.deadlines))
      .catch(() => setDeadlines([]));
  }, []);

  return (
    <HeroScreen back tab title={t('finderHome.title')} subtitle={t('finderHome.sub')}>
      <Card style={styles.card}>
        <Overline>{t('finderHome.pointsTitle')}</Overline>
        <Body>{ready ? t('finderHome.pointsSome') : t('finderHome.pointsNone')}</Body>
        <Button
          title={ready ? t('finderHome.viewPoints') : t('finderHome.addMarks')}
          variant="accent"
          icon={ready ? 'bar-chart-2' : 'edit-3'}
          onPress={() => router.push(ready ? '/course-finder/qualify' : '/course-finder/marks')}
        />
      </Card>

      <View style={{ gap: 10 }}>
        <Overline>{t('finderHome.closingSoon')}</Overline>
        {deadlines && !deadlines.length ? <Muted>{t('finderHome.closingNone')}</Muted> : null}
        {deadlines?.length ? (
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.carousel}>
            {deadlines.map((d) => (
              <DeadlineCard key={`${d.kind}-${d.id}`} d={d} />
            ))}
          </ScrollView>
        ) : null}
      </View>

      <Card style={{ paddingVertical: 4 }}>
        <ListRow icon="book-open" title={t('finderHome.courses')} subtitle={t('finderHome.coursesSub')} onPress={() => router.push('/course-finder/courses')} />
        <ListRow icon="map" title={t('finderHome.explore')} subtitle={t('finderHome.exploreSub')} onPress={() => router.push('/course-finder/explore')} />
        <ListRow icon="shield" title={t('finderHome.check')} subtitle={t('finderHome.checkSub')} onPress={() => router.push('/course-finder/colleges/check')} last />
      </Card>
    </HeroScreen>
  );
}

function DeadlineCard({ d }: { d: UpcomingDeadline }) {
  const soon = d.days <= 7;
  return (
    <Card
      onPress={() => router.push(d.kind === 'university' ? `/course-finder/university/${d.id}` : `/course-finder/funding/${d.id}`)}
      style={styles.deadline}>
      <View style={styles.deadlineHead}>
        <Feather name={d.kind === 'university' ? 'home' : 'award'} size={14} color={colors.textMuted} />
        <Muted>{d.kind === 'university' ? t('finderHome.university') : t('finderHome.funder')}</Muted>
      </View>
      <Strong style={styles.deadlineName} numberOfLines={2}>
        {d.name}
      </Strong>
      <Text style={styles.deadlineLine} numberOfLines={2}>
        {d.line}
      </Text>
      <Tag label={d.label} tone={soon ? 'marigold' : 'jade'} />
    </Card>
  );
}

const styles = StyleSheet.create({
  card: { gap: 10, padding: 16 },
  carousel: { gap: 10, paddingRight: 8 },
  deadline: { width: 200, gap: 6, padding: 14 },
  deadlineHead: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  deadlineName: { fontSize: 14.5, lineHeight: 20, color: colors.text },
  deadlineLine: { fontFamily: fonts.body, fontSize: 12.5, lineHeight: 18, color: colors.textMuted },
});
