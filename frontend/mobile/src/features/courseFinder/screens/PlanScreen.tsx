import { Feather } from '@expo/vector-icons';
import { Redirect, router } from 'expo-router';
import { Pressable, Text, View } from 'react-native';

import { Button } from '@/shared/components/Button';
import { HeroScreen } from '@/shared/components/HeroScreen';
import { Card, InfoNote } from '@/shared/components/Parts';
import { Overline, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { usePalette } from '@/shared/theme/palette';
import { fonts } from '@/shared/theme/tokens';

import { ApplyGuide } from '../components/ApplyBox';
import { PlanSlot } from '../components/PlanSlot';
import { StillOpen, TestDateNote } from '../components/StillOpen';
import { useCourseFinder } from '../state';

/** The three-choice plan: the goal, a route into it and a safer related choice, then how to apply for them. */
export default function PlanScreen() {
  const colors = usePalette();
  const cf = useCourseFinder();
  if (!cf.plan || !cf.university) return <Redirect href="/course-finder" />;
  const { plan, university } = cf;

  function startOver() {
    cf.reset();
    router.dismissTo('/course-finder');
  }

  return (
    <HeroScreen
      back
      title={t('courseFinder.plan')}
      subtitle={t('courseFinder.planIntro')}
      band={
        <Pressable
          accessibilityRole="button"
          onPress={startOver}
          hitSlop={8}
          style={({ pressed }) => [
            { flexDirection: 'row', alignItems: 'center', gap: 6, alignSelf: 'flex-start', opacity: pressed ? 0.7 : 1 },
          ]}>
          <Feather name="rotate-ccw" size={13} color={colors.onAccentSoft} />
          <Text style={{ fontFamily: fonts.medium, fontSize: 14, color: colors.onAccentSoft }}>
            {t('courseFinder.startOver')}
          </Text>
        </Pressable>
      }
      footer={
        <Button
          title={t('courseFinder.fundingButton')}
          variant="primary"
          icon="dollar-sign"
          onPress={() => router.push('/course-finder/funding')}
        />
      }>
      <TestDateNote apply={plan.apply} />
      <StillOpen plan={plan} />

      <PlanSlot title={t('courseFinder.slotGoal')} slot={plan.goal} empty={t('courseFinder.slotEmptyGoal')} planUniversity={university.id} />
      <PlanSlot title={t('courseFinder.slotBridge')} slot={plan.bridge} empty={t('courseFinder.slotEmptyBridge')} planUniversity={university.id} />
      <PlanSlot title={t('courseFinder.slotSafe')} slot={plan.safe} empty={t('courseFinder.slotEmptySafe')} planUniversity={university.id} />

      <Card style={{ gap: 10, padding: 16 }}>
        <Title style={{ fontSize: 18, lineHeight: 24 }}>
          {t('courseFinder.acceptedCardTitle', { university: university.name })}
        </Title>
        <Text style={{ fontFamily: fonts.body, fontSize: 14.5, lineHeight: 20, color: colors.text }}>
          {t('courseFinder.acceptedCardSub')}
        </Text>
        <Button
          title={t('courseFinder.seeWhatHappensNext')}
          variant="secondary"
          icon="arrow-right"
          onPress={() => router.push(`/course-finder/next/${university.id}`)}
        />
      </Card>

      {plan.other_routes.length ? (
        <View style={{ gap: 8 }}>
          <Overline>{t('courseFinder.otherRoutes')}</Overline>
          {plan.other_routes.map((slot) => (
            <PlanSlot key={`${slot.match.university}-${slot.match.programme}`} slot={slot} empty="" planUniversity={university.id} />
          ))}
        </View>
      ) : null}

      {plan.notes.map((note, i) => (
        <InfoNote key={i} icon="info">
          {note}
        </InfoNote>
      ))}

      <Title style={{ fontSize: 22, marginTop: 8 }}>{t('courseFinder.apply')}</Title>
      <ApplyGuide apply={plan.apply} />
    </HeroScreen>
  );
}
