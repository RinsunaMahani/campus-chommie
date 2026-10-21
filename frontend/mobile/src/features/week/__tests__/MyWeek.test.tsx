/**
 * My week (brief, M4), on the API's own answers for the fictional demo
 * students: the week strip says each week's load in words, the rep panel and
 * the confirm form work as a rep needs them, events show flags as counts (never
 * who), and the marks cards say where a student stands.
 */
import { expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import { CandidateForm } from '@/features/classes/components/CandidateForm';
import { RepPanel } from '@/features/classes/components/RepPanel';
import { Candidate } from '@/features/classes/types';
import { ProjectionCard, StandingCard } from '@/features/marks/components/ModuleCards';
import { Module } from '@/features/marks/types';

import { EventCard } from '../components/EventCard';
import { WeekStrip } from '../components/WeekStrip';
import { ClassEvent, WeekAnswer } from '../types';
import candidates from './fixtures/candidates.json';
import eventsRep from './fixtures/events_rep.json';
import modules from './fixtures/modules.json';
import week from './fixtures/week.json';

jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));
jest.mock('expo-web-browser', () => ({ openBrowserAsync: jest.fn() }));

const weeks = (week as unknown as { data: WeekAnswer }).data.weeks;
const candidate = (candidates as unknown as { data: { candidates: Candidate[] } }).data.candidates[0];
const repEvents = (eventsRep as unknown as { data: { events: ClassEvent[] } }).data.events;
const module = (modules as unknown as { data: { modules: Module[] } }).data.modules[0];

test("the week strip says each week's load in words, with its reason, and opens the week", () => {
  const onOpen = jest.fn();
  render(<WeekStrip weeks={weeks} onOpen={onOpen} />);
  expect(screen.getByText('This week')).toBeTruthy();
  expect(screen.getAllByText('Heavy').length).toBeGreaterThan(0);
  expect(screen.getByText(weeks[0].reason)).toBeTruthy();
  fireEvent.press(screen.getByText('This week'));
  expect(onOpen).toHaveBeenCalledWith(weeks[0]);
});

test('the rep panel: messages waiting, pasting a message, and a rep code shown once', () => {
  const onCheck = jest.fn();
  const onMakeRepCode = jest.fn();
  const { rerender } = render(
    <RepPanel waiting={1} onCheck={onCheck} onAnnounce={() => undefined} repCode={null} onMakeRepCode={onMakeRepCode} />,
  );
  expect(screen.getByText('Messages to check: 1')).toBeTruthy();
  fireEvent.press(screen.getByText('Check it'));
  expect(onCheck).toHaveBeenCalled();
  fireEvent.press(screen.getByText('Make a rep code'));
  expect(onMakeRepCode).toHaveBeenCalled();

  rerender(
    <RepPanel
      waiting={0}
      onCheck={onCheck}
      onAnnounce={() => undefined}
      repCode={{ code: 'R7K2P9', expires_at: '2026-10-15T12:00:00+02:00', lines: ['Give this code to the classmate who will be a rep.'] }}
      onMakeRepCode={onMakeRepCode}
    />,
  );
  expect(screen.queryByText('Check it')).toBeNull();
  expect(screen.getByText(/Rep code: R7K2P9/)).toBeTruthy();
  expect(screen.queryByText('Make a rep code')).toBeNull();
});

test("the confirm form starts from what the engine read, and confirms it as the class's event", () => {
  const onConfirm = jest.fn();
  render(<CandidateForm candidate={candidate} events={[]} onConfirm={onConfirm} onDiscard={() => undefined} />);
  expect(screen.getByText(candidate.text)).toBeTruthy();
  expect(screen.getByText(candidate.lines[0])).toBeTruthy();
  expect(screen.getByDisplayValue('Quiz 5')).toBeTruthy();
  expect(screen.getByDisplayValue('10:00')).toBeTruthy();
  expect(screen.getByDisplayValue('Lab C3')).toBeTruthy();
  fireEvent.press(screen.getByText('Confirm'));
  expect(onConfirm).toHaveBeenCalledWith({
    change: null,
    event_id: null,
    kind: 'quiz',
    title: 'Quiz 5',
    on: '2026-10-16',
    at: '10:00',
    venue: 'Lab C3',
    weighting: null,
  });
});

test('fields the engine was unsure of are marked in words, and a bad time is refused', () => {
  const unsure: Candidate = { ...candidate, needs_check: ['at', 'venue'] };
  const onConfirm = jest.fn();
  render(<CandidateForm candidate={unsure} events={[]} onConfirm={onConfirm} onDiscard={() => undefined} />);
  expect(screen.getAllByText('Check this')).toHaveLength(2);
  fireEvent.changeText(screen.getByDisplayValue('10:00'), '25:00');
  fireEvent.press(screen.getByText('Confirm'));
  expect(screen.getByText('Enter a time as HH:MM, like 14:00.')).toBeTruthy();
  expect(onConfirm).not.toHaveBeenCalled();
});

test('a rep sees how many flagged an event and why, never who; a student sees their own flag', () => {
  const flagged: ClassEvent = { ...repEvents[0], flags: { count: 2, reasons: { wrong_date: 2 } } };
  render(<EventCard event={flagged} />);
  expect(screen.getByText('Flagged by 2: Wrong date (2)')).toBeTruthy();
  expect(screen.getByText(flagged.when)).toBeTruthy();

  const mine: ClassEvent = { ...repEvents[0], flags: undefined, your_flag: 'wrong_venue' };
  const onFlag = jest.fn();
  render(<EventCard event={mine} onFlag={onFlag} />);
  expect(screen.getByText('You flagged it: Wrong venue')).toBeTruthy();
  fireEvent.press(screen.getByText('Take my flag back'));
  expect(onFlag).toHaveBeenCalledWith(null);
});

test('a module says where the student stands and where they are heading, in the server’s words', () => {
  render(<StandingCard module={module} />);
  expect(screen.getByText(module.standing.message)).toBeTruthy();
  expect(screen.getByText('Target 65%')).toBeTruthy();
  render(<ProjectionCard module={module} />);
  expect(screen.getByText('About 69%')).toBeTruthy();
  expect(screen.getByText('Likely 68% to 71%')).toBeTruthy();
  expect(screen.getByText(module.projection!.message)).toBeTruthy();
});
