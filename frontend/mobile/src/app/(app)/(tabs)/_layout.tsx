import { Tabs } from 'expo-router';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { dockOptions, dockTab } from '@/shared/components/Dock';

/** The student's bottom bar: Home, Week, Money and Support, on the floating dock. */
export default function TabsLayout() {
  const insets = useSafeAreaInsets();
  return (
    <Tabs screenOptions={dockOptions(insets)}>
      <Tabs.Screen name="home" options={dockTab('Home', 'home')} />
      <Tabs.Screen name="week" options={dockTab('Week', 'calendar')} />
      <Tabs.Screen name="money" options={dockTab('Money', 'credit-card')} />
      <Tabs.Screen name="support" options={dockTab('Support', 'life-buoy')} />
    </Tabs>
  );
}
