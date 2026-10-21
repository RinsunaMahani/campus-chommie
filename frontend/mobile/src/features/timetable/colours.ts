/**
 * A module's colour. A student's modules get the palette's class colours in A to Z order, so up to eight
 * modules always look different and keep their colour across the timetable and the calendar ("ANA201 is
 * orange"). A module that isn't in the timetable (a class's test, say) falls back to a stable pick.
 */
import { Palette } from '@/shared/theme/palette';

const norm = (module: string) => module.toUpperCase().replace(/\s/g, '');

let known: string[] = [];

/** Tell the colours which modules the student has (the timetable screen and calendar call this). */
export function rememberModules(modules: string[]): void {
  known = [...new Set(modules.map(norm))].sort();
}

export function moduleColour(palette: Palette, module: string): string {
  const key = norm(module);
  const at = known.indexOf(key);
  if (at >= 0) return palette.classColours[at % palette.classColours.length];
  let hash = 0;
  for (const ch of key) hash = (hash * 31 + ch.charCodeAt(0)) >>> 0;
  return palette.classColours[hash % palette.classColours.length];
}

/** The colour as a soft fill behind a block (about 18% strong). */
export function tint(hex: string): string {
  return `${hex}2E`;
}
