/**
 * My cards: the student's store cards as coloured tiles with the programme's name in text (never a store's logo),
 * kept on this phone only. A tap shows the barcode for the till; "Add a card" is the one main button.
 */
import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { useSession } from '@/features/auth/session/SessionProvider';
import { Button } from '@/shared/components/Button';
import { EmptyState } from '@/shared/components/EmptyState';
import { InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { t } from '@/shared/i18n';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius, space } from '@/shared/theme/tokens';

import { loadCards, MAX_CARDS, StoreCard } from '../store';

export default function WalletScreen() {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const { profile } = useSession();
  const [cards, setCards] = useState<StoreCard[] | null>(null);

  useFocusEffect(
    useCallback(() => {
      loadCards(profile.email).then(setCards);
    }, [profile.email]),
  );

  return (
    <Screen
      back
      title={t('wallet.title')}
      subtitle={t('wallet.sub')}
      footer={
        cards && cards.length < MAX_CARDS ? (
          <Button title={t('wallet.add')} variant="primary" icon="plus" onPress={() => router.push('/wallet/add')} />
        ) : undefined
      }>
      {cards && !cards.length ? <EmptyState icon="credit-card" title={t('wallet.emptyTitle')} body={t('wallet.empty')} /> : null}
      <View style={styles.grid}>
        {cards?.map((c) => {
          const tint = colors.classColours[c.colour % colors.classColours.length];
          return (
            <Pressable
              key={c.id}
              accessibilityRole="button"
              accessibilityLabel={t('wallet.show', { store: c.store })}
              onPress={() => router.push({ pathname: '/wallet/[id]', params: { id: c.id } })}
              style={[styles.tile, { borderColor: tint }]}>
              <View style={[styles.stripe, { backgroundColor: tint }]} />
              <Text style={styles.store} numberOfLines={2}>
                {c.store}
              </Text>
              <Text style={styles.last}>•••• {c.number.slice(-4)}</Text>
            </Pressable>
          );
        })}
      </View>
      <InfoNote icon="lock">{t('wallet.private')}</InfoNote>
    </Screen>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    grid: { flexDirection: 'row', flexWrap: 'wrap', gap: space.md },
    tile: {
      width: '47%',
      minHeight: 110,
      padding: space.md,
      gap: space.sm,
      borderRadius: radius.lg,
      borderWidth: 1.5,
      backgroundColor: colors.white,
      overflow: 'hidden',
    },
    stripe: { height: 6, borderRadius: radius.pill, width: 40 },
    store: { fontFamily: fonts.bold, fontSize: 16, lineHeight: 21, color: colors.ink },
    last: { fontFamily: fonts.medium, fontSize: 14, color: colors.textMuted, fontVariant: ['tabular-nums'] },
  });
