/**
 * Steps 2 and 3 on the API's own answer (fixtures/points.json, every
 * university, recorded on Tue 13 Oct 2026 for the marks below): how many
 * programmes the marks meet and where, counting a reach as met; each
 * university's row; the points card naming every subject as the learner
 * chose it; and funding open now, soonest closing first.
 */
import { expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import { ApsCard } from '../components/ApsCard';
import { fundingRow } from '../components/ClosingSoon';
import { metAt, qualifyCounts, UniversityRow } from '../components/Qualify';
import { checkRows, MarkRow } from '../marks';
import { FundingCard, PointsAnswer } from '../types';
import recorded from './fixtures/points.json';

jest.mock('@expo/vector-icons', () => ({ Feather: () => null }));
jest.mock('expo-web-browser', () => ({ openBrowserAsync: jest.fn() }));

// Movement is for people; these tests check what each part says and does, as with reduced motion.
jest.mock('@/shared/motion/motion', () => ({ ...jest.requireActual<object>('@/shared/motion/motion'), motionOff: () => true }));

const points = (recorded as unknown as { data: PointsAnswer }).data;
const tut = points.universities.find((u) => u.university === 'tut')!;
const rows: MarkRow[] = [
  { subject: 'english', percent: '72' },
  { subject: 'isizulu', percent: '64' },
  { subject: 'sepedi', percent: '81' },
  { subject: 'mathematics', percent: '70' },
  { subject: 'physical_sciences', percent: '66' },
  { subject: 'life_sciences', percent: '74' },
  { subject: 'geography', percent: '69' },
  { subject: 'life_orientation', percent: '85' },
];

test('the recorded answer is for these marks, sent as the API takes them', () => {
  const sent = checkRows(rows);
  expect(sent.marks.map((m) => m.subject)).toEqual(tut.subjects.map((s) => s.subject));
  expect(sent.names).toMatchObject({ other_language: 'sepedi', another_subject_1: 'isizulu' });
});

test('programmes met and where, a reach counted as met', () => {
  // SMU: 15 reach of 17; TUT: 14 competitive, 75 meet the minimum, 30 reach of 124; UP: 87 and 20 reach of 120.
  expect(qualifyCounts(points)).toEqual({ programmes: 15 + 119 + 107, universities: 3 });
  expect(metAt(tut)).toEqual({ met: 119, total: 124 });
});

test("each university's row: its name, your points there and how many programmes you meet", () => {
  const onPress = jest.fn();
  render(<UniversityRow u={tut} onPress={onPress} />);
  expect(screen.getByText('Tshwane University of Technology')).toBeTruthy();
  expect(screen.getByText('35')).toBeTruthy();
  expect(screen.getByText('You meet 119 of 124 programmes')).toBeTruthy();
  expect(screen.getByText('Not yet confirmed by the team.')).toBeTruthy();
  fireEvent.press(screen.getByRole('button'));
  expect(onPress).toHaveBeenCalled();
});

test('a university without a points rule or programmes says so, instead of a zero', () => {
  const bare = { ...tut, points: null, subjects: [], tiers: { competitive: 0, meets_minimum: 0, reach: 0, not_yet: 0, unverified: 0 } };
  render(<UniversityRow u={bare} onPress={jest.fn()} />);
  expect(screen.getByText('Programmes not added yet')).toBeTruthy();
  expect(screen.getByText('Counts points its own way')).toBeTruthy();
});

test('a university with only subjects_met programmes says how many subjects meet, not 0 of N', () => {
  const onlySubjectsMet = {
    ...tut,
    tiers: { competitive: 0, meets_minimum: 0, reach: 0, subjects_met: 12, not_yet: 61, unverified: 0 },
  };
  render(<UniversityRow u={onlySubjectsMet} onPress={jest.fn()} />);
  expect(screen.getByText('Your subjects meet 12 of 73 programmes. It counts points its own way.')).toBeTruthy();
  expect(screen.queryByText('You meet 0 of 73 programmes')).toBeNull();
});

test('a university with a mix of met and subjects_met programmes names both', () => {
  const mix = {
    ...tut,
    tiers: { competitive: 2, meets_minimum: 3, reach: 0, subjects_met: 7, not_yet: 61, unverified: 0 },
  };
  render(<UniversityRow u={mix} onPress={jest.fn()} />);
  expect(screen.getByText('You meet 5 of 73 programmes. Your subjects meet 7 whose points it counts its own way.')).toBeTruthy();
});

test('a university with no programmes met says 0 of N programmes', () => {
  const none = {
    ...tut,
    tiers: { competitive: 0, meets_minimum: 0, reach: 0, subjects_met: 0, not_yet: 73, unverified: 0 },
  };
  render(<UniversityRow u={none} onPress={jest.fn()} />);
  expect(screen.getByText('You meet 0 of 73 programmes')).toBeTruthy();
});

test("the points card: TUT's total, how it counts, and each subject named as the learner chose it", () => {
  render(<ApsCard points={tut} sent={checkRows(rows)} rows={rows} />);
  expect(screen.getByText('Your points here')).toBeTruthy();
  expect(screen.getByText('35 points')).toBeTruthy();
  expect(screen.getByText(tut.lines[0])).toBeTruthy();
  fireEvent.press(screen.getByText('See each subject'));
  expect(screen.getByText('Sepedi')).toBeTruthy(); // sent as other_language
  expect(screen.getByText('isiZulu')).toBeTruthy(); // sent as another_subject_1
  expect(screen.getByText('81% · level 7')).toBeTruthy();
  expect(screen.getAllByText('not counted')).toHaveLength(tut.subjects.filter((s) => !s.counted).length);
});

test('funding open now, the soonest closing first; when none is open, the ones opening next', () => {
  const card = (id: string, status: string, days: number | null): FundingCard => ({
    id,
    name: id,
    short_name: null,
    status,
    label: status,
    heading: null,
    opens: null,
    days,
    url: null,
    source_url: null,
  });
  const list = [card('a', 'closed', 3), card('b', 'open', null), card('c', 'closing_soon', 4), card('d', 'open', 20), card('e', 'opens_later', 9)];
  expect(fundingRow(list)).toEqual({ open: true, funders: [list[2], list[3], list[1]] });
  const later = [card('a', 'closed', 3), card('f', 'opens_later', 40), card('e', 'opens_later', 9), card('g', 'check', null)];
  expect(fundingRow(later)).toEqual({ open: false, funders: [later[2], later[1]] });
});
