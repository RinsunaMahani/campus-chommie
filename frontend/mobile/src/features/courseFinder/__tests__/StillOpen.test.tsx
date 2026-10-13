/**
 * "What you can still do now" at the top of the plan, built only from the
 * plan's own dates (the API's answers on Tue 13 Oct 2026, fixtures/plan.json
 * for SMU and plan_tut.json for TUT): NSFAS still open with its closing date,
 * TUT's late applications and next window coming up, what isn't published
 * and what has closed, choices with the same dates on one line; and the note
 * a preview's test date brings.
 */
import { expect, jest, test } from '@jest/globals';
import { render, screen } from '@testing-library/react-native';

import { stillOpen, StillOpen, TestDateNote } from '../components/StillOpen';
import { Plan } from '../types';
import smu from './fixtures/plan.json';
import tut from './fixtures/plan_tut.json';

jest.mock('@expo/vector-icons', () => ({ Feather: () => null }));

const smuPlan = (smu as unknown as { data: { plan: Plan } }).data.plan;
const tutPlan = (tut as unknown as { data: { plan: Plan } }).data.plan;
const said = (plan: Plan) => stillOpen(plan).map((s) => [s.title, s.rows.map((r) => [r.who, r.detail])]);

const NSFAS = 'National Student Financial Aid Scheme (NSFAS)';
const SMU = 'Sefako Makgatho Health Sciences University';
const TUT = 'Tshwane University of Technology';

test('aiming at SMU in October: NSFAS still open, then what is not published and what has closed', () => {
  expect(said(smuPlan)).toEqual([
    ['Open now', [[NSFAS, 'Funding for 2027 · closes Sat 31 Oct 2026 · 18 days left']]],
    [
      'Dates not published yet',
      [
        [NSFAS, 'Funding for 2028'],
        [`${SMU}, University of Pretoria`, 'To start in 2028'],
      ],
    ],
    ['Closed', [[`${SMU}, University of Pretoria`, 'To start in 2027']]],
  ]);
});

test('a window the engine asks the learner to check gets its own section, never "Open now"', () => {
  // UP's opening date isn't verified, so on Mon 1 Jun 2026 the engine says "Check the dates" (status check).
  const safe = smuPlan.safe!;
  const check = { ...safe.apply[0], status: 'check' as const, label: 'Check the dates', closes: '2026-06-30', next_date: '2026-06-30', days: 29 };
  const plan = { ...smuPlan, safe: { ...safe, apply: [check, safe.apply[1]] } };
  const sections = said(plan);
  expect(sections[0][0]).toBe('Open now');
  expect(sections[1]).toEqual(['Check the dates', [['University of Pretoria', 'To start in 2027 · closes Tue 30 Jun 2026 · see the choice below']]]);
});

test("aiming at TUT: its late applications and next window come up, soonest first, once for both choices", () => {
  expect(said(tutPlan)).toEqual([
    ['Open now', [[NSFAS, 'Funding for 2027 · closes Sat 31 Oct 2026 · 18 days left']]],
    [
      'Coming up',
      [
        [TUT, 'To start in 2027 · late applications Thu 14 Jan 2027 to Fri 22 Jan 2027 · in 93 days'],
        [TUT, 'To start in 2028 · opens Thu 1 Apr 2027 · in 170 days'],
      ],
    ],
    ['Dates not published yet', [[NSFAS, 'Funding for 2028']]],
  ]);
});

test('the box shows each section and line', () => {
  render(<StillOpen plan={tutPlan} />);
  expect(screen.getByText('What you can still do now')).toBeTruthy();
  expect(screen.getByText('Coming up')).toBeTruthy();
  expect(screen.getAllByText(TUT)).toHaveLength(2);
  expect(screen.getByText('To start in 2028 · opens Thu 1 Apr 2027 · in 170 days')).toBeTruthy();
});

test("a preview's test date is said; the real date says nothing", () => {
  render(<TestDateNote apply={{ ...smuPlan.apply, today: '2026-06-01', test_date: true }} />);
  expect(screen.getByText('Test date: every date here is worked out as if today were Mon 1 Jun 2026. Only a preview does this.')).toBeTruthy();
  expect(render(<TestDateNote apply={{ ...smuPlan.apply, test_date: false }} />).toJSON()).toBeNull();
});
