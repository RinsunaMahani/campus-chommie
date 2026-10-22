/**
 * Support's Call and Email buttons: the number and address come exactly from the contact the university
 * published (real formats from the data packs), short codes are never dialled, and a service with no number
 * or address has no button. The name splits from what the service is for.
 */
import { expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';
import { Linking } from 'react-native';

import { firstEmail, firstPhone, ServiceCard, splitName } from '../components/SupportSections';
import { Service } from '../types';

jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));
jest.mock('expo-web-browser', () => ({ openBrowserAsync: jest.fn() }));

test.each([
  ['012 521 4614 / 4500 / 4317; financialaid@smu.ac.za', '0125214614'],
  ['012 382 6611/6613', '0123826611'],
  ['012 521 3786; administrator 012 521 4225', '0125213786'],
  ['Kitsi Taunyana, 018 700 3347', '0187003347'],
  ['0800 68 78 88', '0800687888'],
  ['Toll-free 08000 67327, USSD *134*67327#, info@nsfas.org.za', '0800067327'],
  ['0800 747 747; SMS 31393 for a call-back', '0800747747'],
  ['Campus control for ambulance services, or 079 417 9546 / 6278', '0794179546'],
  ['Bursaryadministrator@clicksgroup.co.za; help registering: 010 140 3099', '0101403099'],
  ['counselling@tut.ac.za', null],
  ["On campus; SMU names horticulturist Mpho Mmako as the project's representative", null],
  [null, null],
])('the number to call in %p is %p', (contact, phone) => {
  expect(firstPhone(contact)).toBe(phone);
});

test('the email address is the first one written', () => {
  expect(firstEmail('012 382 5750 or 012 382 5780, admission@tut.ac.za')).toBe('admission@tut.ac.za');
  expect(firstEmail('bursary@ndmc.gov.za or 012 065 1022/1021; technical help: helpdesk@ndmc.gov.za')).toBe('bursary@ndmc.gov.za');
  expect(firstEmail('012 521 5735')).toBeNull();
});

test('a name splits from what the service is for, only at a colon after the name', () => {
  expect(splitName('Financial Aid Office: fee blocks and financial clearance')).toEqual([
    'Financial Aid Office',
    'Fee blocks and financial clearance.',
  ]);
  expect(splitName('Campus Health and Wellness Centre: minor ailments, peer health education (free)')).toEqual([
    'Campus Health and Wellness Centre',
    'Minor ailments, peer health education (free)',
  ]);
  expect(splitName('Student Counselling')).toEqual(['Student Counselling', null]);
});

const service: Service = {
  name: 'Financial Aid Office: fee blocks and financial clearance',
  contact: '012 521 4614 / 4500 / 4317; financialaid@smu.ac.za',
  hours: null,
  note: null,
  source_url: 'https://www.smu.ac.za/',
  read_on: '2026-10-11',
  last_verified: null,
};

test('Call and Email open the phone and mail apps with exactly the published number and address', () => {
  const open = jest.spyOn(Linking, 'openURL').mockResolvedValue(true);
  render(<ServiceCard service={service} />);
  expect(screen.getByText('Financial Aid Office')).toBeTruthy();
  expect(screen.getByText('Fee blocks and financial clearance.')).toBeTruthy();
  expect(screen.getByText(service.contact!)).toBeTruthy();
  fireEvent.press(screen.getByText('Call'));
  expect(open).toHaveBeenLastCalledWith('tel:0125214614');
  fireEvent.press(screen.getByText('Email'));
  expect(open).toHaveBeenLastCalledWith('mailto:financialaid@smu.ac.za');
});

test('a service with no number or address has no buttons', () => {
  render(<ServiceCard service={{ ...service, contact: 'On campus' }} />);
  expect(screen.queryByText('Call')).toBeNull();
  expect(screen.queryByText('Email')).toBeNull();
});
