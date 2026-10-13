import { router } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { Button } from '@/shared/components/Button';
import { InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { Body, Overline, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { colors, fonts } from '@/shared/theme/tokens';

/**
 * Onboarding, step 1: the privacy notice in plain words. Consent and the
 * 18-or-older confirmation were recorded at sign-up; this says what that means.
 */
export default function PrivacyNoticeScreen() {
  return (
    <Screen footer={<Button title={t('onboarding.continue')} variant="accent" onPress={() => router.push('/onboarding/campus')} />}>
      <View style={{ gap: 6 }}>
        <Overline>{t('onboarding.step', { n: 1 })}</Overline>
        <Title>{t('onboarding.privacyTitle')}</Title>
        <Body>{t('onboarding.privacyIntro')}</Body>
      </View>
      <InfoNote icon="lock">{t('onboarding.privacyKeep')}</InfoNote>
      <InfoNote icon="slash">{t('onboarding.privacyNever')}</InfoNote>
      <Pressable accessibilityRole="link" onPress={() => router.push('/privacy-policy')} hitSlop={8}>
        <Text style={styles.link}>{t('onboarding.privacyRead')}</Text>
      </Pressable>
    </Screen>
  );
}

const styles = StyleSheet.create({
  link: { fontFamily: fonts.bold, fontSize: 14, color: colors.accentDeep, textDecorationLine: 'underline' },
});
