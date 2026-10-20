import { StyleSheet, Text } from 'react-native';

import { Checkbox } from './Choice';
import { fonts } from '@/shared/theme/tokens';
import { Palette, useStyles } from '@/shared/theme/palette';

/**
 * "I'm 18 or older". Mandatory: accounts are for adults only (POPIA), so
 * the sign-up button stays disabled until it's ticked. The backend records
 * it with the consent records.
 */
export function AgeCheckbox({ checked, onChange, error }: { checked: boolean; onChange: (v: boolean) => void; error?: boolean }) {
  const styles = useStyles(makeStyles);
  return (
    <Checkbox checked={checked} onChange={onChange} error={error} label="I'm 18 or older">
      <Text style={styles.text} onPress={() => onChange(!checked)}>
        I&apos;m 18 or older.
      </Text>
      {error && !checked ? <Text style={styles.error}>You must be 18 or older to create an account.</Text> : null}
    </Checkbox>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  text: { fontFamily: fonts.medium, fontSize: 13.5, lineHeight: 20, color: colors.text },
  error: { fontFamily: fonts.body, fontSize: 12, color: colors.garnet, marginTop: 4 },
});
