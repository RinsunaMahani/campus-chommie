/**
 * What a list shows before it has anything in it: an icon, a short title, one line saying what goes here, and the
 * one button that fills it. UX research: an empty screen should teach the next step, not just say "nothing yet",
 * so a judge or student on a fresh account always has somewhere to go.
 */
import { Feather } from '@expo/vector-icons';
import { ComponentProps } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { Button } from '@/shared/components/Button';
import { IconTile } from '@/shared/components/Parts';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius, space, type } from '@/shared/theme/tokens';

type Props = {
  icon: ComponentProps<typeof Feather>['name'];
  title: string;
  body: string;
  /** The one thing to do next; leave out when the screen's own form is right below. */
  action?: { label: string; icon?: ComponentProps<typeof Feather>['name']; onPress: () => void };
};

export function EmptyState({ icon, title, body, action }: Props) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  return (
    <View style={styles.wrap} accessibilityRole="summary">
      <IconTile name={icon} size={56} tint={colors.accentTint} color={colors.accentDeep} />
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.body}>{body}</Text>
      {action ? (
        <View style={styles.action}>
          <Button title={action.label} icon={action.icon ?? 'plus'} variant="primary" onPress={action.onPress} />
        </View>
      ) : null}
    </View>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    wrap: {
      alignItems: 'center',
      gap: space.sm,
      paddingVertical: space.xl,
      paddingHorizontal: space.lg,
      borderRadius: radius.lg,
      borderWidth: 1,
      borderStyle: 'dashed',
      borderColor: colors.line,
    },
    title: { fontFamily: fonts.bold, ...type.headline, color: colors.ink, textAlign: 'center', marginTop: space.xs },
    body: { fontFamily: fonts.body, ...type.callout, color: colors.textMuted, textAlign: 'center', maxWidth: 320 },
    action: { alignSelf: 'stretch', marginTop: space.sm },
  });
