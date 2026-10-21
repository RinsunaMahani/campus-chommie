import { Feather } from '@expo/vector-icons';
import { Tabs } from 'expo-router';
import { ComponentProps } from 'react';
import { ColorValue, StyleSheet, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { colors, fonts } from '@/shared/theme/tokens';

type IconName = ComponentProps<typeof Feather>['name'];

function TabIcon({ name, color, focused }: { name: IconName; color: ColorValue; focused: boolean }) {
  return (
    <View style={[styles.pill, focused && styles.pillOn]}>
      <Feather name={name} size={23} color={color} />
    </View>
  );
}

/**
 * Bottom bar. Each feature adds its tab as it's built (Week, Money, Course,
 * Support). Big enough to hit with a thumb on a small phone, and it adds
 * the phone's own bottom inset so it never sits under the system navigation bar.
 */
export default function TabsLayout() {
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
        tabBarActiveTintColor: colors.accentDeep,
        tabBarInactiveTintColor: colors.textMuted,
        // A line height, or a label with a descender ('Money') loses its tail.
        tabBarLabelStyle: { fontFamily: fonts.bold, fontSize: 12.5, lineHeight: 18, marginTop: 2 },
        tabBarItemStyle: { paddingTop: 8 },
        tabBarStyle: {
          backgroundColor: colors.white,
          borderTopColor: colors.line,
          height: 78 + insets.bottom,
          paddingBottom: 8 + insets.bottom,
        },
        sceneStyle: { backgroundColor: colors.porcelain },
      }}>
      <Tabs.Screen name="home" options={tab('Home', 'home')} />
      <Tabs.Screen name="week" options={tab('Week', 'calendar')} />
      <Tabs.Screen name="money" options={tab('Money', 'credit-card')} />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  pill: { width: 60, height: 34, borderRadius: 17, alignItems: 'center', justifyContent: 'center' },
  pillOn: { backgroundColor: colors.accentTint },
});
