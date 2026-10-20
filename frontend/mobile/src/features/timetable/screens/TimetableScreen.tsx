/**
 * The Timetable tab: the classes the student entered, day by day, each module in its own colour, with what
 * the week adds up to (and any clashes) on top. "Add a class" opens the form. Only the student sees it.
 */
import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Card } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox } from '@/shared/components/Status';
import { Body, Muted, Overline, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { SkeletonCards } from '@/shared/motion/Shimmer';

import { timetableApi } from '../api/timetableApi';
import { rememberModules } from '../colours';
import { ClassCard } from '../components/ClassCard';
import { TimetableAnswer } from '../types';

export const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

export default function TimetableScreen() {
  const [answer, setAnswer] = useState<TimetableAnswer | null>(null);
  const [error, setError] = useState<string | null>(null);

  useFocusEffect(
    useCallback(() => {
      timetableApi
        .mine()
        .then((a) => {
          setError(null);
          rememberModules(a.entries.map((e) => e.module));
          setAnswer(a);
        })
        .catch((e) => setError(errorText(e, t('common.error'))));
    }, []),
  );

  return (
    <Screen tab>
      <View style={{ gap: 6 }}>
        <Title>{t('timetable.title')}</Title>
        <Muted>{t('timetable.sub')}</Muted>
      </View>
      <Button title={t('timetable.add')} variant="primary" icon="plus" onPress={() => router.push('/timetable/new')} />
      {error ? <ErrorBox message={error} /> : null}
      {!answer && !error ? <SkeletonCards count={3} /> : null}
      {answer ? (
        <Card style={{ gap: 6 }}>
          {answer.lines.map((line, i) => (
            <Body key={i}>{line}</Body>
          ))}
        </Card>
      ) : null}
      {answer
        ? DAY_NAMES.map((day, weekday) => {
            const classes = answer.entries.filter((e) => e.weekday === weekday);
            if (!classes.length) return null;
            return (
              <View key={day} style={{ gap: 8 }}>
                <Overline>{day}</Overline>
                {classes.map((e) => (
                  <ClassCard key={e.id} entry={e} />
                ))}
              </View>
            );
          })
        : null}
    </Screen>
  );
}
