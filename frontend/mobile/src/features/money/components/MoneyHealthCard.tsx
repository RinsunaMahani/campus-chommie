/**
 * Money health card: five simple checks the student can act on.
 * Displays "{done} of {total} done", each check with its words,
 * and tapping opens the screen that fixes it.
 * Strictly non-shaming: "Done" and "Not yet", never a score out of 100.
 */
import { Feather } from '@expo/vector-icons';
import { Href, router } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { Card, Tag } from '@/shared/components/Parts';
import { Overline, Strong } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius, space, type } from '@/shared/theme/tokens';

import { MoneyHealth } from '../types';

type Props = {
  health: MoneyHealth;
};

const ICONS: Record<string, 'clock' | 'shield' | 'trending-up' | 'target' | 'check-circle'> = {
  runway: 'clock',
  buffer: 'shield',
  spending: 'trending-up',
  goals: 'target',
  checkin: 'check-circle',
};

export function MoneyHealthCard({ health }: Props) {
  const styles = useStyles(makeStyles);
  const colors = usePalette();
  const { checks, done_count, total_count } = health;
  const allDone = done_count === total_count;
  const progressPercent = Math.min(100, Math.round((done_count / Math.max(1, total_count)) * 100));

  return (
    <Card style={styles.card}>
      <View style={styles.header}>
        <View style={styles.titleWrap}>
          <Overline>{t('money.health.title')}</Overline>
          <Strong style={styles.heading}>{t('money.health.done', { done: done_count, total: total_count })}</Strong>
        </View>
        <Tag
          label={allDone ? t('money.health.badgeDone') : `${done_count}/${total_count}`}
          tone={allDone ? 'jade' : 'marigold'}
        />
      </View>

      <View style={styles.track}>
        <View style={[styles.fill, { width: `${progressPercent}%` }]} />
      </View>

      <View style={styles.checksList}>
        {checks.map((c, index) => {
          const isDone = c.status === 'done';
          const isNotYet = c.status === 'not yet';
          const badgeTone = isDone ? ('jade' as const) : isNotYet ? ('marigold' as const) : ('muted' as const);
          const badgeLabel = isDone
            ? t('money.health.badgeDone')
            : isNotYet
              ? t('money.health.badgeNotYet')
              : t('money.health.badgeCantTell');

          const iconName = ICONS[c.id] ?? 'check-circle';

          return (
            <Pressable
              key={c.id}
              accessibilityRole="button"
              accessibilityLabel={`${c.title}: ${badgeLabel}. ${c.line}. ${c.action ?? ''}`}
              onPress={() => c.target && router.push(c.target as Href)}
              style={({ pressed }) => [
                styles.checkRow,
                index > 0 && styles.rule,
                pressed && styles.pressed,
              ]}>
              <View style={[styles.iconWrap, { backgroundColor: isDone ? colors.jadeTint : colors.iconTile }]}>
                <Feather
                  name={iconName}
                  size={16}
                  color={isDone ? colors.jade : colors.ink}
                />
              </View>

              <View style={styles.textWrap}>
                <View style={styles.checkTitleRow}>
                  <Text style={styles.checkTitle}>{c.title}</Text>
                  <Tag label={badgeLabel} tone={badgeTone} />
                </View>
                <Text style={styles.checkLine}>{c.line}</Text>
                {c.action ? (
                  <View style={styles.actionRow}>
                    <Text style={styles.actionText}>{c.action}</Text>
                    <Feather name="arrow-right" size={13} color={colors.accentDeep} />
                  </View>
                ) : null}
              </View>
            </Pressable>
          );
        })}
      </View>
    </Card>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    card: {
      gap: space.md,
      padding: space.md,
    },
    header: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    titleWrap: {
      gap: 2,
    },
    heading: {
      ...type.headline,
      color: colors.ink,
    },
    track: {
      height: 6,
      borderRadius: radius.pill,
      backgroundColor: colors.iconTile,
      overflow: 'hidden',
    },
    fill: {
      height: 6,
      borderRadius: radius.pill,
      backgroundColor: colors.accentDeep,
    },
    checksList: {
      gap: space.xs,
    },
    checkRow: {
      flexDirection: 'row',
      alignItems: 'flex-start',
      gap: space.md,
      paddingVertical: space.sm,
    },
    rule: {
      borderTopWidth: 1,
      borderTopColor: colors.line,
    },
    pressed: {
      opacity: 0.8,
    },
    iconWrap: {
      width: 32,
      height: 32,
      borderRadius: radius.sm,
      alignItems: 'center',
      justifyContent: 'center',
      marginTop: 2,
    },
    textWrap: {
      flex: 1,
      gap: 4,
    },
    checkTitleRow: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: space.xs,
      flexWrap: 'wrap',
    },
    checkTitle: {
      fontFamily: fonts.bold,
      ...type.callout,
      color: colors.ink,
      flexShrink: 1,
    },
    checkLine: {
      fontFamily: fonts.medium,
      fontSize: 13,
      lineHeight: 18,
      color: colors.textMuted,
    },
    actionRow: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 4,
      marginTop: 2,
    },
    actionText: {
      fontFamily: fonts.bold,
      fontSize: 13,
      color: colors.accentDeep,
    },
  });

