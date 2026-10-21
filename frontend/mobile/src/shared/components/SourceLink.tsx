import { Feather } from '@expo/vector-icons';
import * as WebBrowser from 'expo-web-browser';
import { Pressable, StyleSheet, Text } from 'react-native';

import { t } from '@/shared/i18n';
import { colors, fonts } from '@/shared/theme/tokens';

/** "smu.ac.za" from "https://www.smu.ac.za/students/apply/". */
export function host(url: string): string {
  const match = /^https?:\/\/([^/?#]+)/i.exec(url);
  return match ? match[1].replace(/^www\./i, '') : url;
}

/** Where a fact comes from: the official page, opened in the browser. Never a blank when nobody has checked it. */
export function SourceLink({ url }: { url: string | null }) {
  if (!url) return <Text style={styles.none}>{t('courseFinder.noSource')}</Text>;
  const label = `${t('courseFinder.source')}: ${host(url)}`;
  return (
    <Pressable accessibilityRole="link" accessibilityLabel={label} onPress={() => WebBrowser.openBrowserAsync(url)} hitSlop={6} style={styles.row}>
      <Feather name="external-link" size={13} color={colors.accentDeep} />
      <Text style={styles.link} numberOfLines={1}>
        {label}
      </Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', gap: 6, alignSelf: 'flex-start' },
  link: { fontFamily: fonts.semibold, fontSize: 12.5, color: colors.accentDeep, textDecorationLine: 'underline' },
  none: { fontFamily: fonts.medium, fontSize: 12.5, color: colors.textMuted },
});
