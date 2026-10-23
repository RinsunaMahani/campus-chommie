import * as Linking from 'expo-linking';
import { useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Button } from '@/shared/components/Button';
import { Card, InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Body, Muted, Overline, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { formatDay } from '@/shared/lib/dates';
import { Palette, useStyles } from '@/shared/theme/palette';
import { fonts } from '@/shared/theme/tokens';

import { whatsappApi } from '../api/whatsappApi';
import { LinkCode, WhatsAppStatus } from '../types';

/**
 * Home -> WhatsApp: link this account's WhatsApp number to the bot with a one-time code (the button opens
 * WhatsApp with the message already typed), see whether a number is linked, and unlink. What the bot does is
 * said plainly, and that it never asks for passwords or bank details. Off until the bot is switched on.
 */
export default function WhatsAppScreen() {
  const styles = useStyles(makeStyles);
  const [status, setStatus] = useState<WhatsAppStatus | null>(null);
  const [code, setCode] = useState<LinkCode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(() => {
    whatsappApi
      .status()
      .then((s) => {
        setStatus(s);
        setError(null);
      })
      .catch((e) => setError(errorText(e, t('common.error'))));
  }, []);
  useFocusEffect(load);

  async function getCode() {
    setBusy(true);
    try {
      setCode(await whatsappApi.code());
      setError(null);
    } catch (e) {
      setError(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  async function unlink() {
    setBusy(true);
    try {
      await whatsappApi.unlink();
      setCode(null);
      load();
    } catch (e) {
      setError(errorText(e, t('common.error')));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Screen back>
      <Title>{t('whatsapp.title')}</Title>
      {error ? <ErrorBox message={error} onRetry={load} /> : null}
      {!error && !status ? <Loading /> : null}

      {status && !status.available ? <InfoNote icon="clock">{t('whatsapp.off')}</InfoNote> : null}

      {status?.available ? (
        <>
          <Body>{t('whatsapp.intro')}</Body>
          <Card>
            <Overline>{t('whatsapp.whatItDoes')}</Overline>
            <Body>{t('whatsapp.reps')}</Body>
            <Body>{t('whatsapp.week')}</Body>
            <Body>{t('whatsapp.stop')}</Body>
          </Card>

          {status.linked > 0 ? (
            <InfoNote icon="check-circle" tone="ok">
              {t('whatsapp.linked', { day: formatDay(status.linked_on[status.linked_on.length - 1]) })}
            </InfoNote>
          ) : null}

          {code ? (
            <Card>
              <Overline>{t('whatsapp.yourCode')}</Overline>
              <Text selectable style={styles.code} accessibilityLabel={code.code.split('').join(' ')}>
                {code.code}
              </Text>
              <Muted>{t('whatsapp.codeSteps', { message: code.message, number: code.bot.number ?? '', minutes: code.minutes })}</Muted>
              {code.send_link ? (
                <Button title={t('whatsapp.openWhatsApp')} icon="message-circle" onPress={() => Linking.openURL(code.send_link!)} />
              ) : null}
            </Card>
          ) : (
            <Button
              title={status.linked > 0 ? t('whatsapp.linkAnother') : t('whatsapp.link')}
              icon="link"
              loading={busy}
              onPress={getCode}
            />
          )}

          {status.linked > 0 ? <Button title={t('whatsapp.unlink')} variant="secondary" icon="x" disabled={busy} onPress={unlink} /> : null}

          <InfoNote icon="shield">{t('whatsapp.privacy')}</InfoNote>
        </>
      ) : null}
      <View style={{ height: 8 }} />
    </Screen>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    code: { fontFamily: fonts.bold, fontSize: 30, letterSpacing: 3, color: colors.ink, marginVertical: 8 },
  });
