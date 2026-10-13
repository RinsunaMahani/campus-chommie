import { Feather } from '@expo/vector-icons';
import { Redirect, router } from 'expo-router';
import { useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { Button } from '@/shared/components/Button';
import { Card, InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox } from '@/shared/components/Status';
import { Body, Muted, Overline, Title } from '@/shared/components/Text';
import { MessageKey, t } from '@/shared/i18n';
import { colors, fonts, radius } from '@/shared/theme/tokens';

import { courseFinderApi } from '../api/courseFinderApi';
import { SubjectPicker } from '../components/SubjectPicker';
import { checkRows, cleanPercent, rowsFor } from '../marks';
import { useCourseFinder } from '../state';
import { SUBJECTS, subjectName } from '../subjects';
import { errorText } from '../words';

/** Step 2: the learner's subjects, picked in one go, and a mark for each. Never saved and never logged. */
export default function MarksScreen() {
  const cf = useCourseFinder();
  const [picking, setPicking] = useState(false);
  const [errors, setErrors] = useState<Record<string, MessageKey>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (!cf.university) return <Redirect href="/course-finder" />;
  const university = cf.university;
  const rows = cf.rows;

  /** Errors only for the subjects still there, and none for `fixed`. */
  function keepErrors(subjects: string[], fixed?: string) {
    setErrors((current) => {
      const next: Record<string, MessageKey> = {};
      for (const s of subjects) if (current[s] && s !== fixed) next[s] = current[s];
      return next;
    });
  }

  function setMark(subject: string, text: string) {
    cf.setRows(rows.map((r) => (r.subject === subject ? { ...r, percent: cleanPercent(text) } : r)));
    keepErrors(rows.map((r) => r.subject), subject);
  }

  function remove(subject: string) {
    const left = rows.filter((r) => r.subject !== subject);
    cf.setRows(left);
    keepErrors(left.map((r) => r.subject));
  }

  function choose(chosen: string[]) {
    cf.setRows(rowsFor(chosen, rows));
    keepErrors(chosen);
    setFormError(null);
    setPicking(false);
  }

  async function submit() {
    const { marks, errors: rowErrors } = checkRows(rows);
    setErrors(rowErrors);
    setFormError(null);
    if (Object.keys(rowErrors).length) return;
    if (!marks.length) {
      setFormError(t('courseFinder.marksEmpty'));
      return;
    }
    setBusy(true);
    try {
      cf.setAnswer(await courseFinderApi.assess(university.id, marks));
      router.push('/course-finder/results');
    } catch (e) {
      setFormError(errorText(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Screen back footer={<Button title={t('courseFinder.show')} variant="accent" onPress={submit} loading={busy} />}>
      <View style={{ gap: 6 }}>
        <Overline>{t('courseFinder.step', { n: 2 })}</Overline>
        <Title>{t('courseFinder.marksHeading')}</Title>
        <Body>{t('courseFinder.marksHelp')}</Body>
        <Muted>{university.name}</Muted>
      </View>

      {rows.length ? (
        <Card style={styles.card}>
          <View style={styles.head}>
            <Text style={[styles.headText, { flex: 1 }]}>{t('courseFinder.subjectsHeading')}</Text>
            <Text style={[styles.headText, styles.headMark]}>{t('courseFinder.percent')}</Text>
          </View>
          {rows.map((row) => {
            const name = subjectName(row.subject);
            const error = errors[row.subject];
            const level = SUBJECTS[row.subject]?.folder === 'more_languages' ? t('courseFinder.secondAdditional') : null;
            return (
              <View key={row.subject} style={styles.line}>
                <View style={styles.row}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.name}>{name}</Text>
                    {level ? <Text style={styles.level}>{level}</Text> : null}
                  </View>
                  <TextInput
                    value={row.percent}
                    onChangeText={(text) => setMark(row.subject, text)}
                    keyboardType="number-pad"
                    maxLength={3}
                    placeholder="0"
                    placeholderTextColor={colors.textFaint}
                    accessibilityLabel={t('courseFinder.markFor', { subject: name })}
                    style={[styles.markBox, !!error && { borderColor: colors.garnet }]}
                  />
                  <Pressable
                    accessibilityRole="button"
                    accessibilityLabel={t('courseFinder.removeSubject', { subject: name })}
                    onPress={() => remove(row.subject)}
                    hitSlop={6}
                    style={styles.remove}>
                    <Feather name="x" size={18} color={colors.textMuted} />
                  </Pressable>
                </View>
                {error ? <Text style={styles.error}>{t(error)}</Text> : null}
              </View>
            );
          })}
        </Card>
      ) : (
        <Body>{t('courseFinder.noSubjects')}</Body>
      )}

      <Button
        title={rows.length ? t('courseFinder.changeSubjects') : t('courseFinder.chooseSubjects')}
        variant={rows.length ? 'secondary' : 'primary'}
        icon="list"
        onPress={() => setPicking(true)}
      />

      {formError ? <ErrorBox message={formError} /> : null}
      <InfoNote icon="lock">{t('courseFinder.nothingStored')}</InfoNote>

      {picking ? <SubjectPicker chosen={rows.map((r) => r.subject)} onDone={choose} onClose={() => setPicking(false)} /> : null}
    </Screen>
  );
}

// The mark column: a 72 px box, then the 36 px remove button 8 px further on.
const MARK = 72;
const REMOVE = 36;

const styles = StyleSheet.create({
  card: { paddingVertical: 6 },
  head: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingTop: 4, paddingBottom: 6 },
  headText: { fontFamily: fonts.semibold, fontSize: 12.5, color: colors.textMuted },
  headMark: { width: MARK, textAlign: 'center', marginRight: REMOVE + 8 },
  line: { borderTopWidth: 1, borderTopColor: colors.line, paddingVertical: 8, gap: 4 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  name: { fontFamily: fonts.semibold, fontSize: 15, color: colors.text },
  level: { fontFamily: fonts.body, fontSize: 12.5, color: colors.textMuted, marginTop: 1 },
  markBox: {
    width: MARK,
    height: 44,
    borderRadius: radius.sm,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.white,
    paddingHorizontal: 8,
    textAlign: 'center',
    fontFamily: fonts.semibold,
    fontSize: 16,
    color: colors.text,
  },
  remove: { width: REMOVE, height: 44, borderRadius: radius.sm, alignItems: 'center', justifyContent: 'center' },
  error: { fontFamily: fonts.body, fontSize: 12, color: colors.garnet },
});
