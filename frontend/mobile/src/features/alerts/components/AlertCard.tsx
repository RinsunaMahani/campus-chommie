/**
 * One of today's alerts (brief, M5): its title and message, then each action
 * in the server's words with a way to act on it: open the week, money, cheap
 * things, marks or support. A support action may already carry the campus's
 * own service, so the student sees who to call without another tap.
 */
import { Feather } from '@expo/vector-icons';
import { ComponentProps } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { Card } from '@/shared/components/Parts';
import { Muted, Strong } from '@/shared/components/Text';
import { MessageKey, t } from '@/shared/i18n';
import { fonts, radius } from '@/shared/theme/tokens';

import { ActionTarget, Alert } from '../types';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';

type IconName = ComponentProps<typeof Feather>['name'];

const ICON: Record<string, IconName> = {
  combined: 'alert-triangle',
  heavy_week: 'calendar',
  money: 'credit-card',
  module: 'award',
};

export function AlertCard({ alert, onOpen }: { alert: Alert; onOpen: (target: ActionTarget) => void }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  return (
    <Card style={styles.card}>
      <View style={styles.head}>
        <View style={styles.icon}>
          <Feather name={ICON[alert.kind] ?? 'bell'} size={16} color={colors.marigoldDeep} />
        </View>
        <Strong style={{ flex: 1 }}>{alert.title}</Strong>
      </View>
      <Text style={styles.message}>{alert.message}</Text>
      {alert.actions.map((a, i) => (
        <View key={i} style={styles.action}>
          <Text style={styles.actionText}>{a.text}</Text>
          {a.service ? (
            <View style={styles.service}>
              <Text style={styles.serviceName}>{a.service.name}</Text>
              {a.service.contact ? (
                <Text selectable style={styles.contact}>
                  {a.service.contact}
                </Text>
              ) : null}
              {a.service.hours ? <Muted>{t('support.hours', { hours: a.service.hours })}</Muted> : null}
            </View>
          ) : null}
          <Pressable accessibilityRole="link" onPress={() => onOpen(a.target)} hitSlop={6} style={styles.link}>
            <Text style={styles.linkText}>{t(`alerts.open.${a.target}` as MessageKey)}</Text>
            <Feather name="arrow-right" size={14} color={colors.accentDeep} />
          </Pressable>
        </View>
      ))}
    </Card>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  card: { gap: 10, borderColor: colors.marigold },
  head: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  icon: { width: 30, height: 30, borderRadius: radius.sm, backgroundColor: colors.marigoldTint, alignItems: 'center', justifyContent: 'center' },
  message: { fontFamily: fonts.body, fontSize: 15, lineHeight: 21, color: colors.text },
  action: { gap: 6, paddingTop: 10, borderTopWidth: 1, borderTopColor: colors.line },
  actionText: { fontFamily: fonts.medium, fontSize: 14.5, lineHeight: 20, color: colors.text },
  service: { gap: 2, padding: 10, borderRadius: radius.sm, backgroundColor: colors.iconTile },
  serviceName: { fontFamily: fonts.semibold, fontSize: 14, lineHeight: 18, color: colors.ink },
  contact: { fontFamily: fonts.bold, fontSize: 14.5, color: colors.ink },
  link: { flexDirection: 'row', alignItems: 'center', gap: 6, alignSelf: 'flex-start' },
  linkText: { fontFamily: fonts.bold, fontSize: 14.5, color: colors.accentDeep },
});
