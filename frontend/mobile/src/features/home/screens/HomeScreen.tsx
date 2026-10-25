import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { View } from 'react-native';

import { CAMPUS_PHOTOS } from '@/features/courseFinder/campusPhotos';
import { PhotoCredit } from '@/features/courseFinder/components/CampusPhotoCard';

import { useSession } from '@/features/auth/session/SessionProvider';
import { studentHeader } from '@/features/profile/components/HeaderTools';
import { useProfile } from '@/features/profile/state';
import { updatesApi } from '@/features/updates/api/updatesApi';

import { HomeReviewCard } from '@/features/review/components/HomeReviewCard';

import { NextSteps } from '../components/NextSteps';
import { TodayTiles } from '../components/TodayTiles';
import { Card, ListRow } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { Overline, Strong } from '@/shared/components/Text';
import { UniMonogram } from '@/shared/components/UniMonogram';
import { t } from '@/shared/i18n';
import { formatDay, todaySast } from '@/shared/lib/dates';

/**
 * Home tab: a hero band at the top (Daylight paper) with today's date, the title and the student's university,
 * on the student's campus photo where we have one (its credit at the foot) or the wallpaper; today's alerts
 * first, then updates and the course finder, and the way to account security and out.
 */
export default function HomeScreen() {
  const { signOut } = useSession();
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
    <Screen
      tab
      hero
      backdrop={photo?.image}
      overline={formatDay(todaySast())}
      title="Home"
      band={
        student?.university_name && student.university ? (
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10, marginTop: 6 }}>
            <UniMonogram id={student.university} size={36} />
            <Strong style={{ flex: 1 }}>{student.university_name}</Strong>
          </View>
        ) : null
      }
      {...studentHeader()}>

      <Overline>{t('home.todayTitle')}</Overline>
      {mock ? null : <TodayTiles />}
      {mock ? null : <HomeReviewCard />}
      {mock ? null : <NextSteps />}

      <Overline>{t('home.more')}</Overline>

      <Card style={{ paddingVertical: 4 }}>
        {mock ? null : (
          <ListRow
            tone="mint"
            icon="bell"
            title={t('alerts.updates')}
            subtitle={unread ? `${t('alerts.unread', { n: unread })}. ${t('alerts.updatesSub')}` : t('alerts.updatesSub')}
            badge={unread || undefined}
            onPress={() => router.push('/updates')}
          />
        )}
        {mock ? null : (
          <ListRow tone="mint" icon="bar-chart-2" title={t('review.title')} subtitle={t('review.entrySub')} onPress={() => router.push('/review')} />
        )}
        <ListRow tone="mint" icon="compass" title={t('courseFinder.title')} subtitle={t('courseFinder.entrySub')} onPress={() => router.push('/course-finder')} />
        <ListRow tone="mint" icon="tool" title={t('colleges.entry')} subtitle={t('colleges.entrySub')} onPress={() => router.push('/course-finder/colleges')} last />
      </Card>

      <Overline>Your account</Overline>
      <Card style={{ paddingVertical: 4 }}>
        <ListRow tone="mint" icon="message-circle" title={t('whatsapp.title')} subtitle={t('whatsapp.entrySub')} onPress={() => router.push('/whatsapp')} />
        <ListRow tone="mint" icon="shield" title="Account security" subtitle="Phones, password and your account" onPress={() => router.push('/security')} />
        <ListRow icon="log-out" title="Sign out" onPress={signOut} last />
      </Card>
      {photo ? <PhotoCredit credit={`${photo.caption}. ${photo.credit}`} source={photo.source} /> : null}
    </Screen>
  );
}
