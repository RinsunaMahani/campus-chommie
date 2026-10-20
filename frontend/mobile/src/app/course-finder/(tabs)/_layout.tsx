import { Tabs } from 'expo-router';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { dockOptions, dockTab } from '@/shared/components/Dock';
import { t } from '@/shared/i18n';

/**
 * Find my course's bottom bar, on the same floating dock as the student's: each part has its own
 * place instead of one long screen. Home (what to do next), My marks (step 1, as before), Courses
 * (by faculty), Explore (universities and colleges) and Funding. No account; nothing kept on a server.
 */
export default function FinderTabsLayout() {
  const insets = useSafeAreaInsets();
  return (
    <Tabs screenOptions={dockOptions(insets)}>
      <Tabs.Screen name="index" options={dockTab(t('finderTabs.home'), 'home')} />
      <Tabs.Screen name="marks" options={dockTab(t('finderTabs.marks'), 'edit-3')} />
      <Tabs.Screen name="courses" options={dockTab(t('finderTabs.courses'), 'book-open')} />
      <Tabs.Screen name="explore" options={dockTab(t('finderTabs.explore'), 'map')} />
      <Tabs.Screen name="bursaries" options={dockTab(t('finderTabs.funding'), 'award')} />
    </Tabs>
  );
}
