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

/**
 * The place's name as a key, without a description after a colon: "Wonderboom Nature Reserve: a fig tree over 1 000
 * years old, ..." -> "wonderboom-nature-reserve". A one-word part before the colon is a prefix, not the name, and
 * stays: "DITSONG: Tswaing Meteorite Crater" -> "ditsong-tswaing-meteorite-crater".
 */
export function placeKey(name: string): string {
  const [head, ...rest] = name.split(':');
  const named = rest.length && head.trim().split(/\s+/).length >= 2 ? head : name;
  return named
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

/**
 * By placeKey, in the order the slideshow shows them. Found on Wikimedia Commons and checked by eye on 25 Oct 2026:
 * each photo's page names the place, and none shows a logo, a face up close or a number plate. Wits Art Museum has
 * no photo of its own on Commons yet and keeps its icon.
 */
export const PLACE_PHOTOS: Record<string, PlacePhoto[]> = {
  'freedom-park': [
    {
      image: require('../../../assets/images/places/freedom-park-1.jpg'),
      caption: "The amphitheatre, with Pretoria beyond",
      credit: "ljswaan, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Freedom_Park_Amphitheatre_01.jpg",
    },
    {
      image: require('../../../assets/images/places/freedom-park-2.jpg'),
      caption: "The building over the fountain pool",
      credit: "ljswaan, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Freedom_Park_Amphitheatre_and_eternal_flame.jpg",
    },
    {
      image: require('../../../assets/images/places/freedom-park-3.jpg'),
      caption: "The eternal flame in its pool",
      credit: "~ souTH AFRica ~, CC BY 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Flames_in_a_pool_at_Freedom_Park_Pretoria_-_panoramio.jpg",
    },
    {
      image: require('../../../assets/images/places/freedom-park-4.jpg'),
      caption: "The stone circle on the hilltop",
      credit: "~ souTH AFRica ~, CC BY 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:%22Holy_ground%22_(no_shoes_or_hats_allowed)_at_Freedom_Park_Pretoria_with_UNISA_in_the_background._-_panoramio.jpg",
    },
    {
      image: require('../../../assets/images/places/freedom-park-5.jpg'),
      caption: "Freedom Park on Salvokop, seen from across the city",
      credit: "Leo za1, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Freedom_Park-333.jpg",
    },
  ],
  'pretoria-national-botanical-garden': [
    {
      image: require('../../../assets/images/places/pretoria-national-botanical-garden-1.jpg'),
      caption: "Steps through flowering beds and cycads",
      credit: "Leo za1, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Pretoria_Botanical_Gardens-001.jpg",
    },
    {
      image: require('../../../assets/images/places/pretoria-national-botanical-garden-2.jpg'),
      caption: "A path through the dry garden",
      credit: "NJR ZA, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:South_Africa-Pretoria-National_Botanical_Gardens03.jpg",
    },
    {
      image: require('../../../assets/images/places/pretoria-national-botanical-garden-3.jpg'),
      caption: "Paths and a signpost among the trees",
      credit: "NJR ZA, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:South_Africa-Pretoria-National_Botanical_Gardens04.jpg",
    },
    {
      image: require('../../../assets/images/places/pretoria-national-botanical-garden-4.jpg'),
      caption: "The sculpted garden gates",
      credit: "Jim Speirs, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Gates_at_the_Botanical_Gardens.JPG",
    },
    {
      image: require('../../../assets/images/places/pretoria-national-botanical-garden-5.jpg'),
      caption: "The tea garden",
      credit: "JMK, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Teetuin_en_konferensiegerief,_Pretoria_Nasionale_Botaniese_Tuin.jpg",
    },
  ],
  'voortrekker-monument': [
    {
      image: require('../../../assets/images/places/voortrekker-monument-1.jpg'),
      caption: "The monument from the foot of the stairs",
      credit: "Ymblanter, CC BY-SA 4.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Pretoria_Voortrekker_Monument_seen_from_the_bottom_of_the_stairs.jpg",
    },
    {
      image: require('../../../assets/images/places/voortrekker-monument-2.jpg'),
      caption: "The dome, from inside",
      credit: "Ymblanter, CC BY-SA 4.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Pretoria_Voortrekker_Monument_Dome_seen_from_the_inside.jpg",
    },
    {
      image: require('../../../assets/images/places/voortrekker-monument-3.jpg'),
      caption: "The stone corridor at the top",
      credit: "JW Hurter, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Voortrekker_Monument_Corridor.jpg",
    },
    {
      image: require('../../../assets/images/places/voortrekker-monument-4.jpg'),
      caption: "The monument above the trees, from Fort Schanskop",
      credit: "Ymblanter, CC BY-SA 4.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Pretoria_Voortrekker_Monument_seen_from_the_northern_gate_of_Fort_Schanskop.jpg",
    },
  ],
  'ditsong-national-museum-of-natural-history': [
    {
      image: require('../../../assets/images/places/ditsong-national-museum-of-natural-history-1.jpg'),
      caption: "The museum's front on Paul Kruger Street",
      credit: "Katangais, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Transvaal_Museum2014.JPG",
    },
    {
      image: require('../../../assets/images/places/ditsong-national-museum-of-natural-history-2.jpg'),
      caption: "Inside the entrance hall",
      credit: "Leo za1, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Transvaal_Museum-020.jpg",
    },
    {
      image: require('../../../assets/images/places/ditsong-national-museum-of-natural-history-3.jpg'),
      caption: "An agate in the minerals display",
      credit: "Leo za1, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Transvaal_Museum-010.jpg",
    },
  ],
  'wonderboom-nature-reserve': [
    {
      image: require('../../../assets/images/places/wonderboom-nature-reserve-1.jpg'),
      caption: "The great fig, the Wonderboom",
      credit: "JMK, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Ficus_salicifolia_-_Die_Wonderboom,_b,_Wonderboom_Natuurreservaat.jpg",
    },
    {
      image: require('../../../assets/images/places/wonderboom-nature-reserve-2.jpg'),
      caption: "Under the fig's branches, by the walkway",
      credit: "JMK, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Ficus_salicifolia_-_Die_Wonderboom,_e,_Wonderboom_NR.jpg",
    },
    {
      image: require('../../../assets/images/places/wonderboom-nature-reserve-3.jpg'),
      caption: "The fig grove from the hill above",
      credit: "JMK, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Ficus_salicifolia_-_Die_Wonderboom,_a,_Wonderboom_Natuurreservaat.jpg",
    },
    {
      image: require('../../../assets/images/places/wonderboom-nature-reserve-4.jpg'),
      caption: "A cave in the reserve",
      credit: "M J Hurter, CC BY 4.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Cave_at_Wonderboom_Nature_Reserve.jpg",
    },
    {
      image: require('../../../assets/images/places/wonderboom-nature-reserve-5.jpg'),
      caption: "The old fort, with Pretoria beyond",
      credit: "M J Hurter, CC BY 4.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Pretoria_from_Fort_Wonderboompoort.jpg",
    },
  ],
  'ditsong-tswaing-meteorite-crater': [
    {
      image: require('../../../assets/images/places/ditsong-tswaing-meteorite-crater-1.jpg'),
      caption: "The crater from its rim",
      credit: "Martin Tuchscherer, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Tswaing_crater_-_panoramio.jpg",
    },
    {
      image: require('../../../assets/images/places/ditsong-tswaing-meteorite-crater-2.jpg'),
      caption: "The crater lake from above",
      credit: "NJR ZA, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Tswaing_crater-001.jpg",
    },
    {
      image: require('../../../assets/images/places/ditsong-tswaing-meteorite-crater-3.jpg'),
      caption: "The crater lake and the bush on its walls",
      credit: "Rotational, Public domain, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Tswaing01.jpg",
    },
    {
      image: require('../../../assets/images/places/ditsong-tswaing-meteorite-crater-4.jpg'),
      caption: "The crater floor",
      credit: "Ossewa, CC BY-SA 4.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Tswaing_crater_2014.jpg",
    },
  ],
  'lowveld-national-botanical-garden': [
    {
      image: require('../../../assets/images/places/lowveld-national-botanical-garden-1.jpg'),
      caption: "The river gorge and its waterfall",
      credit: "Werner Bayer, CC0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Lowveld_National_Botanical_Garden_1.jpg",
    },
    {
      image: require('../../../assets/images/places/lowveld-national-botanical-garden-2.jpg'),
      caption: "The Nels River gorge",
      credit: "Werner Bayer, CC0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Lowveld_National_Botanical_Garden,_Nelsrivier.jpg",
    },
    {
      image: require('../../../assets/images/places/lowveld-national-botanical-garden-3.jpg'),
      caption: "Rapids on the river",
      credit: "Werner Bayer, CC0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Lowveld_National_Botanical_Garden_2.jpg",
    },
    {
      image: require('../../../assets/images/places/lowveld-national-botanical-garden-4.jpg'),
      caption: "A walkway beside the Crocodile River",
      credit: "Karen Wiebe, CC BY-SA 3.0, Wikimedia Commons (cropped)",
      source: "https://commons.wikimedia.org/wiki/File:Laeveld_NBT,_rivieroewer.jpg",
    },
  ],
};

/** The place's slideshow: MIN_PHOTOS to MAX_PHOTOS photos, or none. */
export function photosFor(name: string, photos: Record<string, PlacePhoto[]> = PLACE_PHOTOS): PlacePhoto[] {
  const list = photos[placeKey(name)] ?? [];
  return list.length >= MIN_PHOTOS ? list.slice(0, MAX_PHOTOS) : [];
}
