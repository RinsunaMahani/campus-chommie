/**
 * One verified test or deadline: its kind in words, when and where, what share
 * of the module, every change a rep confirmed, and a way to flag it. Reps also
 * see how many flagged it and why, never who.
 */
import { Feather } from '@expo/vector-icons';
import { useState } from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Button } from '@/shared/components/Button';
import { Card, Tag } from '@/shared/components/Parts';
import { Muted, Strong } from '@/shared/components/Text';
import { MessageKey, t } from '@/shared/i18n';
import { percent } from '@/shared/lib/dates';
import { fonts } from '@/shared/theme/tokens';

import { ClassEvent, FLAG_REASONS, FlagReason } from '../types';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';

export function kindLabel(kind: string): string {
  return t(`week.kind.${kind}` as MessageKey);
}

export function reasonLabel(reason: FlagReason): string {
  return t(`week.flagReason.${reason}` as MessageKey);
}

type Props = {
  event: ClassEvent;
  /** Flag it (a reason) or take the flag back (null). Without it, no flag button. */
  onFlag?: (reason: FlagReason | null) => void;
  busy?: boolean;
};

export function EventCard({ event, onFlag, busy }: Props) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const kind = kindLabel(event.kind);
  // 'Quiz 3' already says it's a quiz: 'Quiz: Quiz 3' would say it twice.
  const title = !event.title ? kind : event.title.toLowerCase().startsWith(kind.toLowerCase()) ? event.title : `${kind}: ${event.title}`;
  const flags = event.flags;
  return (
    <Card style={{ gap: 6, ...(event.cancelled ? { opacity: 0.75 } : {}) }}>
      <View style={styles.head}>
        <Strong style={{ flexShrink: 1 }}>{title}</Strong>
        {event.cancelled ? <Tag label={t('week.cancelled')} tone="garnet" /> : <Tag label={event.module} tone="info" />}
      </View>
      <Text style={[styles.when, event.cancelled && styles.struck]}>{event.when}</Text>
      {event.venue ? <Muted>{event.venue}</Muted> : null}
      {event.weighting != null ? <Muted>{t('week.weighting', { n: percent(event.weighting) })}</Muted> : null}
      {event.changes?.map((c, i) => (
        <Text key={i} style={styles.change}>
          {c.line}
        </Text>
      ))}
      {flags && flags.count > 0 ? (
        <Muted style={{ color: colors.marigoldDeep }}>
          {t('classes.flags', {
            n: flags.count,
            reasons: (Object.entries(flags.reasons) as [FlagReason, number][]).map(([r, n]) => `${reasonLabel(r)} (${n})`).join(', '),
          })}
        </Muted>
      ) : null}
      {onFlag ? (
        event.your_flag ? (
          <View style={{ gap: 6 }}>
            <Muted>{t('week.flagged', { reason: reasonLabel(event.your_flag) })}</Muted>
            <Button title={t('week.unflag')} variant="secondary" icon="rotate-ccw" onPress={() => onFlag(null)} loading={busy} />
          </View>
        ) : (
          <FlagButton onPick={onFlag} busy={busy} />
        )
      ) : null}
    </Card>
  );
}

/** "Something wrong?": a sheet of the six reasons. */
function FlagButton({ onPick, busy }: { onPick: (reason: FlagReason) => void; busy?: boolean }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const [open, setOpen] = useState(false);
  return (
    <>
      <Pressable accessibilityRole="button" onPress={() => setOpen(true)} disabled={busy} hitSlop={6} style={styles.flagLink}>
        <Feather name="flag" size={13} color={colors.textMuted} />
        <Text style={styles.flagText}>{t('week.flag')}</Text>
      </Pressable>
      <Modal visible={open} transparent animationType="fade" onRequestClose={() => setOpen(false)}>
        <View style={styles.backdrop}>
          <Pressable style={{ flex: 1 }} onPress={() => setOpen(false)} accessibilityLabel="Close" />
          <SafeAreaView edges={['bottom']} style={styles.sheet}>
            <View style={styles.handle} />
            <Text style={styles.sheetTitle}>{t('week.flagTitle')}</Text>
            <Text style={styles.sheetHint}>{t('week.flagHint')}</Text>
            {FLAG_REASONS.map((r, i) => (
              <Pressable
                key={r}
                accessibilityRole="button"
                onPress={() => {
                  setOpen(false);
                  onPick(r);
                }}
                style={[styles.option, i < FLAG_REASONS.length - 1 && styles.optionRule]}>
                <Text style={styles.optionText}>{reasonLabel(r)}</Text>
              </Pressable>
            ))}
          </SafeAreaView>
        </View>
      </Modal>
    </>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  head: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 8 },
  when: { fontFamily: fonts.semibold, fontSize: 14, color: colors.text },
  struck: { textDecorationLine: 'line-through', color: colors.textMuted },
  change: { fontFamily: fonts.medium, fontSize: 12.5, lineHeight: 18, color: colors.accentDeep },
  flagLink: { flexDirection: 'row', alignItems: 'center', gap: 6, alignSelf: 'flex-start', paddingTop: 4 },
  flagText: { fontFamily: fonts.semibold, fontSize: 12.5, color: colors.textMuted, textDecorationLine: 'underline' },
  backdrop: { flex: 1, backgroundColor: colors.overlay },
  sheet: { backgroundColor: colors.white, borderTopLeftRadius: 22, borderTopRightRadius: 22, paddingHorizontal: 20, paddingBottom: 14, gap: 4 },
  handle: { alignSelf: 'center', width: 40, height: 4, borderRadius: 2, backgroundColor: colors.line, marginTop: 10, marginBottom: 6 },
  sheetTitle: { fontFamily: fonts.display, fontSize: 20, color: colors.ink },
  sheetHint: { fontFamily: fonts.body, fontSize: 13, lineHeight: 18, color: colors.textMuted, marginBottom: 6 },
  option: { paddingVertical: 14 },
  optionRule: { borderBottomWidth: 1, borderBottomColor: colors.line },
  optionText: { fontFamily: fonts.semibold, fontSize: 15, color: colors.text },
});
