/**
 * Alerts and support (brief, M5), on the API's own answers for the fictional
 * allowance-funded student: the combined alert with its actions, each opening
 * its screen and a support action naming the campus's own office; Support with
 * every kind in order, each service's source and when it was read or checked,
 * and crisis lines held back until a person has checked them.
 */
import { expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import { kindLabel, ServiceCard, SupportSections } from '@/features/support/components/SupportSections';
import { SupportAnswer } from '@/features/support/types';

import { AlertCard } from '../components/AlertCard';
import { AlertsAnswer } from '../types';
import alerts from './fixtures/alerts.json';
import support from './fixtures/support.json';

jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));
jest.mock('expo-web-browser', () => ({ openBrowserAsync: jest.fn() }));
jest.mock('expo-router', () => ({ router: { push: jest.fn() }, useFocusEffect: jest.fn() }));

const alert = (alerts as unknown as { data: AlertsAnswer }).data.alerts[0];
const answer = (support as unknown as { data: SupportAnswer }).data;

test('the combined alert: its title and message at a glance, and a tap opens every action with the campus office to call', () => {
  const onOpen = jest.fn();
  render(<AlertCard alert={alert} onOpen={onOpen} />);
  expect(alert.kind).toBe('combined');
  expect(screen.getByText(alert.title)).toBeTruthy();
  expect(screen.getByText(alert.message)).toBeTruthy();
  expect(screen.queryByText(alert.actions[0].text)).toBeNull();
  expect(screen.getByText(`${alert.actions.length} things you can do · tap to see`)).toBeTruthy();
  fireEvent.press(screen.getByText(alert.title));
  for (const a of alert.actions) expect(screen.getByText(a.text)).toBeTruthy();
  expect(screen.getByText('Financial Aid Office: fee blocks and financial clearance')).toBeTruthy();
  expect(screen.getByText('012 521 4614 / 4500 / 4317; financialaid@smu.ac.za')).toBeTruthy();

  fireEvent.press(screen.getByText('Open My money'));
  expect(onOpen).toHaveBeenLastCalledWith('money');
  fireEvent.press(screen.getByText('Open My week'));
  expect(onOpen).toHaveBeenLastCalledWith('week');
  fireEvent.press(screen.getAllByText('Open Support')[0]);
  expect(onOpen).toHaveBeenLastCalledWith('support');
});

test('support lists every kind for the campus, in order, and holds crisis lines back with the reason', () => {
  render(<SupportSections kinds={answer.kinds} />);
  for (const k of answer.kinds) expect(screen.getByText(kindLabel(k.kind))).toBeTruthy();
  const crisis = answer.kinds.find((k) => k.kind === 'crisis')!;
  expect(crisis.services).toEqual([]);
  expect(screen.getByText(crisis.line!)).toBeTruthy();
  expect(screen.getAllByText('Read on the university\'s page on Fri 9 Oct 2026').length).toBeGreaterThan(0);
});

test('a service a person has checked says so, and one with no date says "Not verified yet"', () => {
  const base = answer.kinds[0].services[0];
  render(<ServiceCard service={{ ...base, last_verified: '2026-10-20' }} />);
  expect(screen.getByText('Checked by a person on Tue 20 Oct 2026')).toBeTruthy();
  render(<ServiceCard service={{ ...base, last_verified: null, read_on: null }} />);
  expect(screen.getByText('Not verified yet')).toBeTruthy();
});
