import { useFocusEffect, useLocalSearchParams } from 'expo-router';
import { useCallback, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Card } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Muted, Overline, Strong, Title } from '@/shared/components/Text';
import { TextField } from '@/shared/components/TextField';
import { t } from '@/shared/i18n';
import { percent } from '@/shared/lib/dates';
import { fonts } from '@/shared/theme/tokens';

import { marksApi } from '../api/marksApi';
import { ProjectionCard, StandingCard } from '../components/ModuleCards';
import { Assessment, Module } from '../types';
import { Palette, useStyles } from '@/shared/theme/palette';

function asPercent(text: string): number | null | 'bad' {
  if (!text.trim()) return null;
  const n = Number(text.replace(',', '.'));
  return Number.isFinite(n) && n >= 0 && n <= 100 ? n : 'bad';
}

/** One module: where the student stands and is heading, and its assessments (tap one to change it). */
export default function ModuleScreen() {
  const styles = useStyles(makeStyles);
  const { id } = useLocalSearchParams<{ id: string }>();
  const [module, setModule] = useState<Module | null>(null);
  const [editing, setEditing] = useState<Assessment | null>(null);
  const [name, setName] = useState('');
  const [weight, setWeight] = useState('');
  const [mark, setMark] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useFocusEffect(
    useCallback(() => {
      marksApi
        .modules()
        .then((list) => setModule(list.find((m) => m.id === id) ?? null))
        .catch((e) => setError(errorText(e, t('common.error'))));
    }, [id]),
  );

  function edit(a: Assessment | null) {
    setEditing(a);
    setName(a?.name ?? '');
    setWeight(a ? percent(a.weight) : '');
    setMark(a?.mark != null ? percent(a.mark) : '');
    setError(null);
  }

  async function save() {
    const w = asPercent(weight);
    const m = asPercent(mark);
    if (!name.trim()) return setError(t('marks.nameMissing'));
    if (w === null || w === 'bad' || w === 0) return setError(t('marks.weightInvalid'));
    if (m === 'bad') return setError(t('marks.percentInvalid'));
    setBusy(true);
    setError(null);
    try {
      const body = { name: name.trim(), weight: w, mark: m };
      setModule(editing ? await marksApi.updateAssessment(id, editing.id, body) : await marksApi.addAssessment(id, body));
      edit(null);
    } catch (e) {
      setError(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    if (!editing) return;
    setBusy(true);
    try {
      setModule(await marksApi.removeAssessment(id, editing.id));
      edit(null);
    } catch (e) {
      setError(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Screen back>
      {!module && !error ? <Loading /> : null}
      {module ? (
        <>
          <View style={{ gap: 2 }}>
            <Title>{module.code}</Title>
            {module.name ? <Strong>{module.name}</Strong> : null}
          </View>
          <StandingCard module={module} />
          <ProjectionCard module={module} />
          <Overline>{t('marks.assessments')}</Overline>
          <Card style={{ paddingVertical: 4 }}>
            {module.assessments.map((a, i) => (
              <Pressable
                key={a.id}
                accessibilityRole="button"
                onPress={() => edit(a)}
                style={[styles.row, i < module.assessments.length - 1 && styles.rule]}>
                <View style={{ flex: 1 }}>
                  <Text style={styles.name}>{a.name}</Text>
                  <Muted>{t('week.weighting', { n: percent(a.weight) })}</Muted>
                </View>
                <Text style={[styles.mark, a.mark == null && styles.toCome]}>{a.mark != null ? `${percent(a.mark)}%` : t('marks.toCome')}</Text>
              </Pressable>
            ))}
          </Card>

          <Overline>{editing ? editing.name : t('marks.addAssessment')}</Overline>
          <TextField label={t('marks.assessment')} value={name} onChangeText={setName} maxLength={80} />
          <View style={styles.pair}>
            <View style={{ flex: 1 }}>
              <TextField label={t('marks.weight')} value={weight} onChangeText={setWeight} keyboardType="decimal-pad" maxLength={5} style={{ minWidth: 0, width: '100%' }} />
            </View>
            <View style={{ flex: 1 }}>
              <TextField label={t('marks.mark')} value={mark} onChangeText={setMark} keyboardType="decimal-pad" maxLength={5} style={{ minWidth: 0, width: '100%' }} />
            </View>
          </View>
          <Muted>{t('marks.markHint')}</Muted>
          {error ? <ErrorBox message={error} /> : null}
          <View style={styles.pair}>
            {editing ? <Button compact title={t('money.delete')} variant="secondary" icon="trash-2" onPress={remove} disabled={busy} /> : null}
            <Button compact title={editing ? t('money.save') : t('marks.addAssessment')} variant="accent" onPress={save} loading={busy} />
          </View>
        </>
      ) : null}
      {!module && error ? <ErrorBox message={error} /> : null}
    </Screen>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 11 },
  rule: { borderBottomWidth: 1, borderBottomColor: colors.line },
  name: { fontFamily: fonts.semibold, fontSize: 14.5, color: colors.text },
  mark: { fontFamily: fonts.bold, fontSize: 15, color: colors.ink },
  toCome: { fontFamily: fonts.medium, fontSize: 13, color: colors.textMuted },
  pair: { flexDirection: 'row', gap: 10 },
});
