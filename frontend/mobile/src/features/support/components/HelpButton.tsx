/**
 * The Help button at the top of every student screen: one tap to campus support and crisis lines, wherever the
 * student is (student mental-health studies: crisis help must be findable at once, never hidden). Crisis numbers
 * show on Support only once a person has checked them.
 */
import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { Pressable, StyleSheet, Text } from 'react-native';

import { t } from '@/shared/i18n';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

export function HelpButton() {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  return (
    <Pressable accessibilityRole="button" accessibilityLabel={t('help.label')} onPress={() => router.push('/support')} hitSlop={8} style={styles.pill}>
      <Feather name="life-buoy" size={16} color={colors.garnet} />
      <Text style={styles.text}>{t('help.button')}</Text>
    </Pressable>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    pill: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 6,
      minHeight: 36,
      paddingHorizontal: 12,
      borderRadius: radius.pill,
      borderWidth: 1,
      borderColor: colors.garnet,
      backgroundColor: colors.garnetTint,
    },
    text: { fontFamily: fonts.bold, fontSize: 14, color: colors.garnet },
  });
