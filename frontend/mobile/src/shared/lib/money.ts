/**
 * Money is integer cents everywhere, same as the backend finance engine.
 * Never do arithmetic on the formatted string.
 */
export type Cents = number;

export function formatRand(cents: Cents): string {
  const negative = cents < 0;
  const abs = Math.abs(Math.round(cents));
  const rands = Math.floor(abs / 100);
  const rest = abs % 100;
  const whole = rands.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  const body = rest === 0 ? whole : `${whole}.${rest.toString().padStart(2, '0')}`;
  return `${negative ? '-' : ''}R${body}`;
}

/** The backend's ceiling for one amount (R1,000,000). */
export const MAX_CENTS: Cents = 100_000_000;

/**
 * Rand as typed ("1500", "R1 500", "1,500.50", "48,50") to integer cents,
 * by string arithmetic so no float ever rounds a cent away. Null when it isn't
 * an amount: negative, more than two decimals, empty, or over the ceiling.
 */
export function parseRand(text: string): Cents | null {
  let s = text.trim().replace(/^R\s*/i, '').replace(/[\s ]/g, '');
  // "48,50" is a decimal comma; "1,500" or "1,500.50" are thousands.
  if (/^\d+,\d{1,2}$/.test(s)) s = s.replace(',', '.');
  else s = s.replace(/,(?=\d{3}(\D|$))/g, '');
  const match = /^(\d+)(?:\.(\d{1,2}))?$/.exec(s);
  if (!match) return null;
  const cents = Number(match[1]) * 100 + Number((match[2] ?? '').padEnd(2, '0'));
  return cents <= MAX_CENTS ? cents : null;
}

/** Cents as the user types them back: "1500" or "48.50", no symbol or separators. */
export function centsToInput(cents: Cents): string {
  const rest = cents % 100;
  return rest === 0 ? String(Math.floor(cents / 100)) : `${Math.floor(cents / 100)}.${String(rest).padStart(2, '0')}`;
}
