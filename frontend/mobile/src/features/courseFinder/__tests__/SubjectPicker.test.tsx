/**
 * The subject picker: several languages ticked in one go, one folder open at
 * a time, everything handed back on Done; and the API's limits (nine
 * subjects, three points-only, each language at one level) shown on the
 * sheet rather than silently refused.
 */
import { expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import { SubjectPicker } from '../components/SubjectPicker';

jest.mock('@expo/vector-icons', () => ({ Feather: () => null }));
jest.mock('react-native-safe-area-context', () => jest.requireActual<{ default: object }>('react-native-safe-area-context/jest/mock').default);

test('several languages at once, then a subject in another folder, all handed back on Done', () => {
  const onDone = jest.fn();
  render(<SubjectPicker chosen={['english', 'life_orientation']} onDone={onDone} onClose={jest.fn()} />);

  // Languages starts open.
  fireEvent.press(screen.getByText('Sepedi'));
  fireEvent.press(screen.getByText('isiZulu'));
  // The folder lists what is ticked in it, in its own order.
  expect(screen.getByText('English, isiZulu, Sepedi')).toBeTruthy();

  // Opening Mathematics closes Languages.
  fireEvent.press(screen.getByRole('button', { name: 'Mathematics' }));
  expect(screen.queryByText('Sepedi')).toBeNull();
  fireEvent.press(screen.getByRole('checkbox', { name: 'Mathematics' }));

  fireEvent.press(screen.getByText('Done · 5 chosen'));
  expect(onDone).toHaveBeenCalledWith(['english', 'life_orientation', 'sepedi', 'isizulu', 'mathematics']);
});

test('a language chosen at one level is greyed at the other, and the points-only limit is said', () => {
  render(<SubjectPicker chosen={['sepedi', 'sal_french', 'religion_studies', 'marine_sciences']} onDone={jest.fn()} onClose={jest.fn()} />);
  expect(screen.getByText('You can enter up to 3 subjects that count towards your points only.')).toBeTruthy();

  fireEvent.press(screen.getByRole('button', { name: /^Second additional languages/ }));
  expect(screen.getAllByText('Already chosen under Languages')).toHaveLength(1);
  fireEvent.press(screen.getByRole('checkbox', { name: 'Mandarin' }));
  expect(screen.getByText('Done · 4 chosen')).toBeTruthy();

  // Unticking frees a place.
  fireEvent.press(screen.getByRole('checkbox', { name: 'French' }));
  fireEvent.press(screen.getByRole('checkbox', { name: 'Mandarin' }));
  expect(screen.getByText('Done · 4 chosen')).toBeTruthy();
});

test('at nine subjects the rest are greyed and the sheet says why; unticking still works', () => {
  const nine = ['english', 'sepedi', 'mathematics', 'physical_sciences', 'life_sciences', 'geography', 'accounting', 'tourism', 'life_orientation'];
  render(<SubjectPicker chosen={nine} onDone={jest.fn()} onClose={jest.fn()} />);
  expect(screen.getByText('That is 9 subjects, the most you can enter.')).toBeTruthy();
  fireEvent.press(screen.getByText('Afrikaans'));
  expect(screen.getByText('Done · 9 chosen')).toBeTruthy();
  fireEvent.press(screen.getByText('Sepedi'));
  expect(screen.getByText('Done · 8 chosen')).toBeTruthy();
});

test('closing the sheet any other way hands nothing back', () => {
  const onDone = jest.fn();
  const onClose = jest.fn();
  render(<SubjectPicker chosen={[]} onDone={onDone} onClose={onClose} />);
  fireEvent.press(screen.getByText('isiXhosa'));
  fireEvent.press(screen.getByLabelText('Close'));
  expect(onClose).toHaveBeenCalled();
  expect(onDone).not.toHaveBeenCalled();
});
