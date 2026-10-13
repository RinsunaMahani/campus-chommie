/**
 * The class rep's tools (brief, M4): messages waiting to be checked, pasting a
 * class message, and a one-time code for the next rep (shown once: only its hash
 * is kept). Members are never listed, so reps bring in the next rep by code.
 */
import { View } from 'react-native';

import { Button } from '@/shared/components/Button';
import { Card, InfoNote } from '@/shared/components/Parts';
import { Muted, Overline, Strong } from '@/shared/components/Text';
import { t } from '@/shared/i18n';

import { RepCode } from '../types';

type Props = {
  waiting: number;
  onCheck: () => void;
  onAnnounce: () => void;
  repCode: RepCode | null;
  onMakeRepCode: () => void;
  making?: boolean;
};

export function RepPanel({ waiting, onCheck, onAnnounce, repCode, onMakeRepCode, making }: Props) {
  return (
    <Card style={{ gap: 12 }}>
      <Overline>{t('classes.rep')}</Overline>
      {waiting > 0 ? (
        <View style={{ gap: 8 }}>
          <Strong>{t('classes.waiting', { n: waiting })}</Strong>
          <Button title={t('classes.check')} variant="accent" icon="check-square" onPress={onCheck} />
        </View>
      ) : null}
      <Button title={t('classes.announce')} variant="secondary" icon="clipboard" onPress={onAnnounce} />
      {repCode ? (
        <InfoNote icon="key">{[t('classes.repCode', { code: repCode.code }), ...repCode.lines].join('\n')}</InfoNote>
      ) : (
        <View style={{ gap: 6 }}>
          <Button title={t('classes.addRep')} variant="secondary" icon="user-plus" onPress={onMakeRepCode} loading={making} />
          <Muted>{t('classes.addRepHint')}</Muted>
        </View>
      )}
    </Card>
  );
}
