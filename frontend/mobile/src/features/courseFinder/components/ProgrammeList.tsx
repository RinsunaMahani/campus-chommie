/**
 * Programmes without marks, the way our course finder shows them with marks: one university's programmes
 * grouped by the faculty that offers them (with the faculty's photo and count), each with its minimum
 * points as the university publishes them. Across universities (a search), grouped by university first.
 * Tapping a programme opens its university.
 */
import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { StyleSheet, Text, View } from 'react-native';

import { Card, Tag } from '@/shared/components/Parts';
import { Overline } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { FadeIn } from '@/shared/motion/FadeIn';
import { colors, fonts } from '@/shared/theme/tokens';

import { Art, artOfFields } from '../faculties';
import { ProgrammeRow } from '../types';
import { FacultySection } from './FacultySection';

type Faculty = { faculty: string | null; art: Art; rows: ProgrammeRow[] };

/** Faculties in the order the server sends them (A to Z, unnamed last). */
export function byFaculty(rows: ProgrammeRow[]): Faculty[] {
  const groups = new Map<string | null, ProgrammeRow[]>();
  for (const r of rows) {
    const list = groups.get(r.faculty) ?? [];
    list.push(r);
    groups.set(r.faculty, list);
  }
  return [...groups.entries()].map(([faculty, list]) => ({ faculty, rows: list, art: artOfFields(list.flatMap((r) => r.fields)) }));
}

function countLine(n: number): string {
  return n === 1 ? t('courseFinder.facultyCountOne') : t('courseFinder.facultyCount', { n });
}

export function ProgrammeCard({ row }: { row: ProgrammeRow }) {
  const points = !row.verified
    ? t('courses.notVerified')
    : row.min_points != null
      ? t('courses.minPoints', { n: row.min_points })
      : t('courses.noMinPoints');
  return (
    <Card onPress={() => router.push(`/course-finder/university/${row.university}`)} style={styles.card}>
      <Text style={styles.name}>{row.name}</Text>
      <View style={styles.tags}>
        <Tag label={points} tone={row.verified && row.min_points != null ? 'jade' : 'muted'} />
        {row.selective ? <Tag label={t('courses.selective')} tone="marigold" /> : null}
      </View>
    </Card>
  );
}

/** One university's programmes, by faculty. */
export function FacultyProgrammes({ rows }: { rows: ProgrammeRow[] }) {
  return (
    <View style={{ gap: 12 }}>
      {byFaculty(rows).map((g, i) => (
        <FadeIn key={g.faculty ?? '-'} delay={Math.min(i, 6) * 40}>
          <FacultySection group={g} counts={countLine(g.rows.length)} startOpen={i === 0}>
            {g.rows.map((r) => (
              <ProgrammeCard key={r.programme} row={r} />
            ))}
          </FacultySection>
        </FadeIn>
      ))}
    </View>
  );
}

/** A search across universities: each university's matches under its name. */
export function SearchResults({ rows }: { rows: ProgrammeRow[] }) {
  const byUni = new Map<string, ProgrammeRow[]>();
  for (const r of rows) byUni.set(r.university_name, [...(byUni.get(r.university_name) ?? []), r]);
  return (
    <View style={{ gap: 16 }}>
      {[...byUni.entries()].map(([name, list]) => (
        <View key={name} style={{ gap: 8 }}>
          <View style={styles.uniHead}>
            <Overline>{name}</Overline>
            <Feather name="chevron-right" size={14} color={colors.textMuted} />
          </View>
          {list.map((r) => (
            <View key={r.programme} style={{ gap: 4 }}>
              {r.faculty ? <Text style={styles.faculty}>{r.faculty}</Text> : null}
              <ProgrammeCard row={r} />
            </View>
          ))}
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  card: { gap: 8, padding: 14 },
  name: { fontFamily: fonts.semibold, fontSize: 14.5, lineHeight: 20, color: colors.text },
  tags: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  uniHead: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  faculty: { fontFamily: fonts.medium, fontSize: 12, color: colors.textMuted },
});
