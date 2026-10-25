/**
 * Real photos of each place near campus, for the Outdoors preview's slideshow: from Wikimedia Commons under the
 * licence their authors chose, checked by eye, cropped to 16:9 and bundled in assets/images/places, with each one's
 * author, licence and Commons page (docs/image-credits.md lists them all). Never an AI image, and never a photo of a
 * different place standing in for this one.
 *
 * A place shows a slideshow only with at least MIN_PHOTOS; it shows at most MAX_PHOTOS. Until a place has enough,
 * its preview shows its category icon instead.
 */
import type { CampusPhoto } from '@/features/courseFinder/campusPhotos';

export type PlacePhoto = CampusPhoto;

export const MIN_PHOTOS = 3;
export const MAX_PHOTOS = 5;

/** "Wonderboom Nature Reserve: a fig tree over 1 000 years old, ..." -> "wonderboom-nature-reserve". */
export function placeKey(name: string): string {
  return name
    .split(':')[0]
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

/** By placeKey. Photos are added once found and checked (Wikimedia Commons; docs/image-credits.md). */
export const PLACE_PHOTOS: Record<string, PlacePhoto[]> = {};

/** The place's slideshow: MIN_PHOTOS to MAX_PHOTOS photos, or none. */
export function photosFor(name: string, photos: Record<string, PlacePhoto[]> = PLACE_PHOTOS): PlacePhoto[] {
  const list = photos[placeKey(name)] ?? [];
  return list.length >= MIN_PHOTOS ? list.slice(0, MAX_PHOTOS) : [];
}
