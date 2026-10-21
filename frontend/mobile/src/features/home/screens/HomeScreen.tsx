import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { View } from 'react-native';

import { CAMPUS_PHOTOS } from '@/features/courseFinder/campusPhotos';
import { PhotoCredit } from '@/features/courseFinder/components/CampusPhotoCard';

import { HomeAlerts } from '@/features/alerts/components/HomeAlerts';
import { useSession } from '@/features/auth/session/SessionProvider';
import { DemoBanner } from '@/features/profile/components/DemoBanner';
import { useProfile } from '@/features/profile/state';
import { updatesApi } from '@/features/updates/api/updatesApi';
import { Button } from '@/shared/components/Button';
import { Card, ListRow } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { Muted, Overline, Strong, Title } from '@/shared/components/Text';
import { UniMonogram } from '@/shared/components/UniMonogram';
import { t } from '@/shared/i18n';

/**
 * Home tab: the student's campus photo behind the top (where we have one, with its credit at the foot),
 * today's alerts first, then updates and the course finder, and the way to account security and out.
 */
export default function HomeScreen() {
  const { profile, signOut } = useSession();
  const { mock, profile: student } = useProfile();
  const photo = student?.university ? CAMPUS_PHOTOS[student.university] : undefined;
  const [unread, setUnread] = useState(0);

  useFocusEffect(
    useCallback(() => {
      if (mock) return;
      updatesApi
        .list()
        .then((list) => setUnread(list.filter((u) => !u.read_at).length))
        .catch(() => undefined);
    }, [mock]),
  );

  return (
    <Screen tab backdrop={photo?.image}>
      <View style={{ gap: 6 }}>
        <Title>Home</Title>
        {student?.university_name && student.university ? (
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10 }}>
            <UniMonogram id={student.university} size={36} />
            <Strong style={{ flex: 1 }}>{student.university_name}</Strong>
          </View>
        ) : null}
        <Muted>Signed in as {profile.email}</Muted>
        <DemoBanner />
      </View>
      {/* Room for the campus photo to show before the cards rise over it. */}
      {photo ? <View style={{ height: 110 }} /> : null}

      <HomeAlerts />

      <Card style={{ paddingVertical: 4 }}>
        {mock ? null : (
          <ListRow
            icon="bell"
            title={unread ? `${t('alerts.updates')} · ${t('alerts.unread', { n: unread })}` : t('alerts.updates')}
            subtitle={t('alerts.updatesSub')}
            onPress={() => router.push('/updates')}
          />
        )}
        <ListRow icon="compass" title={t('courseFinder.title')} subtitle={t('courseFinder.entrySub')} onPress={() => router.push('/course-finder')} />
        <ListRow icon="tool" title={t('colleges.entry')} subtitle={t('colleges.entrySub')} onPress={() => router.push('/course-finder/colleges')} last />
      </Card>

      <Overline>Your account</Overline>
      <Card style={{ paddingVertical: 4 }}>
        <ListRow icon="shield" title="Account security" subtitle="Phones, password and your account" onPress={() => router.push('/security')} last />
      </Card>

      <Button title="Sign out" variant="secondary" icon="log-out" onPress={signOut} />
      {photo ? <PhotoCredit credit={`${photo.caption}. ${photo.credit}`} source={photo.source} /> : null}
    </Screen>
  );
}
