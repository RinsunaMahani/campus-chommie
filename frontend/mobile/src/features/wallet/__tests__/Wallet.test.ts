/**
 * The card wallet: barcodes drawn correctly (a valid EAN-13 and Code 128's check sum worked by hand), card numbers cleaned
 * and checked, and each student's cards kept apart on the phone under a key that doesn't contain their email.
 */
import { beforeEach, expect, jest, test } from '@jest/globals';

import { barcodeFor, CODE128_PATTERNS, code128Values, ean13Modules, isEan13 } from '../barcode';
import { addCard, cleanNumber, loadCards, MAX_CARDS, numberProblem, removeCard, walletKey } from '../store';

const mockSaved = new Map<string, string>();
jest.mock('expo-secure-store', () => ({
  getItemAsync: async (k: string) => mockSaved.get(k) ?? null,
  setItemAsync: async (k: string, v: string) => void mockSaved.set(k, v),
}));

beforeEach(() => mockSaved.clear());

test('every Code 128 pattern is 11 modules wide and unique (the stop is 13)', () => {
  expect(CODE128_PATTERNS).toHaveLength(107);
  for (const p of CODE128_PATTERNS.slice(0, 106)) expect(p.split('').map(Number).reduce((a, b) => a + b, 0)).toBe(11);
  expect(new Set(CODE128_PATTERNS).size).toBe(107);
  expect(CODE128_PATTERNS[106].split('').map(Number).reduce((a, b) => a + b, 0)).toBe(13);
});

test("Code 128's check value is the weighted sum mod 103, and digits use the dense set", () => {
  const b = code128Values('PJJ123C')!;
  expect(b[0]).toBe(104);
  // Start B 104, then P J J 1 2 3 C = 48 42 42 17 18 19 35 weighted 1..7: 879, and 879 mod 103 = 55.
  expect(b[b.length - 1]).toBe(55);
  expect(code128Values('123456')).toEqual([105, 12, 34, 56, (105 + 12 * 1 + 34 * 2 + 56 * 3) % 103]);
  expect(code128Values('café')).toBeNull();
});

test('EAN-13 is checked and drawn as 95 modules with its guards', () => {
  expect(isEan13('4006381333931')).toBe(true);
  expect(isEan13('4006381333932')).toBe(false);
  const m = ean13Modules('4006381333931');
  expect(m).toHaveLength(95);
  expect([m.slice(0, 3), m.slice(45, 50), m.slice(92)]).toEqual(['101', '01010', '101']);
  expect(barcodeFor('4006 3813 3393 1')!.format).toBe('ean13');
  expect(barcodeFor('ABC123')!.format).toBe('code128');
  expect(barcodeFor('')).toBeNull();
});

test('card numbers are cleaned and checked', () => {
  expect(cleanNumber(' 6009 1234-5678 ')).toBe('600912345678');
  expect(numberProblem('600912345678')).toBeNull();
  expect(numberProblem('12345')).toBe('wallet.numberInvalid');
  expect(numberProblem('6009*1234')).toBe('wallet.numberInvalid');
});

test("each student's cards are kept apart, under a key without their email", async () => {
  await addCard('lerato@example.com', 'Clicks ClubCard', '600912345678', '2026-10-21');
  await addCard('sipho@example.com', 'Pick n Pay Smart Shopper', '4006381333931', '2026-10-21');
  expect((await loadCards('Lerato@Example.com ')).map((c) => c.store)).toEqual(['Clicks ClubCard']);
  expect([...mockSaved.keys()].every((k) => !k.includes('lerato') && !k.includes('@'))).toBe(true);
  expect(walletKey('lerato@example.com')).toMatch(/^campus-chommie\.wallet\.v1\.[0-9a-f]{8}$/);
  const [card] = await loadCards('lerato@example.com');
  expect(await removeCard('lerato@example.com', card.id)).toEqual([]);
});

test('at most twelve cards', async () => {
  for (let i = 0; i < MAX_CARDS + 2; i++) await addCard('lerato@example.com', `Card ${i}`, `60091234567${i}`, '2026-10-21');
  expect(await loadCards('lerato@example.com')).toHaveLength(MAX_CARDS);
});
