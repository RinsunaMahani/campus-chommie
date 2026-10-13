/**
 * The tier card (brief, M2): the tier in words, never colour alone; every
 * "why" line; the source, or that nobody has checked it; and the notice while
 * the university's data is unchecked. The answer is the API's own, recorded
 * for the strong SMU learner of the backend tests (fixtures/assess.json).
 */
import { expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import { host, SourceLink } from '../components/SourceLink';
import { TierCard } from '../components/TierCard';
import { AssessAnswer, Match } from '../types';
import recorded from './fixtures/assess.json';

jest.mock('expo-web-browser', () => ({ openBrowserAsync: jest.fn() }));
// Icons load their font after the render; nothing here is about icons.
jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));

const answer = (recorded as unknown as { data: AssessAnswer }).data;
const match = answer.matches[0];

test('a card says its tier in words, every why line, its source and the notice', () => {
  render(<TierCard match={match} />);
  expect(screen.getByText(match.label)).toBeTruthy();
  expect(screen.getByText(match.programme_name)).toBeTruthy();
  for (const line of match.explanation) expect(screen.getByText(line)).toBeTruthy();
  expect(screen.getByText(`Source: ${host(match.source_url!)}`)).toBeTruthy();
  expect(screen.getByText('Not yet confirmed by the team.')).toBeTruthy();
});

test('a learner short of a requirement sees it, and a card without a source says so', () => {
  const short: Match = {
    ...match,
    tier: 'not_yet',
    label: 'Not yet',
    failed: ['Mathematics: 48% (needs 60%).'],
    explanation: ['Your points: 31 (minimum 38).', 'Mathematics: 48% (needs 60%).'],
    source_url: null,
    confirmed: true,
    notice: null,
  };
  render(<TierCard match={short} />);
  expect(screen.getByText('Not yet')).toBeTruthy();
  expect(screen.getByText('Mathematics: 48% (needs 60%).')).toBeTruthy();
  expect(screen.getByText('Source not verified yet')).toBeTruthy();
  expect(screen.queryByText('Not yet confirmed by the team.')).toBeNull();
});

test('choosing a programme as the goal asks for its plan', () => {
  const onPick = jest.fn();
  render(<TierCard match={match} onPick={onPick} />);
  fireEvent.press(screen.getByText('Plan with this as my goal'));
  expect(onPick).toHaveBeenCalledTimes(1);
});

test('a source shows only its site, so a long address never crowds the card', () => {
  expect(host('https://www.smu.ac.za/students/apply/online-application/')).toBe('smu.ac.za');
  render(<SourceLink url="https://nsfas.org.za/content/how-to-apply.html" />);
  expect(screen.getByText('Source: nsfas.org.za')).toBeTruthy();
});
