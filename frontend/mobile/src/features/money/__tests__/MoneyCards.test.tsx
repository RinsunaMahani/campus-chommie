/**
 * The runway card and the life fund (brief, M3), on the API's own answers for
 * the fictional demo students: the allowance-funded one runs short before her
 * next payment with a paused life fund, "late" moves the payment 14 days, and
 * the self-funded one has an amber life fund in a heavy week.
 */
import { expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import { LifeFundCard, NextPaymentCard, RunwayCard, SafeToSpendCard } from '../components/MoneyCards';
import { SummaryReady } from '../types';
import naledi from './fixtures/naledi_summary.json';
import nalediLate from './fixtures/naledi_summary_late.json';
import sipho from './fixtures/sipho_summary.json';

// Icons load their font after the render; nothing here is about icons.
jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));

const summary = (recorded: unknown) => (recorded as { data: SummaryReady }).data;

test('the runway card shows the balance now and says the money runs out before the next payment', () => {
  const s = summary(naledi);
  render(<RunwayCard summary={s} />);
  expect(screen.getByText('R610')).toBeTruthy();
  for (const line of s.runway.lines) expect(screen.getByText(line)).toBeTruthy();
  expect(s.runway.short_before_next).toBe(true);
  expect(screen.getByText(s.pace!.lines[0])).toBeTruthy();
});

test('safe to spend says it in rand a day, with the reason', () => {
  const s = summary(naledi);
  render(<SafeToSpendCard summary={s} />);
  expect(screen.getByText('R0 a day')).toBeTruthy();
  expect(screen.getByText(s.safe_to_spend.lines[0])).toBeTruthy();
});

test('a life fund paused by short money says so in words, and when it resumes', () => {
  const s = summary(naledi);
  render(<LifeFundCard summary={s} />);
  expect(screen.getByText('Paused')).toBeTruthy();
  expect(screen.getByText(s.life_fund.reason)).toBeTruthy();
  expect(screen.getByText('Resumes when your next payment lands.')).toBeTruthy();
});

test('a heavy week turns the self-funded student\'s life fund amber: "Go easy"', () => {
  const s = summary(sipho);
  render(<LifeFundCard summary={s} />);
  expect(s.life_fund.state).toBe('amber');
  expect(screen.getByText('Go easy')).toBeTruthy();
  expect(screen.getByText(`This week: ${s.this_week!.reason}`)).toBeTruthy();
});

test('"two weeks late" moves the payment 14 days, and the switch asks for it', () => {
  const now = summary(naledi);
  const late = summary(nalediLate);
  expect(now.next_payment!.lands_on).toBe('2026-10-31');
  expect(late.next_payment!.lands_on).toBe('2026-11-14');

  const onLate = jest.fn();
  render(<NextPaymentCard summary={now} onLate={onLate} />);
  expect(screen.getByText('Living allowance (demo amount)')).toBeTruthy();
  expect(screen.getByText('R1,500')).toBeTruthy();
  expect(screen.getByText('Lands Sat 31 Oct 2026')).toBeTruthy();
  fireEvent(screen.getByRole('switch'), 'valueChange', true);
  expect(onLate).toHaveBeenCalledWith(true);

  render(<NextPaymentCard summary={late} onLate={onLate} />);
  expect(screen.getByText('Lands Sat 14 Nov 2026')).toBeTruthy();
});
