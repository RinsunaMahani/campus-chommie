import { Feather } from '@expo/vector-icons';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';

import { Button } from '@/shared/components/Button';
import { t } from '@/shared/i18n';
import { fonts, radius } from '@/shared/theme/tokens';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';

/** A spinner with words, so a slow phone never shows a blank screen. */
export function Loading({ label }: { label?: string }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  return (
    <View style={styles.loading} accessibilityLiveRegion="polite">
      <ActivityIndicator color={colors.ink} />
      <Text style={styles.loadingText}>{label ?? t('common.loading')}</Text>
    </View>
  );
}

/** What went wrong, and a way to try again when trying again can help. */
export function ErrorBox({ message, onRetry }: { message: string; onRetry?: () => void }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  return (
    <View style={styles.error} accessibilityRole="alert">
      <View style={styles.row}>
        <Feather name="alert-circle" size={16} color={colors.garnet} style={{ marginTop: 2 }} />
        <Text style={styles.errorText}>{message}</Text>
      </View>
      {onRetry ? <Button title={t('common.retry')} variant="secondary" icon="refresh-cw" onPress={onRetry} /> : null}
    </View>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  loading: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 16 },
  loadingText: { fontFamily: fonts.medium, fontSize: 15, color: colors.textMuted },
  error: { gap: 12, padding: 14, borderRadius: radius.md, backgroundColor: colors.garnetTint },
  row: { flexDirection: 'row', gap: 10 },
  errorText: { flex: 1, fontFamily: fonts.medium, fontSize: 15, lineHeight: 20, color: colors.text },
});
