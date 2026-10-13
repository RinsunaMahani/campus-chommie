import { Feather } from '@expo/vector-icons';
import { Redirect, router } from 'expo-router';
import { useMemo, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { Button } from '@/shared/components/Button';
import { InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { SelectField } from '@/shared/components/SelectField';
import { TextField } from '@/shared/components/TextField';
import { Body, Muted, Overline, Title } from '@/shared/components/Text';
import { MessageKey, t } from '@/shared/i18n';
import { colors, fonts, radius } from '@/shared/theme/tokens';

import { courseFinderApi } from '../api/courseFinderApi';
import { ErrorBox } from '../components/Status';
import { checkRows, cleanPercent, MarkRow, newRow } from '../marks';
import { useCourseFinder } from '../state';
import { MAX_SUBJECTS, subjectOptions } from '../subjects';
import { errorText } from '../words';

/** Step 2: the learner's marks, one row per subject, up to nine. Never saved and never logged. */
export default function MarksScreen() {
  const cf = useCourseFinder();
  const [errors, setErrors] = useState<Record<number, MessageKey>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const options = useMemo(() => subjectOptions(), []);

  if (!cf.university) return <Redirect href="/course-finder" />;
  const university = cf.university;
  const rows = cf.rows;

  function update(key: number, patch: Partial<MarkRow>) {
    cf.setRows(rows.map((r) => (r.key === key ? { ...r, ...patch } : r)));
    setErrors((current) => {
      const next = { ...current };
      delete next[key];
      return next;
    });
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

      {rows.map((row, index) => {
        const taken = new Set(rows.filter((r) => r.key !== row.key && r.subject).map((r) => r.subject));
        const error = errors[row.key];
        return (
          <View key={row.key} style={{ gap: 4 }}>
            <View style={styles.row}>
              <View style={{ flex: 1 }}>
                <SelectField
                  label={t('courseFinder.subject', { n: index + 1 })}
                  sheetTitle={t('courseFinder.subjectPick')}
                  placeholder={t('courseFinder.subjectPick')}
                  value={row.subject}
                  options={options.filter((o) => !taken.has(o.value))}
                  onChange={(subject) => update(row.key, { subject })}
                />
              </View>
              <View style={styles.mark}>
                <TextField
                  label={t('courseFinder.percent')}
                  value={row.percent}
                  onChangeText={(text) => update(row.key, { percent: cleanPercent(text) })}
                  keyboardType="number-pad"
                  maxLength={3}
                  placeholder="0"
                  style={styles.markInput}
                  accessibilityLabel={`${t('courseFinder.subject', { n: index + 1 })}: ${t('courseFinder.percent')}`}
                />
              </View>
              <Pressable
                accessibilityRole="button"
                accessibilityLabel={t('courseFinder.removeSubject', { n: index + 1 })}
                onPress={() => cf.setRows(rows.filter((r) => r.key !== row.key))}
                hitSlop={6}
                style={styles.remove}>
                <Feather name="x" size={18} color={colors.textMuted} />
              </Pressable>
            </View>
            {error ? <Text style={styles.error}>{t(error)}</Text> : null}
          </View>
        );
      })}

      {rows.length < MAX_SUBJECTS ? (
        <Button title={t('courseFinder.addSubject')} variant="secondary" icon="plus" onPress={() => cf.setRows([...rows, newRow()])} />
      ) : (
        <Muted>{t('courseFinder.addSubjectFull', { n: MAX_SUBJECTS })}</Muted>
      )}

      {formError ? <ErrorBox message={formError} /> : null}
      <InfoNote icon="lock">{t('courseFinder.nothingStored')}</InfoNote>
    </Screen>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'flex-end', gap: 8 },
  mark: { width: 86 },
  // On the web an input keeps its default width unless allowed to shrink into its box.
  markInput: { minWidth: 0, width: '100%' },
  // 50 px: the same height as the fields beside it.
  remove: {
    width: 36,
    height: 50,
    borderRadius: radius.sm,
    alignItems: 'center',
    justifyContent: 'center',
  },
  error: { fontFamily: fonts.body, fontSize: 12, color: colors.garnet },
});
