/**
 * A university in Explore: its campus photo (or its text monogram where we have no logo-free photo), name
 * and city, what it costs to apply, and where its applications stand today. Tapping opens the university.
 */
import { router } from 'expo-router';
import { Image, StyleSheet, Text, View } from 'react-native';

import { UniMonogram } from '@/shared/components/UniMonogram';
import { Card, Tag } from '@/shared/components/Parts';
import { Muted } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { formatRand } from '@/shared/lib/money';
import { colors, fonts } from '@/shared/theme/tokens';

import { CAMPUS_PHOTOS } from '../campusPhotos';
import { UniversityCardInfo } from '../types';

export function feeLabel(cents: number | null): string {
  if (cents == null) return t('explore.feeUnknown');
  return cents === 0 ? t('explore.free') : t('explore.fee', { fee: formatRand(cents) });
}

export function statusTone(status: string | undefined) {
  if (status === 'open' || status === 'late_open') return 'jade' as const;
  if (status === 'closing_soon' || status === 'check') return 'marigold' as const;
  return 'muted' as const;
}

export function UniversityCard({ u }: { u: UniversityCardInfo }) {
  const photo = CAMPUS_PHOTOS[u.id];
  return (
    <Card onPress={() => router.push(`/course-finder/university/${u.id}`)} style={styles.card}>
      {photo ? (
        <Image source={photo.image} style={styles.photo} resizeMode="cover" accessibilityIgnoresInvertColors accessible={false} />
      ) : null}
      <View style={styles.body}>
        <View style={styles.head}>
          {photo ? null : <UniMonogram id={u.id} size={42} />}
          <View style={{ flex: 1 }}>
            <Text style={styles.name}>{u.name}</Text>
            {u.city ? <Muted>{u.city}</Muted> : null}
          </View>
        </View>
        <View style={styles.tags}>
          <Tag label={feeLabel(u.fee_cents)} tone={u.fee_cents === 0 ? 'jade' : 'muted'} />
          {u.applications ? <Tag label={u.applications.label} tone={statusTone(u.applications.status)} /> : null}
        </View>
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: { padding: 0, overflow: 'hidden' },
  photo: { width: '100%', aspectRatio: 16 / 9 },
  body: { gap: 10, padding: 14 },
  head: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  name: { fontFamily: fonts.bold, fontSize: 15.5, lineHeight: 21, color: colors.text },
  tags: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
});
