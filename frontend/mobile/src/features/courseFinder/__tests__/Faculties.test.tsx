/**
 * Step 3's Courses tab grouped by faculty: which faculty comes first, the
 * counts said in words, the picture chosen from the programmes' fields, and
 * a section that opens and closes.
 */
import { expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';
import { Text } from 'react-native';

import { facultyCounts, FacultySection } from '../components/FacultySection';
import { artFor, groupByFaculty, hasFaculties } from '../faculties';
import { Match, Tier } from '../types';

jest.mock('@expo/vector-icons', () => ({ Feather: () => null }));
jest.mock('@/shared/motion/motion', () => ({ ...jest.requireActual<object>('@/shared/motion/motion'), motionOff: () => true }));

function match(programme: string, tier: Tier, faculty: string | null, fields: string[] = []): Match {
  return {
    university: 'test',
    university_name: 'Test University',
    programme,
    programme_name: programme.toUpperCase(),
    tier,
    label: tier,
    selective: tier === 'reach',
    faculty,
    fields,
    points: 30,
    min_points: 28,
    gap: null,
    failed: [],
    explanation: [],
    source_url: null,
    confirmed: false,
    notice: null,
  } as Match;
}

const matches = [
  match('mbchb', 'reach', 'Faculty of Health Sciences', ['medicine', 'health_sciences']),
  match('bcom', 'meets_minimum', 'Faculty of Commerce', ['commerce']),
  match('bacc', 'competitive', 'Faculty of Commerce', ['accounting', 'commerce']),
  match('bnurs', 'meets_minimum', 'Faculty of Health Sciences', ['nursing']),
  match('bsw', 'not_yet', null, ['humanities']),
  match('bpharm', 'meets_minimum', 'Faculty of Health Sciences', ['pharmacy']),
];

test('faculties with more programmes the learner meets come first; unnamed ones go last', () => {
  const groups = groupByFaculty(matches);
  // Both meet 2; Health also has a reach, so it comes first.
  expect(groups.map((g) => g.faculty)).toEqual(['Faculty of Health Sciences', 'Faculty of Commerce', null]);
  const health = groups[0];
  expect([health.meets, health.reach, health.matches.map((m) => m.programme)]).toEqual([2, 1, ['mbchb', 'bnurs', 'bpharm']]);
});

test('more programmes met wins before reaches count', () => {
  const groups = groupByFaculty(matches.filter((m) => m.programme !== 'bpharm'));
  expect(groups.map((g) => g.faculty)).toEqual(['Faculty of Commerce', 'Faculty of Health Sciences', null]);
  const tied = groupByFaculty([matches[0], matches[1]]);
  expect(tied.map((g) => g.faculty)).toEqual(['Faculty of Commerce', 'Faculty of Health Sciences']);
});

test('a group takes the picture most of its fields share', () => {
  expect(artFor([matches[0], matches[3], matches[5]])).toBe('health');
  expect(artFor([matches[1], matches[2]])).toBe('commerce');
  expect(artFor([match('x', 'not_yet', null, ['unknown_field'])])).toBe('other');
});

test('grouping only when some programme names its faculty', () => {
  expect(hasFaculties(matches)).toBe(true);
  expect(hasFaculties([matches[4]])).toBe(false);
});

test('counts are words, never colour alone', () => {
  const [health, commerce, other] = groupByFaculty(matches);
  expect(facultyCounts(commerce)).toBe('2 meet the minimum · 2 programmes');
  expect(facultyCounts(health)).toBe('2 meet the minimum · 1 reach · 3 programmes');
  expect(facultyCounts(other)).toBe('1 programme');
});

test('a section names its faculty and opens to its programmes', () => {
  const [health, , other] = groupByFaculty(matches);
  render(
    <>
      <FacultySection group={health} startOpen={false}>
        <Text>MBCHB card</Text>
      </FacultySection>
      <FacultySection group={other} startOpen>
        <Text>BSW card</Text>
      </FacultySection>
    </>,
  );
  expect(screen.getByText('Faculty of Health Sciences')).toBeTruthy();
  expect(screen.getByText('Other programmes')).toBeTruthy();
  expect(screen.queryByText('MBCHB card')).toBeNull();
  expect(screen.getByText('BSW card')).toBeTruthy();
  fireEvent.press(screen.getByLabelText('Faculty of Health Sciences. 2 meet the minimum · 1 reach · 3 programmes'));
  expect(screen.getByText('MBCHB card')).toBeTruthy();
});
