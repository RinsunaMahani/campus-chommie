/**
 * A funder's picture: the faculty photo of the field most of its fields share
 * (engineering, health, ...), or the library for a funder open to any field.
 * Never a funder's logo: logos are their owners' trademarks.
 */
import { artOfFields } from "./faculties";
import { FacultyPhoto, PHOTOS } from "./facultyPhotos";

export function funderPhoto(funder: {
  any_field?: boolean;
  fields?: { id: string }[];
}): FacultyPhoto {
  const art = funder.any_field
    ? null
    : artOfFields((funder.fields ?? []).map((f) => f.id));
  return (art && PHOTOS[art]) || PHOTOS.humanities!;
}
