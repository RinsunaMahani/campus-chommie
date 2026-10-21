/**
 * Import from a PDF: the student picks their university's class or exam timetable, the server reads it and
 * sends back everything it lists (nothing is kept there), the student types or taps their module codes, checks
 * the classes or exams that match, leaves out any that are wrong, and saves them in one go.
 */
import { Feather } from '@expo/vector-icons';
import * as DocumentPicker from 'expo-document-picker';
import { router, useLocalSearchParams } from 'expo-router';
import { useEffect, useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Card, InfoNote, ToggleRow } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Body, Muted, Overline, Title } from '@/shared/components/Text';
import { TextField } from '@/shared/components/TextField';
import { t } from '@/shared/i18n';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import { examsApi, timetableApi } from '../api/timetableApi';
import { moduleColour, rememberModules } from '../colours';
import { ExamCard } from '../components/ExamCard';
import { FoundClass, FoundExam, ImportAnswer, ImportLayout } from '../types';

/** The most codes shown to tap: a whole university's exam list has hundreds, so it's typed instead. */
const MAX_CHIPS = 40;

/** "mchm000, MPHS 000 mchm000" -> ["MCHM000", "MPHS000"]: upper case, no spaces, each once. */
export function parseCodes(text: string): string[] {
  const out: string[] = [];
  for (const raw of text.toUpperCase().split(/[,;\n]+/)) {
    // "MPHS 000" is one code; "MCHM000 MPHS000" is two.
    for (const code of raw.trim().split(/\s+(?=[A-Z])/)) {
      const clean = code.replace(/\s+/g, '');
      if (clean && !out.includes(clean)) out.push(clean);
    }
  }
  return out;
}

/** The rows for these codes, and the codes the PDF doesn't list. */
export function matching<T extends { module: string }>(rows: T[], codes: string[], listed: string[]) {
  return { rows: rows.filter((r) => codes.includes(r.module)), missing: codes.filter((c) => !listed.includes(c)) };
}

const key = (row: FoundClass | FoundExam) =>
  'weekday' in row ? `${row.module}|${row.weekday}|${row.starts}|${row.kind}` : `${row.module}|${row.on}|${row.starts}|${row.paper}`;

