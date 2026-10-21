/**
 * The three-choice plan (brief, M2): each choice with its lines and source,
 * a route's conditions, a safer choice at another university saying where,
 * how to apply on the day, and the funding the choice opens. The plan is the
 * API's own, recorded for the strong SMU learner aiming at MBChB
 * (fixtures/plan.json).
 */
import { expect, jest, test } from '@jest/globals';
import { render, screen } from '@testing-library/react-native';

import { ApplyGuide } from '../components/ApplyBox';
import { PlanSlot } from '../components/PlanSlot';
import { Plan } from '../types';
import { formatDay } from '../words';
import recorded from './fixtures/plan.json';

jest.mock('expo-web-browser', () => ({ openBrowserAsync: jest.fn() }));
// Icons load their font after the render; nothing here is about icons.
jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));

const plan = (recorded as unknown as { data: { plan: Plan } }).data.plan;

test('the goal shows its lines, how to apply for each intake, and its funding', () => {
  const goal = plan.goal!;
  render(<PlanSlot title="1. Your goal" slot={goal} empty="" planUniversity="smu" />);
  expect(screen.getByText('1. Your goal')).toBeTruthy();
  expect(screen.getByText(goal.match.programme_name)).toBeTruthy();
  expect(screen.getByText(goal.match.label)).toBeTruthy();
  for (const line of goal.notes) expect(screen.getByText(line)).toBeTruthy();
  for (const w of goal.apply) expect(screen.getByText(w.heading)).toBeTruthy();
  expect(screen.getByText(goal.funding!.lines[0])).toBeTruthy();
  for (const f of goal.funding!.funders) expect(screen.getByText(f.name)).toBeTruthy();
});

test('a route into the goal says whether it is guaranteed, its conditions and its places, once each', () => {
  const route = plan.bridge!;
  render(<PlanSlot title="2. A route into your goal" slot={route} empty="" planUniversity="smu" />);
  expect(screen.getByText('Considered, not guaranteed.')).toBeTruthy();
  expect(screen.getByText(`Conditions: ${route.bridge!.conditions}`)).toBeTruthy();
  expect(screen.getByText('Places on this route: 5.')).toBeTruthy();
});

test('a safer choice at another university says where it is', () => {
  const safe = plan.safe!;
  render(<PlanSlot title="3. A safer related choice" slot={safe} empty="" planUniversity="smu" />);
  expect(screen.getByText(`At ${safe.match.university_name}`)).toBeTruthy();
  expect(screen.getByText(safe.notes[0])).toBeTruthy();
});

test('a choice the plan has nothing for says so', () => {
  render(<PlanSlot title="2. A route into your goal" slot={null} empty="We found no published route into your goal." />);
  expect(screen.getByText('We found no published route into your goal.')).toBeTruthy();
});

test('how to apply lists every date still ahead, the fee and NSFAS', () => {
  render(<ApplyGuide apply={plan.apply} />);
  for (const d of plan.apply.deadlines) expect(screen.getByText(d.text)).toBeTruthy();
  expect(screen.getAllByText(formatDay(plan.apply.deadlines[0].date)).length).toBeGreaterThan(0);
  expect(screen.getByText('R300')).toBeTruthy(); // SMU's fee, from integer cents
  for (const g of [...plan.apply.universities, ...plan.apply.funding]) expect(screen.getByText(g.name)).toBeTruthy();
});
