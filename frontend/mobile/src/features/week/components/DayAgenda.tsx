/**
 * One day as a list, in time order: classes (in their module colour), tests and deadlines, exams and the
 * student's own plans, each tappable to where it's kept. Empty, it says so and offers to add a plan.
 */
import { router } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { moduleColour } from '@/features/timetable/colours';
import { Button } from '@/shared/components/Button';
import { t } from '@/shared/i18n';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius, space } from '@/shared/theme/tokens';

import { DayItem, itemsOn, Sources } from '../calendarDays';

function label(it: DayItem): { title: string; sub: string; time: string } {
  switch (it.type) {
    case 'class':
      return { title: it.entry.module, sub: t(`timetable.kind.${it.entry.kind}`) + (it.entry.venue ? ` · ${it.entry.venue}` : ''), time: `${it.at}–${it.ends}` };
    case 'event':
      return { title: `${it.event.module} ${it.event.title ?? t(`week.kind.${it.event.kind}`)}`, sub: it.event.weighting ? t('week.worth', { n: it.event.weighting }) : t(`week.kind.${it.event.kind}`), time: it.at ?? t('week.dueLabel') };
    case 'exam':
      return { title: `${it.exam.module} ${t('timetable.exam')}`, sub: it.exam.paper ?? '', time: it.at };
    case 'plan':
      return { title: it.plan.title, sub: t(`activity.kind.${it.plan.kind}`) + (it.plan.place ? ` · ${it.plan.place}` : ''), time: `${it.at}–${it.ends}` };
  }
}

export function DayAgenda({ date, sources }: { date: string; sources: Sources }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const items = itemsOn(date, sources);
  const colourOf = (it: DayItem) =>
    it.type === 'class' ? moduleColour(colors, it.entry.module)
      : it.type === 'plan' ? colors.classColours[4]
        : it.type === 'exam' || (it.type === 'event' && it.event.kind !== 'assignment') ? colors.garnet
          : colors.marigold;
  const open = (it: DayItem) => {
    if (it.type === 'class') router.push({ pathname: '/timetable/[id]', params: { id: it.entry.id } });
    else if (it.type === 'plan') router.push({ pathname: '/activity/[id]', params: { id: it.plan.id } });
    else if (it.type === 'exam') router.push('/timetable');
    else router.push('/classes');
  };
  if (!items.length) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>{sources.off.has(date) ? t('week.recessDay') : t('week.nothing')}</Text>
        <Button title={t('activity.add')} variant="secondary" icon="plus" compact onPress={() => router.push({ pathname: '/activity/[id]', params: { id: 'new' } })} />
      </View>
    );
  }
  return (
    <View style={{ gap: space.sm }}>
      {items.map((it, i) => {
        const l = label(it);
        const c = colourOf(it);
        return (
          <Pressable key={i} accessibilityRole="button" accessibilityLabel={`${l.time} ${l.title}, ${l.sub}`} onPress={() => open(it)} style={[styles.item, { borderLeftColor: c }, it.type === 'plan' && styles.plan]}>
            <Text style={styles.time}>{l.time}</Text>
            <View style={{ flex: 1, gap: 2 }}>
              <Text style={[styles.title, { color: c }]} numberOfLines={1}>
                {l.title}
              </Text>
              {l.sub ? (
                <Text style={styles.sub} numberOfLines={1}>
                  {l.sub}
                </Text>
              ) : null}
            </View>
          </Pressable>
        );
      })}
    </View>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    item: { flexDirection: 'row', alignItems: 'center', gap: space.md, padding: space.md, borderRadius: radius.md, borderLeftWidth: 4, backgroundColor: colors.white },
    plan: { borderStyle: 'dashed', borderWidth: 1, borderColor: colors.classColours[4] },
    time: { width: 92, fontFamily: fonts.bold, fontSize: 14, color: colors.ink, fontVariant: ['tabular-nums'] },
    title: { fontFamily: fonts.bold, fontSize: 15 },
    sub: { fontFamily: fonts.medium, fontSize: 13, color: colors.textMuted },
    empty: { gap: space.sm, alignItems: 'flex-start', paddingVertical: space.sm },
    emptyText: { fontFamily: fonts.medium, fontSize: 15, color: colors.textMuted },
  });