export default function ImportScreen() {
  const params = useLocalSearchParams<{ layout?: string }>();
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const [layout, setLayout] = useState<ImportLayout>(params.layout === 'exams' ? 'exams' : 'classes');
  const [answer, setAnswer] = useState<ImportAnswer | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [codesText, setCodesText] = useState('');
  const [left, setLeft] = useState<Set<string>>(new Set());
  const [replace, setReplace] = useState(false);
  const [reading, setReading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Exams: start from the modules already in the timetable.
  useEffect(() => {
    if (layout !== 'exams') return;
    timetableApi
      .mine()
      .then(({ entries }) => setCodesText((now) => now || [...new Set(entries.map((e) => e.module.replace(/\s+/g, '')))].join(', ')))
      .catch(() => undefined);
  }, [layout]);

  const codes = useMemo(() => parseCodes(codesText), [codesText]);
  const found = useMemo(() => {
    if (!answer) return { rows: [] as (FoundClass | FoundExam)[], missing: [] as string[] };
    const rows: (FoundClass | FoundExam)[] = answer.layout === 'classes' ? answer.classes : answer.exams;
    return matching(rows, codes, answer.modules);
  }, [answer, codes]);
  const chosen = found.rows.filter((r) => !left.has(key(r)));

  async function choose() {
    setError(null);
    const picked = await DocumentPicker.getDocumentAsync({ type: 'application/pdf', copyToCacheDirectory: true, multiple: false });
    if (picked.canceled || !picked.assets?.length) return;
    const asset = picked.assets[0];
    setReading(true);
    setAnswer(null);
    setLeft(new Set());
    setFileName(asset.name);
    try {
      const read = await timetableApi.importPdf({ uri: asset.uri, name: asset.name, mimeType: asset.mimeType, file: asset.file }, layout);
      rememberModules(read.modules);
      setAnswer(read);
    } catch (e) {
      setError(errorText(e, t('common.error')));
    } finally {
      setReading(false);
    }
  }

  function toggleCode(code: string) {
    const next = codes.includes(code) ? codes.filter((c) => c !== code) : [...codes, code];
    setCodesText(next.join(', '));
  }

  async function save() {
    if (!answer || !chosen.length) return;
    setSaving(true);
    setError(null);
    try {
      if (answer.layout === 'classes') {
        await timetableApi.addMany(
          (chosen as FoundClass[]).map((c) => ({ module: c.module, kind: c.kind, weekday: c.weekday, starts: c.starts, ends: c.ends, venue: c.venue })),
          replace,
        );
      } else {
        await examsApi.addMany(
          (chosen as FoundExam[]).map((e) => ({ module: e.module, on: e.on, starts: e.starts, minutes: e.minutes, title: e.title, paper: e.paper })),
          replace,
        );
      }
      router.back();
    } catch (e) {
      setError(errorText(e, t('common.error')));
    } finally {
      setSaving(false);
    }
  }

  const chip = (on: boolean, label: string, onPress: () => void, colour?: string) => (
    <Pressable key={label} accessibilityRole="button" accessibilityState={{ selected: on }} onPress={onPress} style={[styles.chip, on && styles.chipOn]}>
      <Text style={[styles.chipText, colour && !on ? { color: colour } : null, on && styles.chipTextOn]}>{label}</Text>
    </Pressable>
  );

  const n = chosen.length;
  return (
    <Screen
      back
      footer={
        answer && n ? (
          <Button
            title={t(answer.layout === 'classes' ? 'timetable.saveClasses' : 'timetable.saveExams', { n })}
            variant="primary"
            onPress={save}
            loading={saving}
          />
        ) : undefined
      }>
      <View style={{ gap: 6 }}>
        <Title>{t('timetable.importTitle')}</Title>
        <Muted>{t('timetable.importSub')}</Muted>
      </View>
      <View style={styles.row}>
        {chip(layout === 'classes', t('timetable.importClasses'), () => { setLayout('classes'); setAnswer(null); })}
        {chip(layout === 'exams', t('timetable.importExams'), () => { setLayout('exams'); setAnswer(null); })}
      </View>
      <Button
        title={answer ? t('timetable.chooseAnother') : t('timetable.choosePdf')}
        variant={answer ? 'secondary' : 'primary'}
        icon="file-text"
        onPress={choose}
        disabled={reading}
      />
      {fileName && (reading || answer) ? (
        <View style={styles.row}>
          <Feather name="file" size={14} color={colors.textMuted} />
          <Muted>{fileName}</Muted>
        </View>
      ) : null}
      {reading ? <Loading label={t('timetable.reading')} /> : null}
      {error ? <ErrorBox message={error} /> : null}

      {answer ? (
        <>
          <Card style={{ gap: 6 }}>
            {answer.lines.map((line, i) => (
              <Body key={i}>{line}</Body>
            ))}
          </Card>
          {answer.modules.length ? (
            <>
              <TextField
                label={t('timetable.yourModules')}
                value={codesText}
                onChangeText={setCodesText}
                autoCapitalize="characters"
                placeholder="MCHM000, MPHS000"
                hint={t('timetable.yourModulesHint')}
              />
              {answer.modules.length <= MAX_CHIPS ? (
                <View style={{ gap: 8 }}>
                  <Overline>{t('timetable.inThisPdf')}</Overline>
                  <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chips}>
                    {answer.modules.map((m) => chip(codes.includes(m), m, () => toggleCode(m), moduleColour(colors, m)))}
                  </ScrollView>
                </View>
              ) : null}
              {found.missing.length ? <InfoNote icon="alert-circle">{t('timetable.notInPdf', { codes: found.missing.join(', ') })}</InfoNote> : null}
              {!codes.length ? <InfoNote icon="info">{t('timetable.pickModules')}</InfoNote> : null}
            </>
          ) : null}

          {found.rows.length ? (
            <View style={{ gap: 8 }}>
              <Muted>{t('timetable.checkThese')}</Muted>
              {found.rows.map((row) => {
                const k = key(row);
                const out = left.has(k);
                const toggle = () =>
                  setLeft((now) => {
                    const next = new Set(now);
                    if (next.has(k)) next.delete(k);
                    else next.add(k);
                    return next;
                  });
                const label = t('timetable.leaveOut', { what: `${row.module} ${'weekday' in row ? `${row.day} ${row.starts}` : row.day}` });
                return (
                  <View key={k} style={out ? { opacity: 0.4 } : undefined}>
                    {'weekday' in row ? <FoundClassRow row={row} onToggle={toggle} label={label} /> : <ExamCard exam={row} onRemove={toggle} removeLabel={label} />}
                  </View>
                );
              })}
              <ToggleRow
                icon="refresh-cw"
                title={t(answer.layout === 'classes' ? 'timetable.replaceClasses' : 'timetable.replaceExams')}
                subtitle={t('timetable.replaceSub')}
                value={replace}
                onChange={setReplace}
              />
            </View>
          ) : null}
        </>
      ) : null}
    </Screen>
  );
}

function FoundClassRow({ row, onToggle, label }: { row: FoundClass; onToggle: () => void; label: string }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const colour = moduleColour(colors, row.module);
  return (
    <Card style={styles.found}>
      <View style={[styles.bar, { backgroundColor: colour }]} />
      <View style={{ flex: 1, gap: 3, paddingVertical: 10 }}>
        <Text style={[styles.module, { color: colour }]}>
          {row.module} <Text style={styles.kind}>{t(`timetable.kind.${row.kind}`)}</Text>
        </Text>
        <Text style={styles.meta}>
          {row.day} · {row.starts} to {row.ends}
          {row.venue ? ` · ${row.venue}` : ''}
        </Text>
      </View>
      <Pressable accessibilityRole="button" accessibilityLabel={label} onPress={onToggle} hitSlop={8} style={{ padding: 14 }}>
        <Feather name="x" size={18} color={colors.textMuted} />
      </Pressable>
    </Card>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    row: { flexDirection: 'row', alignItems: 'center', gap: 8 },
    chips: { gap: 8, paddingRight: 8 },
    chip: {
      paddingHorizontal: 14,
      paddingVertical: 8,
      borderRadius: radius.pill,
      borderWidth: 1,
      borderColor: colors.line,
      backgroundColor: colors.white,
    },
    chipOn: { backgroundColor: colors.accent, borderColor: colors.accent },
    chipText: { fontFamily: fonts.semibold, fontSize: 13, color: colors.ink },
    chipTextOn: { color: colors.pillText },
    found: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 0, overflow: 'hidden' },
    bar: { alignSelf: 'stretch', width: 5 },
    module: { fontFamily: fonts.bold, fontSize: 15 },
    kind: { fontFamily: fonts.medium, fontSize: 13, color: colors.textMuted },
    meta: { fontFamily: fonts.medium, fontSize: 13, color: colors.textMuted },
  });
