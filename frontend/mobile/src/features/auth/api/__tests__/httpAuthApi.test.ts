/**
 * Sign-up sends exactly what the backend's RegisterSchema expects,
 * including the 18-or-older confirmation (the server refuses anything
 * but true), and the mock refuses the same way the server does.
 */
import { beforeEach, expect, jest, test } from '@jest/globals';

import { PRIVACY_POLICY } from '@/content/legal/privacyPolicy';
import { TERMS_OF_USE } from '@/content/legal/termsOfUse';

import { httpAuthApi } from '../httpAuthApi';
import { mockAuthApi } from '../mockAuthApi';

jest.mock('@/shared/api/tokenStore', () => ({
  getTokens: async () => null,
  setTokens: async () => undefined,
  clearTokens: async () => undefined,
}));
jest.mock('@/shared/api/trustedPhone', () => ({
  getTrustedToken: async () => null,
  setTrustedToken: async () => undefined,
  phoneInfo: () => ({ platform: 'android', label: 'Test phone' }),
}));

let bodies: unknown[] = [];

beforeEach(() => {
  bodies = [];
  global.fetch = jest.fn((_url: string, init: { body?: string }) => {
    bodies.push(init.body ? JSON.parse(init.body) : undefined);
    return Promise.resolve({ status: 202, json: () => Promise.resolve({ success: true, data: {} }) });
  }) as unknown as typeof fetch;
});

const consent = { privacyVersion: PRIVACY_POLICY.version, termsVersion: TERMS_OF_USE.version, acceptedAt: '2026-10-09T10:00:00.000Z' };

test('sign-up sends the documents and the 18-or-older confirmation', async () => {
  await httpAuthApi.createAccount({ email: 'lindiwe@example.com', password: 'Campus2026!', consent, confirmed18OrOlder: true });
  expect(bodies[0]).toEqual({
    email: 'lindiwe@example.com',
    password: 'Campus2026!',
    consent: { privacy_version: PRIVACY_POLICY.version, terms_version: TERMS_OF_USE.version, confirmed_18_or_older: true },
  });
});

test('the mock refuses a sign-up without the confirmation, like the server', async () => {
  await expect(
    mockAuthApi.createAccount({ email: 'lindiwe@example.com', password: 'Campus2026!', consent, confirmed18OrOlder: false }),
  ).rejects.toMatchObject({ code: 'AGE_NOT_CONFIRMED' });
});
