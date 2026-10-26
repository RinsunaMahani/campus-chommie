/**
 * api() extra headers: sent, never able to replace the token, and sent
 * again unchanged on the retry after a token refresh (so a retried save
 * keeps its Idempotency-Key).
 */
import { beforeEach, expect, jest, test } from '@jest/globals';

import { api, newIdempotencyKey, NO_CONNECTION, onSlowRequests, TIMED_OUT, wakeServer } from '../client';

let mockTokens: { accessToken: string; refreshToken: string } | null = { accessToken: 'old', refreshToken: 'r1' };
jest.mock('../tokenStore', () => ({
  getTokens: async () => mockTokens,
  setTokens: async (t: typeof mockTokens) => {
    mockTokens = t;
  },
  clearTokens: async () => {
    mockTokens = null;
  },
}));

type Call = { url: string; headers: Record<string, string> };
let calls: Call[] = [];

function respond(status: number, body: object) {
  return Promise.resolve({ status, json: () => Promise.resolve(body) });
}

beforeEach(() => {
  calls = [];
  mockTokens = { accessToken: 'old', refreshToken: 'r1' };
});

test('extra headers are sent and cannot replace the token', async () => {
  global.fetch = jest.fn((url: string, init: { headers: Record<string, string> }) => {
    calls.push({ url, headers: init.headers });
    return respond(201, { success: true, data: { ok: 1 } });
  }) as unknown as typeof fetch;

  await api('POST', '/money/spending', { a: 1 }, { auth: true, headers: { 'Idempotency-Key': 'k-1', Authorization: 'Bearer forged' } });

  expect(calls[0].headers['Idempotency-Key']).toBe('k-1');
  expect(calls[0].headers.Authorization).toBe('Bearer old');
});

test('the retry after a token refresh sends the same Idempotency-Key', async () => {
  global.fetch = jest.fn((url: string, init: { headers: Record<string, string> }) => {
    calls.push({ url, headers: init.headers });
    if (url.endsWith('/auth/refresh')) return respond(200, { success: true, data: { access_token: 'new', refresh_token: 'r2' } });
    if (init.headers.Authorization === 'Bearer old') return respond(401, { success: false, code: 'TOKEN_EXPIRED' });
    return respond(201, { success: true, data: { saved: true } });
  }) as unknown as typeof fetch;

  const out = await api<{ saved: boolean }>('POST', '/money/spending', { a: 1 }, { auth: true, headers: { 'Idempotency-Key': 'k-2' } });

  const saves = calls.filter((c) => c.url.endsWith('/spending'));
  expect(out.saved).toBe(true);
  expect(saves).toHaveLength(2);
  expect(saves.map((c) => c.headers['Idempotency-Key'])).toEqual(['k-2', 'k-2']);
  expect(saves[1].headers.Authorization).toBe('Bearer new');
});

test('idempotency keys are unique', () => {
  const keys = new Set(Array.from({ length: 1000 }, newIdempotencyKey));
  expect(keys.size).toBe(1000);
});

// ------------------------------------------------- a server waking up

test('a read that finds no connection is tried once more, and then succeeds', async () => {
  let n = 0;
  global.fetch = jest.fn(() => {
    n += 1;
    return n === 1 ? Promise.reject(new TypeError('Network request failed')) : respond(200, { success: true, data: { ok: 1 } });
  }) as unknown as typeof fetch;
  await expect(api('GET', '/universities')).resolves.toEqual({ ok: 1 });
  expect(n).toBe(2);
});

test('a write is never sent twice by the client', async () => {
  let n = 0;
  global.fetch = jest.fn(() => {
    n += 1;
    return Promise.reject(new TypeError('Network request failed'));
  }) as unknown as typeof fetch;
  await expect(api('POST', '/money/spending', { a: 1 })).rejects.toMatchObject({ code: 'NETWORK', message: NO_CONNECTION });
  expect(n).toBe(1);
});

test('a slow request tells the app, and the all-clear comes when it ends', async () => {
  jest.useFakeTimers();
  const seen: boolean[] = [];
  const stop = onSlowRequests((s) => seen.push(s));
  let answer: (v: unknown) => void = () => undefined;
  global.fetch = jest.fn(() => new Promise((r) => (answer = r))) as unknown as typeof fetch;
  const pending = api('GET', '/universities');
  await jest.advanceTimersByTimeAsync(5000);
  expect(seen).toEqual([true]);
  answer({ status: 200, json: () => Promise.resolve({ success: true, data: {} }) });
  await pending;
  expect(seen).toEqual([true, false]);
  stop();
  jest.useRealTimers();
});

test('a request that times out says the server is taking long, not that the phone is offline', async () => {
  jest.useFakeTimers();
  global.fetch = jest.fn(
    (_url: string, init: { signal: AbortSignal }) =>
      new Promise((_r, reject) => init.signal.addEventListener('abort', () => reject(new Error('aborted')))),
  ) as unknown as typeof fetch;
  const pending = api('POST', '/money/spending', { a: 1 });
  const check = expect(pending).rejects.toMatchObject({ code: 'NETWORK', message: TIMED_OUT });
  await jest.advanceTimersByTimeAsync(31000);
  await check;
  jest.useRealTimers();
});

test('opening the app wakes the database too, and a failure there is silent', async () => {
  const fetchMock = jest.fn(() => Promise.reject(new Error('offline')));
  global.fetch = fetchMock as unknown as typeof fetch;
  wakeServer();
  await Promise.resolve();
  expect(fetchMock).toHaveBeenCalledTimes(1);
  expect(String((fetchMock.mock.calls[0] as unknown[])[0])).toMatch(/\/health$/);
});
