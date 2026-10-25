/**
 * What the Outdoors sheet and the full list share about a place: its icon and words for its category, and where
 * "Open in maps" goes. Only the place's own public name and address go to the maps app, never anything about the
 * student or where they are.
 */
import { Feather } from '@expo/vector-icons';
import { ComponentProps } from 'react';
import { Platform } from 'react-native';

import { MessageKey, t } from '@/shared/i18n';

type IconName = ComponentProps<typeof Feather>['name'];

export function categoryIcon(category?: string | null): IconName {
  const cat = (category || '').toLowerCase();
  if (cat.includes('outdoor') || cat.includes('park') || cat.includes('nature') || cat.includes('garden')) return 'sun';
  if (cat.includes('museum') || cat.includes('art') || cat.includes('gallery')) return 'bookmark';
  if (cat.includes('heritage') || cat.includes('history') || cat.includes('monument')) return 'compass';
  if (cat.includes('sport') || cat.includes('walk') || cat.includes('hike')) return 'activity';
  if (cat.includes('market') || cat.includes('shop')) return 'shopping-bag';
  return 'map-pin';
}

export function categoryLabel(category?: string | null): string {
  if (!category) return '';
  const key = `cheap.category.${category.toLowerCase()}` as MessageKey;
  const label = t(key);
  if (label !== key) return label;
  return category.charAt(0).toUpperCase() + category.slice(1);
}

/**
 * The phone's own maps app, searching for the place: Android's `geo:` lets the student pick any maps app, iPhones
 * open Apple Maps, and the web build opens OpenStreetMap (the map data the app already credits). None without an
 * address: the app never guesses where a place is.
 */
export function mapsUrl(place: { name: string; address: string | null }, os: string = Platform.OS): string | null {
  if (!place.address) return null;
  const q = encodeURIComponent(`${place.name}, ${place.address}`);
  if (os === 'android') return `geo:0,0?q=${q}`;
  if (os === 'ios') return `maps:?q=${q}`;
  return `https://www.openstreetmap.org/search?query=${q}`;
}
