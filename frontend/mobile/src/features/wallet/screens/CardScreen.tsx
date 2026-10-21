/**
 * One store card at the till: the programme's name, then the barcode big on white with its number under it.
 * A tip says to turn the brightness up; removing the card asks first.
 */
import { router, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { Alert, Platform } from 'react-native';

import { useSession } from '@/features/auth/session/SessionProvider';
import { Button } from '@/shared/components/Button';
import { InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { Body } from '@/shared/components/Text';
import { t } from '@/shared/i18n';

import { BarcodeView } from '../components/BarcodeView';
import { loadCards, removeCard, StoreCard } from '../store';

export default function CardScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { profile } = useSession();
  const [card, setCard] = useState<StoreCard | null | undefined>(undefined);

  useEffect(() => {
    loadCards(profile.email).then((cards) => setCard(cards.find((c) => c.id === id) ?? null));
  }, [id, profile.email]);

  async function remove() {
    const go = async () => {
      await removeCard(profile.email, id);
      router.back();
    };
    if (Platform.OS === 'web') return go();
    Alert.alert(t('wallet.removeTitle'), t('wallet.removeSure'), [
      { text: t('wallet.keep'), style: 'cancel' },
      { text: t('wallet.remove'), style: 'destructive', onPress: go },
    ]);
  }

  return (
    <Screen
      back
      title={card?.store ?? t('wallet.title')}
      footer={card ? <Button title={t('wallet.remove')} variant="secondary" icon="trash-2" onPress={remove} /> : undefined}>
      {card === null ? <Body>{t('wallet.gone')}</Body> : null}
      {card ? <BarcodeView number={card.number} /> : null}
      {card ? <InfoNote icon="sun">{t('wallet.brightness')}</InfoNote> : null}
    </Screen>
  );
}
