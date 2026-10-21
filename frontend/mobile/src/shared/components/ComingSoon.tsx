import { Feather } from '@expo/vector-icons';
import { ComponentProps } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { IconTile } from './Parts';
import { BackButton, Screen } from './Screen';
import { Body, Title } from './Text';
import { fonts } from '@/shared/theme/tokens';
import { Palette, useStyles } from '@/shared/theme/palette';

type Props = {
  title: string;
  icon: ComponentProps<typeof Feather>['name'];
  message: string;
  back?: boolean;
};

/** A feature whose folder exists but whose screens aren't built yet. Never a dead end: says what's coming. */
export function ComingSoon({ title, icon, message, back = true }: Props) {
  const styles = useStyles(makeStyles);
  return (
    <Screen>
      <View style={styles.header}>
        {back ? <BackButton /> : null}
        <Text style={styles.title}>{title}</Text>
      </View>
      <View style={styles.center}>
        <IconTile name={icon} size={64} />
        <Title style={{ textAlign: 'center' }}>Being built next</Title>
        <Body style={{ textAlign: 'center' }}>{message}</Body>
      </View>
    </Screen>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  header: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  title: { fontFamily: fonts.bold, fontSize: 17, color: colors.text },
  center: { alignItems: 'center', gap: 12, paddingTop: 100, paddingHorizontal: 12 },
});
