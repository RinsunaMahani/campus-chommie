/**
 * The one way the app talks to the Campus Chommie API.
 *
 *  - Speaks the backend's envelope: {success, message, data, code}.
 *    Failures become an ApiError with the server's stable `code`.
 *  - Attaches the access token. When it has expired, refreshes ONCE (even
 *    if several requests fail together) and retries.
 *  - If the session was ended elsewhere (logout, password change, new
 *    phone, stolen token detected), tells the app to sign out.
 *  - Times out instead of hanging on a bad network. The free server can take up to a minute to wake after a
 *    restart, so a slow request tells the app (it shows "Waking up the server"), and a read (GET) that times out
 *    or finds no connection is tried once more before giving up. Writes are never repeated here.
 *  - Extra headers per call (e.g. Idempotency-Key), kept on the retry.
 *  - A FormData body (a file upload) goes as multipart: fetch sets its content type and boundary.
 */
import { API_BASE_URL } from '@/constants/config';

import { clearTokens, getTokens, setTokens } from './tokenStore';

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public data?: Record<string, unknown>,
    /** The server's field errors on a 422 (marshmallow's shape, nested by section). */
    public errors?: unknown,
  ) {
    super(message);
  }
}

type Envelope<T> = { success: boolean; message?: string; data?: T; code?: string; errors?: unknown };

const TIMEOUT_MS = 30000;
/** After this long a request counts as slow: the app says the server is waking up. */
const SLOW_MS = 4000;

/** "Slow" listeners: told when the first request turns slow and when the last slow one ends. */
const slowListeners = new Set<(slow: boolean) => void>();
let slowCount = 0;

export function onSlowRequests(listener: (slow: boolean) => void): () => void {
  slowListeners.add(listener);
  return () => slowListeners.delete(listener);
}

function slow(delta: 1 | -1) {
  const was = slowCount > 0;
  slowCount = Math.max(0, slowCount + delta);
  if (was !== slowCount > 0) slowListeners.forEach((l) => l(slowCount > 0));
}

/** Opening the app: a quick ping so the server starts waking while the student reads the first screen. */
export function wakeServer(): void {
  fetch(`${API_BASE_URL}/ping`, { method: 'GET' }).catch(() => undefined);
}

export const TIMED_OUT = 'Campus Chommie is taking long to answer. Try again in a minute.';
export const NO_CONNECTION = "Can't reach Campus Chommie. Check your connection and try again.";

let onSessionEnded: (() => void) | null = null;
/** The session provider registers how to sign out when the server says the session is over. */
export function setSessionEndedHandler(handler: (() => void) | null) {
  onSessionEnded = handler;
}

type Headers = Record<string, string>;

async function raw<T>(method: string, path: string, body?: unknown, token?: string, extra: Headers = {}): Promise<{ status: number; json: Envelope<T> }> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  let isSlow = false;
  const slowTimer = setTimeout(() => {
    isSlow = true;
    slow(1);
  }, SLOW_MS);
  const form = typeof FormData !== 'undefined' && body instanceof FormData;
  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: {
        // The caller's extras first: they can never replace the token or content type.
        ...extra,
        ...(form ? {} : { 'Content-Type': 'application/json' }),
        Accept: 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: body === undefined ? undefined : form ? (body as FormData) : JSON.stringify(body),
      signal: controller.signal,
    });
    let json: Envelope<T>;
    try {
      json = (await res.json()) as Envelope<T>;
    } catch {
      json = { success: false, message: 'Unexpected response from the server.', code: 'BAD_RESPONSE' };
    }
    return { status: res.status, json };
  } catch {
    throw new ApiError(0, 'NETWORK', controller.signal.aborted ? TIMED_OUT : NO_CONNECTION);
  } finally {
    clearTimeout(timer);
    clearTimeout(slowTimer);
    if (isSlow) slow(-1);
  }
}

let refreshing: Promise<boolean> | null = null;

/** A read that times out or finds no connection gets one more try (the server may have been waking up). */
async function readOnceMore<T>(method: string, path: string, body?: unknown, token?: string, extra: Headers = {}) {
  try {
    return await raw<T>(method, path, body, token, extra);
  } catch (e) {
    if (e instanceof ApiError && e.status === 0) return raw<T>(method, path, body, token, extra);
    throw e;
  }
}

/** Single-flight refresh: concurrent 401s share one refresh call. */
async function refreshTokens(): Promise<boolean> {
  if (!refreshing) {
    refreshing = (async () => {
      const tokens = await getTokens();
      if (!tokens) return false;
      const { status, json } = await raw<{ access_token: string; refresh_token: string }>('POST', '/auth/refresh', undefined, tokens.refreshToken);
      if (status === 200 && json.data) {
        await setTokens({ accessToken: json.data.access_token, refreshToken: json.data.refresh_token });
        return true;
      }
      return false;
    })().finally(() => {
      refreshing = null;
    });
  }
  return refreshing;
}

/**
 * A key for one user action (one tap on Save). Send it as Idempotency-Key
 * so a retry after a dropped connection is saved once, not twice. Make it
 * when the user taps, and reuse it if the same save is tried again.
 * Not a secret: the server ties it to the signed-in user, the route and
 * the request body, so it only has to be unique.
 */
export function newIdempotencyKey(): string {
  const c = (globalThis as { crypto?: { randomUUID?: () => string } }).crypto;
  if (c?.randomUUID) return c.randomUUID();
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}-${Math.random().toString(36).slice(2)}`;
}

/**
 * Call the API. `auth: true` sends the access token and handles expiry.
 * `headers` adds extra headers (e.g. { 'Idempotency-Key': key }); they are
 * sent again, unchanged, on the retry after a token refresh.
 * Returns `data` from the envelope; throws ApiError otherwise.
 */
export async function api<T>(
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE',
  path: string,
  body?: unknown,
  opts: { auth?: boolean; headers?: Headers } = {},
): Promise<T> {
  const token = opts.auth ? (await getTokens())?.accessToken : undefined;
  let { status, json } = await (method === 'GET' ? readOnceMore : raw)<T>(method, path, body, token, opts.headers);

  if (opts.auth && status === 401 && json.code === 'TOKEN_EXPIRED') {
    if (await refreshTokens()) {
      ({ status, json } = await raw<T>(method, path, body, (await getTokens())?.accessToken, opts.headers));
    }
  }

  if (opts.auth && status === 401) {
    // Session over (signed out elsewhere, password changed, new phone...).
    await clearTokens();
    onSessionEnded?.();
  }

  if (status >= 200 && status < 300 && json.success) return (json.data ?? {}) as T;
  throw new ApiError(
    status,
    json.code ?? 'ERROR',
    json.message ?? 'Something went wrong. Try again.',
    (json.data as Record<string, unknown>) ?? undefined,
    json.errors,
  );
}
