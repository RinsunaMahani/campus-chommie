/**
 * One university, as a short overview: its campus photo, your points there (once your marks are in), its
 * application fee and where applications stand today, then two clear ways on: Courses (by faculty, on their
 * own screen) and How to apply (on its own screen). Works without marks too.
 */
import { Feather } from '@expo/vector-icons';
import { router, useLocalSearchParams } from 'expo-router';
import { ComponentProps, useEffect, useMemo, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { BandChip, HeroScreen } from '@/shared/components/HeroScreen';
import { Card, Tag } from '@/shared/components/Parts';
import { ErrorBox } from '@/shared/components/Status';
import { Muted, Overline, Strong } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { SkeletonCards } from '@/shared/motion/Shimmer';
import { colors, fonts, radius } from '@/shared/theme/tokens';

import { courseFinderApi } from '../api/courseFinderApi';
import { ApsCard } from '../components/ApsCard';
import { CampusPhotoCard } from '../components/CampusPhotoCard';
import { feeLabel, statusTone } from '../components/UniversityCard';
import { checkRows } from '../marks';
import { useCourseFinder } from '../state';
import { ApplyInfoAnswer } from '../types';
import { errorText } from '../words';

export default function UniversityScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const cf = useCourseFinder();
  const sent = useMemo(() => checkRows(cf.rows), [cf.rows]);
  const points = cf.points?.universities.find((u) => u.university === id) ?? null;
  const [info, setInfo] = useState<ApplyInfoAnswer | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (!id) return;
    courseFinderApi
      .applyInfo(id)
      .then(setInfo)
      .catch((e) => setError(errorText(e)));
  }, [id, attempt]);

  const uni = info?.university;
  const guide = info?.apply.guide;
  const window = guide?.windows[0] ?? null;

  return (
    <HeroScreen
      back
      title={uni?.name ?? points?.university_name ?? ''}
      subtitle={uni?.city ?? undefined}
      band={uni && !uni.confirmed && uni.notice ? <BandChip label={uni.notice} /> : null}>
      {id ? <CampusPhotoCard university={id} /> : null}
      {points ? <ApsCard points={points} sent={sent} rows={cf.rows} /> : null}

      {error ? (
        <ErrorBox
          message={error}
          onRetry={() => {
            setError(null);
            setAttempt((n) => n + 1);
          }}
        />
      ) : null}
      {!info && !error ? <SkeletonCards count={2} /> : null}

      {info && guide ? (
        <Card style={styles.card}>
          <Overline>{t('university.glance')}</Overline>
          <View style={styles.row}>
            <Muted style={{ flex: 1 }}>{t('university.fee')}</Muted>
            <Tag label={feeLabel(guide.fee_cents)} tone={guide.fee_cents === 0 ? 'jade' : 'muted'} />
          </View>
          {window ? (
            <View style={{ gap: 6 }}>
              <View style={styles.row}>
                <Muted style={{ flex: 1 }}>{window.heading}</Muted>
                <Tag label={window.label} tone={statusTone(window.status)} />
              </View>
              {window.lines[0] ? <Text style={styles.line}>{window.lines[0]}</Text> : null}
            </View>
          ) : null}
        </Card>
      ) : null}

      {id ? (
        <View style={{ gap: 10 }}>
          <BigLink
            icon="book-open"
            title={t('university.courses')}
            sub={t('university.coursesSub', { n: uni?.programmes ?? '…' })}
            onPress={() => router.push(`/course-finder/university/${id}/courses`)}
          />
          <BigLink
            icon="send"
            title={t('university.apply')}
            sub={t('university.applySub')}
            onPress={() => router.push(`/course-finder/university/${id}/apply`)}
          />
        </View>
      ) : null}
    </HeroScreen>
  );
}

function BigLink({ icon, title, sub, onPress }: { icon: ComponentProps<typeof Feather>['name']; title: string; sub: string; onPress: () => void }) {
  return (
    <Card onPress={onPress} style={styles.link}>
      <View style={styles.icon}>
        <Feather name={icon} size={20} color={colors.ink} />
      </View>
      <View style={{ flex: 1, gap: 2 }}>
        <Strong style={styles.linkTitle}>{title}</Strong>
        <Muted>{sub}</Muted>
      </View>
      <Feather name="chevron-right" size={18} color={colors.accentDeep} />
    </Card>
  );
}

const styles = StyleSheet.create({
  card: { gap: 12, padding: 16 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  line: { fontFamily: fonts.body, fontSize: 13.5, lineHeight: 20, color: colors.text },
  link: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 16 },
  icon: {
    width: 42,
    height: 42,
    borderRadius: radius.sm,
    backgroundColor: colors.iconTile,
    alignItems: 'center',
    justifyContent: 'center',
  },
  linkTitle: { fontSize: 16, color: colors.text },
});
