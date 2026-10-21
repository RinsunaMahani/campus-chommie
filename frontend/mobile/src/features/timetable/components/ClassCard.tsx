/**
 * One class in the timetable: its module in its own colour (a bar on the left and the code), what kind of
 * class, when and where, and a coral "Clashes" tag when it overlaps another. Tapping opens it to change.
 */
import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { StyleSheet, Text, View } from 'react-native';

import { Card, Tag } from '@/shared/components/Parts';
import { t } from '@/shared/i18n';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import { moduleColour } from '../colours';
import { TimetableEntry } from '../types';

export function ClassCard({ entry }: { entry: TimetableEntry }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const colour = moduleColour(colors, entry.module);
  return (
    <Card onPress={() => router.push(`/timetable/${entry.id}`)} style={styles.card}>
      <View style={[styles.bar, { backgroundColor: colour }]} />
      <View style={styles.body}>
        <View style={styles.head}>
          <Text style={[styles.module, { color: colour }]}>{entry.module}</Text>
          <Text style={styles.kind}>{t(`timetable.kind.${entry.kind}`)}</Text>
          {entry.clashes ? <Tag label={t('timetable.clashes')} tone="garnet" /> : null}
        </View>
        {entry.title ? <Text style={styles.title}>{entry.title}</Text> : null}
        <View style={styles.meta}>
          <Feather name="clock" size={13} color={colors.textMuted} />
          <Text style={styles.metaText}>
            {entry.starts} to {entry.ends}
          </Text>
          {entry.venue ? (
            <>
              <Feather name="map-pin" size={13} color={colors.textMuted} />
              <Text style={styles.metaText} numberOfLines={1}>
                {entry.venue}
              </Text>
            </>
          ) : null}
        </View>
      </View>
    </Card>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    card: { flexDirection: 'row', padding: 0, overflow: 'hidden' },
    bar: { width: 5, borderTopLeftRadius: radius.lg, borderBottomLeftRadius: radius.lg },
    body: { flex: 1, gap: 4, padding: 12 },
    head: { flexDirection: 'row', alignItems: 'center', gap: 8, flexWrap: 'wrap' },
    module: { fontFamily: fonts.bold, fontSize: 15 },
    kind: { fontFamily: fonts.medium, fontSize: 13, color: colors.textMuted },
    title: { fontFamily: fonts.medium, fontSize: 13.5, color: colors.text },
    meta: { flexDirection: 'row', alignItems: 'center', gap: 6 },
    metaText: { flexShrink: 1, fontFamily: fonts.medium, fontSize: 13, color: colors.textMuted },
  });
