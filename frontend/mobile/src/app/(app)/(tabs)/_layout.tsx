import { Feather } from '@expo/vector-icons';
import { router, Tabs } from 'expo-router';
import { ComponentProps } from 'react';
import { ColorValue, Pressable, StyleProp, StyleSheet, Text, View, ViewStyle } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { fonts } from '@/shared/theme/tokens';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';

type IconName = ComponentProps<typeof Feather>['name'];

function TabIcon({ name, color, focused }: { name: IconName; color: ColorValue; focused: boolean }) {
  const styles = useStyles(makeStyles);
  return (
    <View style={[styles.pill, focused && styles.pillOn]}>
      <Feather name={name} size={23} color={color} />
    </View>
  );
}

/**
 * The centre button, like YouTube's and Standard Bank's: raised above the bar, round and filled, and it opens the
 * Outdoors sheet over the screen you're on instead of switching tabs.
 */
function OutdoorsButton({ style }: { style?: StyleProp<ViewStyle> }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  return (
    <View style={[style, styles.centreSlot]} pointerEvents="box-none">
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Outdoors"
        accessibilityHint="Opens places near your campus"
        onPress={() => router.push('/places')}
        style={({ pressed }) => [styles.centre, pressed && { transform: [{ scale: 0.94 }] }]}>
        <Feather name="sun" size={26} color={colors.pillText} />
      </Pressable>
      <Text style={styles.centreLabel}>Outdoors</Text>
    </View>
  );
}

/**
 * Bottom bar: Home, Week, Outdoors in the centre, Money, Support. Big enough to hit with a thumb on a small phone,
 * and it adds the phone's own bottom inset so it never sits under the system navigation bar.
 */
export default function TabsLayout() {
  const colors = usePalette();
  const insets = useSafeAreaInsets();
  const tab = (title: string, icon: IconName) => ({
    title,
    tabBarIcon: ({ color, focused }: { color: ColorValue; focused: boolean }) => (
      <TabIcon name={icon} color={color} focused={focused} />
    ),
  });

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        // The tab you're on in mint: the student side's colour for "here" and for actions.
        tabBarActiveTintColor: colors.accentDeep,
        tabBarInactiveTintColor: colors.textFaint,
        // A line height, or a label with a descender ('Money') loses its tail.
        tabBarLabelStyle: { fontFamily: fonts.bold, fontSize: 11.5, lineHeight: 18, marginTop: 2 }, // five tabs: "Timetable" fits
        // Each tab stacks 5 + 28 (icon) + 20 (label) + 5 = 58 under this padding. The dock's 76 holds that with
        // the same gap above the pill as under the words; any less and the label's bottom is cut off.
        tabBarItemStyle: { paddingTop: 11 },
        // Floating glass, clear of the screen's edges and the system bar.
        tabBarStyle: {
          position: 'absolute',
          left: 14,
          right: 14,
          bottom: 12 + insets.bottom,
          height: 76,
          paddingBottom: 0,
          borderRadius: 24,
          borderTopWidth: 1,
          borderWidth: 1,
          borderTopColor: colors.line,
          borderColor: colors.line,
          backgroundColor: colors.dock,
          elevation: 0,
          // The centre button rises above the bar.
          overflow: 'visible',
        },
        sceneStyle: { backgroundColor: colors.porcelain },
      }}>
      <Tabs.Screen name="home" options={tab('Home', 'home')} />
      <Tabs.Screen name="week" options={tab('Week', 'calendar')} />
      <Tabs.Screen name="outdoors" options={{ title: 'Outdoors', tabBarButton: ({ style }) => <OutdoorsButton style={style} /> }} />
      <Tabs.Screen name="money" options={tab('Money', 'credit-card')} />
      <Tabs.Screen name="support" options={tab('Support', 'life-buoy')} />
    </Tabs>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  pill: { width: 60, height: 34, borderRadius: 17, alignItems: 'center', justifyContent: 'center' },
  pillOn: { backgroundColor: colors.accentTint },
  centreSlot: { flex: 1, alignItems: 'center', justifyContent: 'flex-end', paddingBottom: 9 },
  centre: {
    position: 'absolute',
    top: -22,
    width: 60,
    height: 60,
    borderRadius: 30,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.accent,
    // A ring the colour of the page, so the button reads as lifted off the bar.
    borderWidth: 4,
    borderColor: colors.porcelain,
  },
  centreLabel: { fontFamily: fonts.bold, fontSize: 11.5, lineHeight: 18, color: colors.accentDeep },
});
