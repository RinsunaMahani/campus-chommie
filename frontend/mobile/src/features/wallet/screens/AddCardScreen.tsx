/**
 * Add a store card: pick the programme (or type another), then scan the barcode with the camera or type the
 * number. The camera is used only while scanning, and nothing it sees is kept. The card is saved on this phone only.
 */
import { CameraView, useCameraPermissions } from 'expo-camera';
import { router } from 'expo-router';
import { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { useSession } from '@/features/auth/session/SessionProvider';
import { Button } from '@/shared/components/Button';
import { InfoNote } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { Overline } from '@/shared/components/Text';
import { TextField } from '@/shared/components/TextField';
import { MessageKey, t } from '@/shared/i18n';
import { todaySast } from '@/shared/lib/dates';
import { Palette, useStyles } from '@/shared/theme/palette';
import { radius, space, fonts } from '@/shared/theme/tokens';

import { addCard, cleanNumber, numberProblem } from '../store';

/** Programme names only, in text: never a store's logo or colours. */
export const PROGRAMMES = [
  'Shoprite Xtra Savings',
  'Checkers Xtra Savings',
  'Pick n Pay Smart Shopper',
  'Clicks ClubCard',
  'Dis-Chem Benefits',
  'Woolworths WRewards',
];

export default function AddCardScreen() {
  const styles = useStyles(makeStyles);
  const { profile } = useSession();
  const [store, setStore] = useState('');
  const [other, setOther] = useState(false);
  const [number, setNumber] = useState('');
  const [scanning, setScanning] = useState(false);
  const [permission, requestPermission] = useCameraPermissions();
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);

  async function scan() {
    if (!permission?.granted) {
      const answer = await requestPermission();
      if (!answer.granted) {
        setErrors({ number: t('wallet.noCamera') });
        return;
      }
    }
    setScanning(true);
  }

  async function save() {
    const clean = cleanNumber(number);
    const found: Record<string, string> = {};
    if (!store.trim()) found.store = t('wallet.storeMissing');
    const problem = numberProblem(clean);
    if (problem) found.number = t(problem as MessageKey);
    setErrors(found);
    if (Object.keys(found).length) return;
    setBusy(true);
    await addCard(profile.email, store, clean, todaySast());
    router.back();
  }

  if (scanning) {
    return (
      <View style={styles.camera}>
        <CameraView
          style={StyleSheet.absoluteFill}
          facing="back"
          barcodeScannerSettings={{ barcodeTypes: ['ean13', 'ean8', 'upc_a', 'code128', 'code39', 'itf14', 'qr'] }}
          onBarcodeScanned={({ data }) => {
            setNumber(cleanNumber(data));
            setScanning(false);
          }}
        />
        <View style={styles.cameraFoot}>
          <Text style={styles.cameraText}>{t('wallet.aim')}</Text>
          <Button title={t('wallet.typeInstead')} variant="secondary" onPress={() => setScanning(false)} />
        </View>
      </View>
    );
  }

  const chip = (on: boolean, label: string, onPress: () => void) => (
    <Pressable key={label} accessibilityRole="button" accessibilityState={{ selected: on }} onPress={onPress} style={[styles.chip, on && styles.chipOn]}>
      <Text style={[styles.chipText, on && styles.chipTextOn]}>{label}</Text>
    </Pressable>
  );

  return (
    <Screen back title={t('wallet.add')} footer={<Button title={t('timetable.save')} variant="primary" onPress={save} loading={busy} />}>
      <View style={{ gap: space.sm }}>
        <Overline>{t('wallet.which')}</Overline>
        <View style={styles.wrap}>
          {PROGRAMMES.map((p) => chip(!other && store === p, p, () => { setOther(false); setStore(p); }))}
          {chip(other, t('wallet.other'), () => { setOther(true); setStore(''); })}
        </View>
        {errors.store && !other ? <Text style={styles.error}>{errors.store}</Text> : null}
      </View>
      {other ? <TextField label={t('wallet.storeName')} value={store} onChangeText={setStore} maxLength={40} error={errors.store} /> : null}
      <Button title={t('wallet.scan')} variant="secondary" icon="camera" onPress={scan} />
      <TextField
        label={t('wallet.number')}
        value={number}
        onChangeText={setNumber}
        maxLength={48}
        autoCapitalize="characters"
        keyboardType="default"
        hint={t('wallet.numberHint')}
        error={errors.number}
      />
      <InfoNote icon="lock">{t('wallet.private')}</InfoNote>
    </Screen>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    wrap: { flexDirection: 'row', flexWrap: 'wrap', gap: space.sm },
    chip: { paddingHorizontal: 14, paddingVertical: 9, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.line, backgroundColor: colors.white },
    chipOn: { backgroundColor: colors.accent, borderColor: colors.accent },
    chipText: { fontFamily: fonts.semibold, fontSize: 14, color: colors.ink },
    chipTextOn: { color: colors.pillText },
    error: { fontFamily: fonts.medium, fontSize: 14, color: colors.garnet },
    camera: { flex: 1, backgroundColor: '#000000' },
    cameraFoot: { position: 'absolute', left: 20, right: 20, bottom: 40, gap: space.md },
    cameraText: { fontFamily: fonts.bold, fontSize: 16, color: '#FFFFFF', textAlign: 'center' },
  });
