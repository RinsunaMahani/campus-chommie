/**
 * Openly licensed photos for the faculty headers, one per kind of field,
 * bundled in assets/images/faculties with their credit (licence and author),
 * from Wikimedia Commons. Generic subjects only: never a real campus, never a
 * university's logo. A kind without a photo shows its icon instead.
 * The full credits list is docs/image-credits.md.
 */
import { ImageSourcePropType } from 'react-native';

import { Art } from './faculties';

export type FacultyPhoto = { image: ImageSourcePropType; credit: string };

export const PHOTOS: Partial<Record<Art, FacultyPhoto>> = {};
