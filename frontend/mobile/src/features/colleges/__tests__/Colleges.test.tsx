/**
 * Colleges: the list searches as you type (from 3 letters) and opens a college; a college shows its
 * status, number, qualifications and sources, with DHET's warning signs when cancelled; the check
 * answers in words, lists what matched, and never sends fewer than 3 letters.
 */
import { beforeEach, expect, jest, test } from '@jest/globals';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react-native';

import { collegesApi } from '../api/collegesApi';
import CheckCollegeScreen from '../screens/CheckCollegeScreen';
import CollegeScreen from '../screens/CollegeScreen';
import CollegesScreen from '../screens/CollegesScreen';
import { CheckAnswer, CollegeAnswer, CollegeCard, CollegeListAnswer } from '../types';

const mockPush = jest.fn();
let mockParams: Record<string, string> = { id: 'acme-college' };

jest.mock('expo-router', () => ({
  router: { push: (...args: unknown[]) => mockPush(...args), back: jest.fn(), canGoBack: () => true },
  useLocalSearchParams: () => mockParams,
}));
jest.mock('react-native-safe-area-context', () => {
  const actual = jest.requireActual<object>('react-native-safe-area-context');
  return { ...actual, useSafeAreaInsets: () => ({ top: 0, left: 0, right: 0, bottom: 0 }) };
});
jest.mock('expo-web-browser', () => ({ openBrowserAsync: jest.fn() }));
jest.mock('@expo/vector-icons', () => ({ Feather: () => null }));

const acme: CollegeCard = {
  id: 'acme-college',
  name: 'Acme College (Pty) Ltd',
  kind: 'private_college',
  kind_label: 'Private college',
  status: 'registered',
  label: 'Registered',
  registration_number: '2010/FE07/001',
  provinces: ['Gauteng'],
  website: 'www.acme.co.za',
  website_problem: null,
  lines: ['Acme College (Pty) Ltd is registered with the Department of Higher Education and Training (registration number 2010/FE07/001).'],
};
const list = (colleges: CollegeCard[], page = 1, pages = 1): CollegeListAnswer => ({
  summary: `${colleges.length} colleges: ${colleges.length} registered.`,
  total: colleges.length,
  page,
  pages,
  colleges,
  confirmed: false,
  notice: 'Not yet confirmed by the team.',
});

beforeEach(() => {
  jest.restoreAllMocks();
  mockPush.mockClear();
  mockParams = { id: 'acme-college' };
});

test('the list loads, searches from three letters, and opens a college', async () => {
  const listSpy = jest.spyOn(collegesApi, 'list').mockResolvedValue(list([acme]));
  render(<CollegesScreen />);
  expect(await screen.findByText('1 colleges: 1 registered.')).toBeTruthy();
  expect(screen.getByText('Not yet confirmed by the team.')).toBeTruthy();

  fireEvent.changeText(screen.getByLabelText('Search by name, registration number or course'), 'ac');
  expect(screen.getByText('Type at least 3 letters.')).toBeTruthy();
  fireEvent.changeText(screen.getByLabelText('Search by name, registration number or course'), 'acme');
  await waitFor(() => expect(listSpy).toHaveBeenLastCalledWith({ q: 'acme', kind: undefined, province: undefined }), { timeout: 3000 });

  fireEvent.press(screen.getByText('Public TVET'));
  await waitFor(() => expect(listSpy).toHaveBeenLastCalledWith({ q: 'acme', kind: 'tvet', province: undefined }));

  fireEvent.press(screen.getByText('Acme College (Pty) Ltd'));
  expect(mockPush).toHaveBeenCalledWith('/course-finder/colleges/acme-college');
  fireEvent.press(screen.getByText('Is this college registered?'));
  expect(mockPush).toHaveBeenCalledWith('/course-finder/colleges/check');
}, 15000);

test('more colleges load a page at a time', async () => {
  const listSpy = jest.spyOn(collegesApi, 'list')
    .mockResolvedValueOnce(list([acme], 1, 2))
    .mockResolvedValueOnce(list([{ ...acme, id: 'beta', name: 'Beta College' }], 2, 2));
  render(<CollegesScreen />);
  fireEvent.press(await screen.findByText('Show more colleges'));
  expect(await screen.findByText('Beta College')).toBeTruthy();
  expect(screen.getByText('Acme College (Pty) Ltd')).toBeTruthy();
  expect(listSpy).toHaveBeenLastCalledWith({ q: undefined, kind: undefined, province: undefined, page: 2 });
});

