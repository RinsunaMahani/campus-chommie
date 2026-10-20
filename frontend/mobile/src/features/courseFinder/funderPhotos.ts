/**
 * How a funder looks in the app: its short name on a monogram tile everywhere, and on its own page the faculty
 * photo of the field most of its fields share (engineering, health, ...). A funder open to any field has no
 * photo: a stock picture would say nothing about it. Never a funder's logo: logos are their owners'
 * trademarks and would read as the funder endorsing the app.
 */
import { artOfFields } from "./faculties";
import { FacultyPhoto, PHOTOS } from "./facultyPhotos";

export function funderPhoto(funder: {
  any_field?: boolean;
  fields?: { id: string }[];
}): FacultyPhoto | null {
  const art = funder.any_field
    ? null
    : artOfFields((funder.fields ?? []).map((f) => f.id));
  return (art && PHOTOS[art]) || null;
}

/** Words that name the kind of scheme rather than who runs it. */
const GENERIC = new Set(["bursary", "bursaries", "fund", "foundation", "fellowship", "programme", "scheme", "loans", "awards", "assist", "database"]);
const CAPS = /^[A-Z0-9@&]{2,7}$/;

/**
 * The letters on a funder's tile, from its own names only: "NSFAS", "CSIR", "SAICA" (Thuthuka's bracketed
 * owner), "NEDBANK", "OM" (Old Mutual), "LPW" (Limpopo Public Works).
 */
export function funderMonogram(funder: { name: string; short_name?: string | null }): string {
  const short = (funder.short_name ?? funder.name).trim();
  const first = short.split(/\s+/)[0];
  if (CAPS.test(first)) return first;
  const bracketed = /\(([A-Z0-9@&]{2,7})\)/.exec(funder.name);
  if (bracketed) return bracketed[1];
  const words = short.split(/\s+/).filter((w) => !GENERIC.has(w.toLowerCase()));
  if (words.length === 1 && words[0].length <= 7) return words[0].toUpperCase();
  const capitals = words.map((w) => w.replace(/[^A-Z]/g, "") || w[0].toUpperCase()).join("");
  return capitals.slice(0, 4) || short[0].toUpperCase();
}
