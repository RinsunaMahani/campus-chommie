import { useEffect, useState } from 'react';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { onSlowRequests } from '@/shared/api/client';
import { t } from '@/shared/i18n';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

/**
 * While any request is slow (the free server can take up to a minute to wake after a restart), a small pill at the
 * top says so, instead of the app looking stuck. It goes away by itself when the answer arrives.
 */
export function WakingBanner() {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const insets = useSafeAreaInsets();
  const [slow, setSlow] = useState(false);

  useEffect(() => onSlowRequests(setSlow), []);

  if (!slow) return null;
  return (
    <View pointerEvents="none" style={[styles.wrap, { top: insets.top + 8 }]}>
      <View style={styles.pill} accessibilityRole="alert" accessibilityLiveRegion="polite">
        <ActivityIndicator size="small" color={colors.pillText} />
        <Text style={styles.text}>{t('common.waking')}</Text>
      </View>
    </View>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    wrap: { position: 'absolute', left: 0, right: 0, alignItems: 'center', zIndex: 1000 },
    pill: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 8,
      paddingHorizontal: 14,
      paddingVertical: 8,
      borderRadius: radius.pill,
      backgroundColor: colors.accent,
    },
    text: { fontFamily: fonts.semibold, fontSize: 14, color: colors.pillText },
  });