test('a college shows its status, number, qualifications, sources and no invented entry rules', async () => {
  const answer: CollegeAnswer = {
    college: {
      ...acme,
      phone: null,
      head_office: null,
      sites: ['27 Main Road, Johannesburg'],
      qualifications: Array.from({ length: 10 }, (_, i) => `National Certificate (Vocational) ${i + 1}`),
      notes: [],
      occupational: [],
      sources: [{ url: 'https://www.dhet.gov.za/r.pdf', publisher: 'DHET', title: 'The Register of Private Colleges', retrieved: '2026-10-20' }],
    },
    warning_signs: null,
    confirmed: false,
    notice: null,
  };
  jest.spyOn(collegesApi, 'college').mockResolvedValue(answer);
  render(<CollegeScreen />);
  expect(await screen.findByText('Registered')).toBeTruthy();
  expect(screen.getByText('2010/FE07/001')).toBeTruthy();
  expect(screen.queryByText('National Certificate (Vocational) 10')).toBeNull();
  fireEvent.press(screen.getByText('Show all 10'));
  expect(screen.getByText('National Certificate (Vocational) 10')).toBeTruthy();
  expect(screen.getByText("Entry requirements aren't in DHET's lists. Ask the college, and keep its answer in writing.")).toBeTruthy();
  expect(screen.getByText('The Register of Private Colleges')).toBeTruthy();
  expect(screen.queryByText('Signs of a bogus college, from DHET')).toBeNull();
});

test('a cancelled college carries DHET’s warning signs', async () => {
  jest.spyOn(collegesApi, 'college').mockResolvedValue({
    college: { ...acme, status: 'cancelled', label: 'Registration cancelled', phone: null, head_office: null, sites: [], qualifications: [], notes: [], occupational: [], sources: [] },
    warning_signs: { items: ['Consultants promising jobs after graduation.'], source_url: 'https://www.dhet.gov.za/p.pdf' },
    confirmed: true,
    notice: null,
  });
  render(<CollegeScreen />);
  expect(await screen.findByText('Signs of a bogus college, from DHET')).toBeTruthy();
  expect(screen.getByText('Consultants promising jobs after graduation.')).toBeTruthy();
});

test('the check answers in words and lists what matched', async () => {
  const answer: CheckAnswer = {
    verdict: 'bogus',
    label: 'Illegal (bogus) college',
    lines: ['DHET lists “Barkley University” as an illegal (bogus) college: it is not registered, so its qualifications are not recognised.'],
    colleges: [],
    unregistered: [{ id: 'barkley-university', name: 'Barkley University', where: 'Global', label: 'Illegal (bogus) college' }],
    warning_signs: { items: ['The absence of a physical address.'], source_url: null },
    sources: [{ url: 'https://www.dhet.gov.za/r.pdf', publisher: 'DHET', title: 'Register of Private Higher Education Institutions', retrieved: '2026-10-20' }],
    confirmed: false,
    notice: null,
  };
  const checkSpy = jest.spyOn(collegesApi, 'check').mockResolvedValue(answer);
  render(<CheckCollegeScreen />);
  const input = screen.getByLabelText("College's name or registration number");

  fireEvent.changeText(input, 'ba');
  fireEvent.press(screen.getByText('Check'));
  expect(checkSpy).not.toHaveBeenCalled();

  fireEvent.changeText(input, '  Barkley  ');
  await act(async () => {
    fireEvent.press(screen.getByText('Check'));
  });
  expect(checkSpy).toHaveBeenCalledWith('Barkley');
  expect(screen.getAllByText('Illegal (bogus) college').length).toBe(2);
  expect(screen.getByText('Where DHET says it operates: Global')).toBeTruthy();
  expect(screen.getByText('The absence of a physical address.')).toBeTruthy();
  expect(screen.getByText('Register of Private Higher Education Institutions')).toBeTruthy();
});


test('a dead or parked website is described, never linked', async () => {
  jest.spyOn(collegesApi, 'college').mockResolvedValue({
    college: {
      ...acme, website: null, phone: null, head_office: null, sites: [], qualifications: [], notes: [], occupational: [], sources: [],
      website_problem: { listed: 'www.parked.co.za', note: 'The address is a parked domain.', checked: '2026-10-20' },
    },
    warning_signs: null, confirmed: false, notice: null,
  });
  render(<CollegeScreen />);
  expect(await screen.findByText(/DHET lists www\.parked\.co\.za, but it isn't the college's working site/)).toBeTruthy();
  expect(screen.queryByRole('link', { name: /parked/ })).toBeNull();
});
