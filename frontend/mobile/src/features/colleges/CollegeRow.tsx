/**
 * One college in a list: its name, what kind it is and where, its status as a coloured tag (mint for
 * public and registered, amber for provisional, coral for cancelled or bogus), and the first line of
 * its status in words. Tapping opens the college.
 */
import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { ComponentProps } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { Card, Tag } from '@/shared/components/Parts';
import { Muted, Strong } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { colors, fonts } from '@/shared/theme/tokens';

import { CollegeCard, Verdict } from './types';

type Tone = NonNullable<ComponentProps<typeof Tag>['tone']>;

export function statusTone(status: Verdict): Tone {
  if (status === 'public' || status === 'registered') return 'jade';
  if (status === 'provisionally_registered' || status === 'several') return 'marigold';
  if (status === 'not_found') return 'muted';
  return 'garnet';
}

export function CollegeRow({ college }: { college: CollegeCard }) {
  const where = college.provinces.join(', ');
  return (
    <Card onPress={() => router.push(`/course-finder/colleges/${college.id}`)} style={styles.card}>
      <View style={styles.head}>
        <Strong style={styles.name} accessibilityLabel={t('colleges.open', { name: college.name })}>
          {college.name}
        </Strong>
        <Tag label={college.label} tone={statusTone(college.status)} />
      </View>
      <Muted>{where ? `${college.kind_label} · ${where}` : college.kind_label}</Muted>
      {college.lines[0] ? (
        <Text style={styles.line} numberOfLines={3}>
          {college.lines[0]}
        </Text>
      ) : null}
      <View style={styles.tap}>
        <Feather name="chevron-right" size={16} color={colors.accentDeep} />
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: { gap: 6, padding: 14 },
  head: { flexDirection: 'row', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8 },
  name: { flex: 1, fontSize: 15.5, color: colors.text },
  line: { fontFamily: fonts.body, fontSize: 14, lineHeight: 19, color: colors.textMuted },
  tap: { position: 'absolute', right: 10, bottom: 10 },
});
