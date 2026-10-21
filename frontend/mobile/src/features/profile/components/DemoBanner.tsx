import { Feather } from '@expo/vector-icons';
import { StyleSheet, Text, View } from 'react-native';

import { t } from '@/shared/i18n';
import { colors, fonts, radius } from '@/shared/theme/tokens';

import { useProfile } from '../state';

/** On a judge's demo account, every screen with its data says the data is fictional (CLAUDE.md). */
export function DemoBanner() {
  const { demo } = useProfile();
  if (!demo) return null;
  return (
    <View style={styles.banner} accessibilityRole="text">
      <Feather name="info" size={14} color={colors.marigoldDeep} />
      <Text style={styles.text}>{t('common.demoBanner')}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    alignSelf: 'flex-start',
    backgroundColor: colors.marigoldTint,
    borderRadius: radius.pill,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  text: { fontFamily: fonts.bold, fontSize: 12.5, color: colors.marigoldDeep },
});
