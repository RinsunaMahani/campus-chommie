/**
 * Store-card barcodes drawn by the app itself, so no barcode library is needed: EAN-13 for a valid 13-digit card
 * number (many South African loyalty cards), Code 128 for anything else (set C for an even run of digits, set B
 * otherwise). Each returns the bars as widths in modules, starting with a bar; the card screen draws them.
 */

/** Code 128 patterns 0-106: bar, space, bar, space... widths in modules (106 is the stop, 13 wide). */
const C128 = [
  '212222', '222122', '222221', '121223', '121322', '131222', '122213', '122312', '132212', '221213',
  '221312', '231212', '112232', '122132', '122231', '113222', '123122', '123221', '223211', '221132',
  '221231', '213212', '223112', '312131', '311222', '321122', '321221', '312212', '322112', '322211',
  '212123', '212321', '232121', '111323', '131123', '131321', '112313', '132113', '132311', '211313',
  '231113', '231311', '112133', '112331', '132131', '113123', '113321', '133121', '313121', '211331',
  '231131', '213113', '213311', '213131', '311123', '311321', '331121', '312113', '312311', '332111',
  '314111', '221411', '431111', '111224', '111422', '121124', '121421', '141122', '141221', '112214',
  '112412', '122114', '122411', '142112', '142211', '241211', '221114', '413111', '241112', '134111',
  '111242', '121142', '121241', '114212', '124112', '124211', '411212', '421112', '421211', '212141',
  '214121', '412121', '111143', '111341', '131141', '114113', '114311', '411113', '411311', '113141',
  '114131', '311141', '411131', '211412', '211214', '211232', '2331112',
];
export const CODE128_PATTERNS = C128;
const START_B = 104;
const START_C = 105;
const STOP = 106;

/** The values Code 128 sends for `text` (start, data, check), or null if it has a character it can't send. */
export function code128Values(text: string): number[] | null {
  if (!text) return null;
  let values: number[];
  if (/^\d+$/.test(text) && text.length % 2 === 0) {
    values = [START_C];
    for (let i = 0; i < text.length; i += 2) values.push(Number(text.slice(i, i + 2)));
  } else {
    values = [START_B];
    for (const ch of text) {
      const code = ch.charCodeAt(0);
      if (code < 32 || code > 126) return null;
      values.push(code - 32);
    }
  }
  const check = values.reduce((sum, v, i) => sum + v * (i === 0 ? 1 : i), 0) % 103;
  return [...values, check];
}

function code128Bars(text: string): number[] | null {
  const values = code128Values(text);
  if (!values) return null;
  return [...values, STOP].flatMap((v) => C128[v].split('').map(Number));
}

const L = ['0001101', '0011001', '0010011', '0111101', '0100011', '0110001', '0101111', '0111011', '0110111', '0001011'];
const G = ['0100111', '0110011', '0011011', '0100001', '0011101', '0111001', '0000101', '0010001', '0001001', '0010111'];
const R = ['1110010', '1100110', '1101100', '1000010', '1011100', '1001110', '1010000', '1000100', '1001000', '1110100'];
/** Which of the left six digits use G, by the first digit (1 = G). */
const PARITY = ['000000', '001011', '001101', '001110', '010011', '011001', '011100', '010101', '010110', '011010'];

export function isEan13(text: string): boolean {
  if (!/^\d{13}$/.test(text)) return false;
  const digits = text.split('').map(Number);
  const sum = digits.slice(0, 12).reduce((s, d, i) => s + d * (i % 2 ? 3 : 1), 0);
  return (10 - (sum % 10)) % 10 === digits[12];
}

/** EAN-13 as 95 modules, 1 = bar. */
export function ean13Modules(text: string): string {
  const d = text.split('').map(Number);
  const parity = PARITY[d[0]];
  let out = '101';
  for (let i = 1; i <= 6; i++) out += parity[i - 1] === '1' ? G[d[i]] : L[d[i]];
  out += '01010';
  for (let i = 7; i <= 12; i++) out += R[d[i]];
  return out + '101';
}

/** Runs of bars and spaces in modules, starting with a bar. */
function runs(modules: string): number[] {
  const out: number[] = [];
  let i = 0;
  while (i < modules.length) {
    let j = i;
    while (j < modules.length && modules[j] === modules[i]) j++;
    out.push(j - i);
    i = j;
  }
  return out;
}

export type Barcode = { format: 'ean13' | 'code128'; widths: number[] };

/** The bars for a card number, or null when it can't be drawn (an empty or unusual number). */
export function barcodeFor(number: string): Barcode | null {
  const clean = number.replace(/\s+/g, '');
  if (isEan13(clean)) return { format: 'ean13', widths: runs(ean13Modules(clean)) };
  const bars = code128Bars(clean);
  return bars ? { format: 'code128', widths: bars } : null;
}
