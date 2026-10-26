/**
 * One college: its status in words (with DHET's warning signs when its registration is cancelled), its
 * registration number, website and office line, the occupational qualifications a TVET college offers or
 * the qualifications a private one is registered for, where it may teach, the register's own notes, and
 * where each fact comes from. No entry requirements: DHET's lists don't have them, and we never guess.
 */
import { Feather } from '@expo/vector-icons';
import { useLocalSearchParams } from 'expo-router';
import * as WebBrowser from 'expo-web-browser';
import { useEffect, useState } from 'react';
import { Linking, Pressable, StyleSheet, Text, View } from 'react-native';

import { errorText, formatDay } from '@/features/courseFinder/words';
import { HeroScreen } from '@/shared/components/HeroScreen';
import { Card, InfoNote, Tag } from '@/shared/components/Parts';
import { SourceLink } from '@/shared/components/SourceLink';
import { ErrorBox } from '@/shared/components/Status';
import { Muted, Overline } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { SkeletonCards } from '@/shared/motion/Shimmer';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts } from '@/shared/theme/tokens';

import { collegesApi } from '../api/collegesApi';
import { statusTone } from '../CollegeRow';
import { CollegeAnswer, WarningSigns } from '../types';

const FIRST = 8;

export default function CollegeScreen() {
  const styles = useStyles(makeStyles);
  const { id } = useLocalSearchParams<{ id: string }>();
  const [answer, setAnswer] = useState<CollegeAnswer | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (!id) return;
    collegesApi
      .college(id)
      .then(setAnswer)
      .catch((e) => setError(errorText(e)));
  }, [id, attempt]);

  const c = answer?.college;
  return (
    <HeroScreen back title={c?.name ?? t('colleges.title')} subtitle={c ? [c.kind_label, ...c.provinces].join(' · ') : undefined}>
      {error ? (
        <ErrorBox
          message={error}
          onRetry={() => {
            setError(null);
            setAttempt((n) => n + 1);
          }}
        />
      ) : null}
      {!answer && !error ? <SkeletonCards count={3} /> : null}

      {c && answer ? (
        <View style={{ gap: 14 }}>

          <Card style={styles.card}>
            <Tag label={c.label} tone={statusTone(c.status)} />
            {c.lines.map((line, i) => (
              <Text key={i} style={styles.line}>
                {line}
              </Text>
            ))}
          </Card>

          {answer.warning_signs ? <Signs signs={answer.warning_signs} /> : null}

          <Card style={styles.card}>
            {c.kind !== 'tvet' ? (
              <Fact label={t('colleges.registration')} value={c.registration_number ?? t('colleges.noNumber')} />
            ) : null}
            {c.website ? (
              <Fact label={t('colleges.website')} value={c.website} onPress={() => WebBrowser.openBrowserAsync(`https://${c.website}`)} />
            ) : null}
            {c.website_problem ? (
              <View style={styles.fact}>
                <Muted>{t('colleges.website')}</Muted>
                <Text style={styles.line}>
                  {t('colleges.websiteProblem', {
                    site: c.website_problem.listed,
                    note: c.website_problem.note.replace(/\.$/, ''),
                    date: formatDay(c.website_problem.checked),
                  })}
                </Text>
              </View>
            ) : null}
            {c.phone ? <Fact label={t('colleges.phone')} value={c.phone} onPress={() => Linking.openURL(`tel:${c.phone!.split('/')[0].replace(/\s/g, '')}`)} /> : null}
          </Card>

          {c.occupational.length ? (
            <Card style={styles.card}>
              <Overline>{t('colleges.occupational')}</Overline>
              <Muted>{t('colleges.occupationalNote')}</Muted>
              {c.occupational.map((q) => (
                <View key={q.saqa_id} style={styles.qual}>
                  <Text style={styles.itemText}>{q.name}</Text>
                  <View style={styles.tags}>
                    <Tag label={q.nsfas_allowances ? t('colleges.nsfasYes') : t('colleges.nsfasNo')} tone={q.nsfas_allowances ? 'jade' : 'muted'} />
                    {q.centre_of_specialisation ? <Tag label={t('colleges.specialisation')} tone="info" /> : null}
                  </View>
                </View>
              ))}
            </Card>
          ) : null}

          {c.qualifications.length ? (
            <ListCard title={t('colleges.qualifications')} note={t('colleges.qualificationsNote')} items={c.qualifications} />
          ) : null}
          {c.sites.length ? <ListCard title={t('colleges.sites')} items={c.sites} /> : null}
          {c.notes.length ? <ListCard title={t('colleges.notes')} items={c.notes} /> : null}

          <InfoNote icon="help-circle">{t('colleges.entryRequirements')}</InfoNote>

          <Card style={styles.card}>
            <Overline>{t('colleges.sources')}</Overline>
            {c.sources.map((s) => (
              <View key={s.url} style={{ gap: 2 }}>
                <Muted>{s.title ?? s.publisher}</Muted>
                <SourceLink url={s.url} />
              </View>
            ))}
          </Card>
        </View>
      ) : null}
    </HeroScreen>
  );
}

