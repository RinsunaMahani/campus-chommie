/**
 * A section that opens in place: a header row (icon, title, an optional one-line summary, a chevron) that is
 * tappable as a whole, and the details under it once open. Progressive-disclosure guidance: one level only
 * (never a section inside a section), the whole header is the target, and nothing urgent hides in one (crisis
 * help is never inside a Section). Screen readers hear "expanded" or "collapsed"; closed details aren't there.
 */
import { Feather } from '@expo/vector-icons';
import { ComponentProps, ReactNode, useState } from 'react';
import { LayoutAnimation, Platform, Pressable, StyleSheet, Text, UIManager, View } from 'react-native';

import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius, space, type } from '@/shared/theme/tokens';

if (Platform.OS === 'android') UIManager.setLayoutAnimationEnabledExperimental?.(true);

type Props = {
  title: string;
  /** One line under the title, shown open or closed: the gist ("Closes Tue 30 Jun"). */
  summary?: string;
  icon?: ComponentProps<typeof Feather>['name'];
  /** The icon's colour: a signal colour for attention, or the default. */
  tint?: string;
  defaultOpen?: boolean;
  /** No rule above it: the first section in a card. */
  first?: boolean;
  children: ReactNode;
};

export function Section({ title, summary, icon, tint, defaultOpen = false, first, children }: Props) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const [open, setOpen] = useState(defaultOpen);
  const toggle = () => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setOpen((o) => !o);
  };
  return (
    <View style={[styles.wrap, !first && styles.rule]}>
      <Pressable
        accessibilityRole="button"
        accessibilityState={{ expanded: open }}
        accessibilityLabel={summary ? `${title}. ${summary}` : title}
        onPress={toggle}
        style={styles.head}>
        {icon ? (
          <View style={[styles.icon, { backgroundColor: colors.iconTile }]}>
            <Feather name={icon} size={18} color={tint ?? colors.accentDeep} />
          </View>
        ) : null}
        <View style={styles.words}>
          <Text style={styles.title}>{title}</Text>
          {summary ? <Text style={styles.summary}>{summary}</Text> : null}
        </View>
        <Feather name={open ? 'chevron-up' : 'chevron-down'} size={20} color={colors.textMuted} />
      </Pressable>
      {open ? <View style={styles.body}>{children}</View> : null}
    </View>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    wrap: { paddingVertical: space.xs },
    rule: { borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: colors.line },
    // 48 high at least: a comfortable thumb target.
    head: { flexDirection: 'row', alignItems: 'center', gap: space.md, minHeight: 48, paddingVertical: space.sm },
    icon: { width: 36, height: 36, borderRadius: radius.sm, alignItems: 'center', justifyContent: 'center' },
    words: { flex: 1, gap: 2 },
    title: { fontFamily: fonts.bold, ...type.headline, color: colors.ink },
    summary: { fontFamily: fonts.medium, ...type.label, color: colors.textMuted },
    body: { gap: space.sm, paddingBottom: space.md },
  });
