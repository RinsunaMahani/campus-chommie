import { router } from 'expo-router';
import { View } from 'react-native';

import { useSession } from '@/features/auth/session/SessionProvider';
import { Button } from '@/shared/components/Button';
import { Card, ListRow } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { Muted, Overline, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';

/** Home tab: who is signed in, the course finder, and the way to account security and out. */
export default function HomeScreen() {
  const { profile, signOut } = useSession();

  return (
    <Screen tab>
      <View style={{ gap: 6 }}>
        <Title>Home</Title>
        <Muted>Signed in as {profile.email}</Muted>
      </View>

      <Card style={{ paddingVertical: 4 }}>
        <ListRow icon="compass" title={t('courseFinder.title')} subtitle={t('courseFinder.entrySub')} onPress={() => router.push('/course-finder')} last />
      </Card>

      <Overline>Your account</Overline>
      <Card style={{ paddingVertical: 4 }}>
        <ListRow icon="shield" title="Account security" subtitle="Phones, password and your account" onPress={() => router.push('/security')} last />
      </Card>

      <Button title="Sign out" variant="secondary" icon="log-out" onPress={signOut} />
    </Screen>
  );
}