function Fact({ label, value, onPress }: { label: string; value: string; onPress?: () => void }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const body = (
    <View style={styles.fact}>
      <Muted>{label}</Muted>
      <View style={styles.factValue}>
        <Text style={[styles.factText, onPress && styles.factLink]}>{value}</Text>
        {onPress ? <Feather name="external-link" size={13} color={colors.accentDeep} /> : null}
      </View>
    </View>
  );
  return onPress ? (
    <Pressable accessibilityRole="link" accessibilityLabel={`${label}: ${value}`} onPress={onPress} hitSlop={4}>
      {body}
    </Pressable>
  ) : (
    body
  );
}

function ListCard({ title, note, items }: { title: string; note?: string; items: string[] }) {
  const styles = useStyles(makeStyles);
  const [all, setAll] = useState(false);
  const shown = all ? items : items.slice(0, FIRST);
  return (
    <Card style={styles.card}>
      <Overline>{title}</Overline>
      {note ? <Muted>{note}</Muted> : null}
      {shown.map((item, i) => (
        <View key={i} style={styles.item}>
          <Text style={styles.bullet}>•</Text>
          <Text style={styles.itemText}>{item}</Text>
        </View>
      ))}
      {items.length > FIRST && !all ? (
        <Pressable accessibilityRole="button" onPress={() => setAll(true)} hitSlop={6}>
          <Text style={styles.more}>{t('colleges.showAll', { n: items.length })}</Text>
        </Pressable>
      ) : null}
    </Card>
  );
}

/** DHET's own warning signs of a bogus college, in its words, with its source. */
export function Signs({ signs }: { signs: WarningSigns }) {
  const styles = useStyles(makeStyles);
  return (
    <Card style={styles.card}>
      <Overline>{t('colleges.signsTitle')}</Overline>
      {signs.items.map((item, i) => (
        <View key={i} style={styles.item}>
          <Text style={styles.bullet}>•</Text>
          <Text style={styles.itemText}>{item}</Text>
        </View>
      ))}
      <SourceLink url={signs.source_url} />
    </Card>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
  card: { gap: 10, padding: 14 },
  line: { fontFamily: fonts.body, fontSize: 15, lineHeight: 21, color: colors.text },
  fact: { gap: 2, paddingVertical: 2 },
  factValue: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  factText: { fontFamily: fonts.semibold, fontSize: 15.5, color: colors.text },
  factLink: { color: colors.accentDeep, textDecorationLine: 'underline' },
  qual: { gap: 6, paddingTop: 8, borderTopWidth: 1, borderTopColor: colors.line },
  tags: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  item: { flexDirection: 'row', gap: 8 },
  bullet: { fontFamily: fonts.bold, fontSize: 15, lineHeight: 20, color: colors.accentDeep },
  itemText: { flex: 1, fontFamily: fonts.body, fontSize: 14.5, lineHeight: 20, color: colors.text },
  more: { fontFamily: fonts.semibold, fontSize: 14, color: colors.accentDeep },
});
