/**
 * The moving parts say what they are to a screen reader: tabs are tabs with
 * the chosen one selected, an opening section is a button that says whether
 * it's open, and a carousel shows every card. Movement aside, each works
 * with a tap.
 */
import { expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';
import { Text } from 'react-native';

import { Expandable } from '../Expandable';
import { SlidingTabs } from '../SlidingTabs';
import { SnapCarousel } from '../SnapCarousel';

jest.mock('@expo/vector-icons', () => ({ Feather: () => null }));

// Movement is for people; these tests check what each part says and does, as with reduced motion.
jest.mock('@/shared/motion/motion', () => ({ ...jest.requireActual<object>('@/shared/motion/motion'), motionOff: () => true }));

test('sliding tabs: the chosen tab is selected, and a tap chooses another', () => {
  const onChange = jest.fn();
  render(<SlidingTabs tabs={['Courses', 'How to apply']} index={0} onChange={onChange} />);
  expect(screen.getByRole('tab', { name: 'Courses', selected: true })).toBeTruthy();
  expect(screen.getByRole('tab', { name: 'How to apply', selected: false })).toBeTruthy();
  fireEvent.press(screen.getByRole('tab', { name: 'How to apply' }));
  expect(onChange).toHaveBeenCalledWith(1);
});

test('an opening section says whether it is open, and changes its words', () => {
  render(
    <Expandable closedLabel="See each subject" openLabel="Hide the subjects" color="#1E1B4B">
      <Text>English</Text>
    </Expandable>,
  );
  expect(screen.getByRole('button', { name: 'See each subject', expanded: false })).toBeTruthy();
  fireEvent.press(screen.getByRole('button'));
  expect(screen.getByRole('button', { name: 'Hide the subjects', expanded: true })).toBeTruthy();
});

test('a carousel shows every card', () => {
  render(<SnapCarousel items={['NSFAS', 'Funza Lushaka']} cardWidth={240} keyOf={(s) => s} label="Funding" render={(s) => <Text>{s}</Text>} />);
  expect(screen.getByText('NSFAS')).toBeTruthy();
  expect(screen.getByText('Funza Lushaka')).toBeTruthy();
});
