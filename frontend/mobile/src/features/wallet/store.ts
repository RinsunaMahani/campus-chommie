/**
 * The student's store cards, kept on this phone only: in its secure storage (Android Keystore / iOS Keychain),
 * never sent to our server. A card's barcode is often all a till needs to spend its points, so it's treated like a
 * key. Each signed-in student has their own wallet on the phone (the key is a short hash of their email, never the
 * email itself). On the web preview there's no secure storage, so cards live in memory until the page reloads.
 */
import * as SecureStore from 'expo-secure-store';

export type StoreCard = {
  id: string;
  /** The programme's name as the student picked or typed it: "Clicks ClubCard". */
  store: string;
  number: string;
  /** Which palette colour its tile uses. */
  colour: number;
  added: string;
};

export const MAX_CARDS = 12;
const memory = new Map<string, string>();

/** FNV-1a, 32-bit, as hex: enough to keep wallets apart, and the email can't be read back from it. */
export function walletKey(email: string): string {
  let h = 0x811c9dc5;
  for (const ch of email.trim().toLowerCase()) {
    h ^= ch.charCodeAt(0);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return `campus-chommie.wallet.v1.${h.toString(16).padStart(8, '0')}`;
}

async function read(key: string): Promise<string | null> {
  try {
    return await SecureStore.getItemAsync(key);
  } catch {
    return memory.get(key) ?? null;
  }
}

async function write(key: string, value: string): Promise<void> {
  try {
    await SecureStore.setItemAsync(key, value);
  } catch {
    memory.set(key, value);
  }
}

export async function loadCards(email: string): Promise<StoreCard[]> {
  const raw = await read(walletKey(email));
  if (!raw) return [];
  try {
    const cards = JSON.parse(raw);
    return Array.isArray(cards) ? (cards as StoreCard[]) : [];
  } catch {
    return [];
  }
}

export async function saveCards(email: string, cards: StoreCard[]): Promise<void> {
  await write(walletKey(email), JSON.stringify(cards.slice(0, MAX_CARDS)));
}

/** A card number as people type it: digits and letters only, spaces and dashes dropped. */
export function cleanNumber(text: string): string {
  return text.replace(/[\s-]+/g, '').toUpperCase();
}

export function numberProblem(number: string): string | null {
  if (!/^[0-9A-Z]{6,40}$/.test(number)) return 'wallet.numberInvalid';
  return null;
}

export async function addCard(email: string, store: string, number: string, today: string): Promise<StoreCard[]> {
  const cards = await loadCards(email);
  const card: StoreCard = {
    id: `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 7)}`,
    store: store.trim(),
    number,
    colour: cards.length,
    added: today,
  };
  const next = [...cards, card].slice(0, MAX_CARDS);
  await saveCards(email, next);
  return next;
}

export async function removeCard(email: string, id: string): Promise<StoreCard[]> {
  const next = (await loadCards(email)).filter((c) => c.id !== id);
  await saveCards(email, next);
  return next;
}
