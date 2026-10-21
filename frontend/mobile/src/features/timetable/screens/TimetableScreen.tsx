/**
 * The Timetable tab: the classes the student entered, day by day, each module in its own colour, with what
 * the week adds up to (and any clashes) on top, then their exams. "Add a class" opens the form; "Import from a
 * PDF" reads their university's class or exam timetable. Only the student sees it.
 */
import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { View } from 'react-native';

import { studentHeader } from '@/features/profile/components/HeaderTools';
import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Card } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox } from '@/shared/components/Status';
import { Body, Overline, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { SkeletonCards } from '@/shared/motion/Shimmer';

import { examsApi, timetableApi } from '../api/timetableApi';
import { rememberModules } from '../colours';
import { ClassCard } from '../components/ClassCard';
import { ExamCard } from '../components/ExamCard';
import { ExamsAnswer, TimetableAnswer } from '../types';

export const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

export default function TimetableScreen() {
  const [answer, setAnswer] = useState<TimetableAnswer | null>(null);
  const [exams, setExams] = useState<ExamsAnswer | null>(null);
  const [error, setError] = useState<string | null>(null);

  useFocusEffect(
    useCallback(() => {
      Promise.all([timetableApi.mine(), examsApi.mine()])
        .then(([a, x]) => {
          setError(null);
          rememberModules([...a.entries.map((e) => e.module), ...x.exams.map((e) => e.module)]);
          setAnswer(a);
          setExams(x);
        })
        .catch((e) => setError(errorText(e, t('common.error'))));
    }, []),
  );

  function removeExam(id: string) {
    examsApi
      .remove(id)
      .then(setExams)
      .catch((e) => setError(errorText(e, t('common.error'))));
  }

  return (
    <Screen back title={t('timetable.title')} subtitle={t('timetable.sub')} {...studentHeader()}>
      <View style={{ flexDirection: 'row', gap: 10 }}>
        <View style={{ flex: 1 }}>
          <Button title={t('timetable.add')} variant="primary" icon="plus" compact onPress={() => router.push('/timetable/new')} />
        </View>
        <View style={{ flex: 1 }}>
          <Button title={t('timetable.importButton')} variant="secondary" icon="file-text" compact onPress={() => router.push('/timetable/import')} />
        </View>
      </View>
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
      {exams ? (
        <View style={{ gap: 8 }}>
          <Title style={{ fontSize: 20 }}>{t('timetable.exams')}</Title>
          <Card style={{ gap: 6 }}>
            {exams.lines.map((line, i) => (
              <Body key={i}>{line}</Body>
            ))}
          </Card>
          {exams.exams.map((x) => (
            <ExamCard key={x.id} exam={x} onRemove={() => removeExam(x.id)} removeLabel={t('timetable.deleteExam', { module: x.module })} />
          ))}
          <Button
            title={t('timetable.importExamsButton')}
            variant="secondary"
            icon="file-text"
            onPress={() => router.push({ pathname: '/timetable/import', params: { layout: 'exams' } })}
          />
        </View>
      ) : null}
    </Screen>
  );
}
