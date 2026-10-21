/**
 * One of today's alerts (brief, M5): its title and message, always shown; a tap
 * opens what to do, each action in the server's words with a way to act on it:
 * open the week, money, cheap things, marks or support. A support action may
 * already carry the campus's own service, so the student sees who to call.
 * Closed by default so Home reads at a glance (progressive disclosure).
 */
import { Feather } from '@expo/vector-icons';
import { ComponentProps, useState } from 'react';
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
  const [open, setOpen] = useState(false);
  return (
    <Card style={styles.card}>
      <Pressable
        accessibilityRole="button"
        accessibilityState={{ expanded: open }}
        onPress={() => setOpen((o) => !o)}
        style={{ gap: 8 }}>
        <View style={styles.head}>
          <View style={styles.icon}>
            <Feather name={ICON[alert.kind] ?? 'bell'} size={16} color={colors.marigoldDeep} />
          </View>
          <Strong style={{ flex: 1 }}>{alert.title}</Strong>
          <Feather name={open ? 'chevron-up' : 'chevron-down'} size={20} color={colors.textMuted} />
        </View>
        <Text style={styles.message}>{alert.message}</Text>
        {!open && alert.actions.length ? (
          <Text style={styles.more}>{t('alerts.whatToDo', { n: alert.actions.length })}</Text>
        ) : null}
      </Pressable>
      {(open ? alert.actions : []).map((a, i) => (
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
  message: { fontFamily: fonts.body, fontSize: 16, lineHeight: 23, color: colors.text },
  more: { fontFamily: fonts.bold, fontSize: 14, color: colors.accentDeep },
  action: { gap: 6, paddingTop: 10, borderTopWidth: 1, borderTopColor: colors.line },
  actionText: { fontFamily: fonts.medium, fontSize: 14.5, lineHeight: 20, color: colors.text },
  service: { gap: 2, padding: 10, borderRadius: radius.sm, backgroundColor: colors.iconTile },
  serviceName: { fontFamily: fonts.semibold, fontSize: 14, lineHeight: 18, color: colors.ink },
  contact: { fontFamily: fonts.bold, fontSize: 14.5, color: colors.ink },
  link: { flexDirection: 'row', alignItems: 'center', gap: 6, alignSelf: 'flex-start' },
  linkText: { fontFamily: fonts.bold, fontSize: 14.5, color: colors.accentDeep },
});
