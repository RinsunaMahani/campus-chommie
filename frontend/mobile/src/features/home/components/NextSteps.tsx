/**
 * "Do this next" on Home: at most three steps the server worked out from everything the app knows about the
 * student (money, the week, exams, saved bursaries, goals), most urgent first. Each is one line, why in small
 * text, and where it leads; amber marks the urgent ones. Replaces the long alert cards ("Heads up").
 */
import { Feather } from '@expo/vector-icons';
import { Href, router, useFocusEffect } from 'expo-router';
import { ComponentProps, useCallback, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { api } from '@/shared/api/client';
import { Card } from '@/shared/components/Parts';
import { Overline } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius, space, type } from '@/shared/theme/tokens';

export type NextStep = {
  kind: string;
  line: string;
  why: string;
  action: string;
  target: 'money' | 'week' | 'timetable' | 'funding' | 'support';
  tone: 'normal' | 'attention';
};

export const nextStepsApi = {
  mine: () => api<{ today: string; steps: NextStep[] }>('GET', '/me/next-steps', undefined, { auth: true }),
};

type IconName = ComponentProps<typeof Feather>['name'];

const ICON: Record<string, IconName> = {
  money_and_week: 'alert-triangle',
  money: 'credit-card',
  exam: 'edit-3',
  due: 'flag',
  heavy_week: 'calendar',
  funding: 'award',
  goal: 'target',
  setup_classes: 'clock',
  setup_money: 'credit-card',
};

export const ROUTE: Record<NextStep['target'], Href> = {
  money: '/money',
  week: '/week',
  timetable: '/timetable',
  funding: '/course-finder/funding',
  support: '/support',
};

export function NextSteps() {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const [steps, setSteps] = useState<NextStep[] | null>(null);

  useFocusEffect(
    useCallback(() => {
      nextStepsApi
        .mine()
        .then((a) => setSteps(a.steps))
        .catch(() => setSteps([]));
    }, []),
  );

  if (!steps || !steps.length) return null;
  return (
    <View style={{ gap: space.sm }}>
      <Overline>{t('home.doNext')}</Overline>
      <Card style={{ paddingVertical: space.xs }}>
        {steps.map((s, i) => {
          const tint = s.tone === 'attention' ? colors.marigold : colors.accentDeep;
          return (
            <Pressable
              key={s.kind + i}
              accessibilityRole="button"
              accessibilityLabel={`${s.line} ${s.action}`}
              accessibilityHint={s.why}
              onPress={() => router.push(ROUTE[s.target])}
              style={({ pressed }) => [styles.row, i > 0 && styles.rule, pressed && { opacity: 0.75 }]}>
              <View style={[styles.icon, { backgroundColor: colors.iconTile }]}>
                <Feather name={ICON[s.kind] ?? 'arrow-right'} size={18} color={tint} />
              </View>
              <View style={{ flex: 1, gap: 3 }}>
                <Text style={styles.line}>{s.line}</Text>
                <Text style={styles.why} numberOfLines={2}>
                  {s.why}
                </Text>
                <Text style={[styles.action, { color: tint }]}>{s.action} →</Text>
              </View>
            </Pressable>
          );
        })}
      </Card>
    </View>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    row: { flexDirection: 'row', gap: space.md, paddingVertical: space.md, alignItems: 'flex-start' },
    rule: { borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: colors.line },
    icon: { width: 36, height: 36, borderRadius: radius.sm, alignItems: 'center', justifyContent: 'center' },
    line: { fontFamily: fonts.bold, ...type.callout, color: colors.ink },
    why: { fontFamily: fonts.medium, fontSize: 13, lineHeight: 18, color: colors.textMuted },
    action: { fontFamily: fonts.bold, fontSize: 14 },
  });
