/**
 * Home -> WhatsApp: off until the bot is switched on; then a one-time code with the message to send and a button
 * that opens WhatsApp with it typed; a linked number says since when and can be unlinked.
 */
import { beforeEach, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import * as Linking from 'expo-linking';

import { whatsappApi } from '../api/whatsappApi';
import WhatsAppScreen from '../screens/WhatsAppScreen';
import { LinkCode, WhatsAppStatus } from '../types';

jest.mock('@expo/vector-icons', () => ({ Feather: () => null, FontAwesome: () => null }));
jest.mock('expo-linking', () => ({ openURL: jest.fn() }));
jest.mock('expo-router', () => ({
  router: { push: jest.fn(), back: jest.fn(), canGoBack: () => true },
  useFocusEffect: (cb: () => void) => {
    const React = jest.requireActual<typeof import('react')>('react');
    React.useEffect(() => {
      cb();
    }, [cb]);
  },
}));
jest.mock('react-native-safe-area-context', () => {
  const actual = jest.requireActual<object>('react-native-safe-area-context');
  return { ...actual, useSafeAreaInsets: () => ({ top: 0, left: 0, right: 0, bottom: 0 }) };
});

const bot = { number: '+1 555 010 0000', chat_link: 'https://wa.me/15550100000' };
const on: WhatsAppStatus = { available: true, linked: 0, linked_on: [], bot };
const code: LinkCode = {
  code: 'ABCD-EFGH',
  message: 'LINK ABCD-EFGH',
  expires_at: '2026-10-23T10:10:00Z',
  minutes: 10,
  bot,
  send_link: 'https://wa.me/15550100000?text=LINK%20ABCD-EFGH',
};

beforeEach(() => {
  jest.restoreAllMocks();
});

test('switched off, it says so and offers no button', async () => {
  jest.spyOn(whatsappApi, 'status').mockResolvedValue({ available: false, linked: 0, linked_on: [], bot: null });
  render(<WhatsAppScreen />);
  expect(await screen.findByText(/isn’t switched on yet/)).toBeTruthy();
  expect(screen.queryByText('Link WhatsApp')).toBeNull();
});

test('a code comes with the message to send, and the button opens WhatsApp with it typed', async () => {
  jest.spyOn(whatsappApi, 'status').mockResolvedValue(on);
  jest.spyOn(whatsappApi, 'code').mockResolvedValue(code);
  render(<WhatsAppScreen />);
  fireEvent.press(await screen.findByText('Link WhatsApp'));
  expect(await screen.findByText('ABCD-EFGH')).toBeTruthy();
  expect(screen.getByText(/Send “LINK ABCD-EFGH” to \+1 555 010 0000 on WhatsApp\. The code works once, for 10 minutes\./)).toBeTruthy();
  fireEvent.press(screen.getByText('Open WhatsApp and send it'));
  expect(Linking.openURL).toHaveBeenCalledWith(code.send_link);
  expect(screen.getByText(/never asks for passwords/)).toBeTruthy();
});

test('a linked number says since when, and unlinking asks the server', async () => {
  jest.spyOn(whatsappApi, 'status').mockResolvedValueOnce({ ...on, linked: 1, linked_on: ['2026-10-23'] }).mockResolvedValue(on);
  const unlink = jest.spyOn(whatsappApi, 'unlink').mockResolvedValue({});
  render(<WhatsAppScreen />);
  expect(await screen.findByText(/A WhatsApp number is linked \(since/)).toBeTruthy();
  fireEvent.press(screen.getByText('Unlink WhatsApp'));
  await waitFor(() => expect(unlink).toHaveBeenCalled());
  expect(await screen.findByText('Link WhatsApp')).toBeTruthy();
});
