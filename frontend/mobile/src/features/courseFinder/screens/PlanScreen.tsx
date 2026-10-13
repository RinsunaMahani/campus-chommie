import { Redirect, router } from 'expo-router';
import { View } from 'react-native';

import { Button } from '@/shared/components/Button';
import { HeroScreen } from '@/shared/components/HeroScreen';
import { InfoNote } from '@/shared/components/Parts';
import { Overline, Title } from '@/shared/components/Text';
import { t } from '@/shared/i18n';

import { ApplyGuide } from '../components/ApplyBox';
import { PlanSlot } from '../components/PlanSlot';
import { StillOpen, TestDateNote } from '../components/StillOpen';
import { useCourseFinder } from '../state';

/** The three-choice plan: the goal, a route into it and a safer related choice, then how to apply for them. */
export default function PlanScreen() {
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
      footer={
        <View style={{ flexDirection: 'row', gap: 10 }}>
          <Button compact title={t('courseFinder.changeGoal')} variant="secondary" onPress={() => router.back()} />
          <Button compact title={t('courseFinder.startOver')} variant="secondary" icon="rotate-ccw" onPress={startOver} />
        </View>
      }>
      <TestDateNote apply={plan.apply} />
      <StillOpen plan={plan} />

      <PlanSlot title={t('courseFinder.slotGoal')} slot={plan.goal} empty={t('courseFinder.slotEmptyGoal')} planUniversity={university.id} />
      <PlanSlot title={t('courseFinder.slotBridge')} slot={plan.bridge} empty={t('courseFinder.slotEmptyBridge')} planUniversity={university.id} />
      <PlanSlot title={t('courseFinder.slotSafe')} slot={plan.safe} empty={t('courseFinder.slotEmptySafe')} planUniversity={university.id} />

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
