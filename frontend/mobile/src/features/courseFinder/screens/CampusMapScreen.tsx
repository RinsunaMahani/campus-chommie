import { Feather } from '@expo/vector-icons';
import * as WebBrowser from 'expo-web-browser';
import { useLocalSearchParams } from 'expo-router';
import { ComponentProps, useEffect, useMemo, useState } from 'react';
import { Platform, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import Svg, { Circle, G, Polygon, Polyline, Text as SvgText } from 'react-native-svg';

import { HeroScreen } from '@/shared/components/HeroScreen';
import { Card, IconTile, InfoNote } from '@/shared/components/Parts';
import { SourceLink } from '@/shared/components/SourceLink';
import { ErrorBox } from '@/shared/components/Status';
import { Body, Muted, Overline, Strong, Title } from '@/shared/components/Text';
import { MessageKey, t } from '@/shared/i18n';
import { SkeletonCards } from '@/shared/motion/Shimmer';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import { courseFinderApi } from '../api/courseFinderApi';
import { CampusMapView, LatLon, MapPlace, MapStreet, UniversityMapAnswer } from '../types';
import { errorText } from '../words';

type FeatherIcon = ComponentProps<typeof Feather>['name'];

export function placeKindIcon(kind: string): FeatherIcon {
  switch (kind) {
    case 'academic':
      return 'book-open';
    case 'library':
      return 'book';
    case 'admin':
      return 'briefcase';
    case 'residence':
      return 'home';
    case 'health':
      return 'heart';
    case 'sport':
      return 'activity';
    case 'food':
      return 'coffee';
    case 'parking':
      return 'navigation';
    case 'services':
      return 'tool';
    default:
      return 'map-pin';
  }
}

export function placeKindLabel(kind: string): string {
  const key = `courseFinder.mapKind.${kind}` as MessageKey;
  const label = t(key);
  return label === key ? t('courseFinder.mapKind.other') : label;
}

const SVG_WIDTH = 320;
const SVG_HEIGHT = 240;
const SVG_PAD = 14;

function makeProjector(southWest: LatLon, northEast: LatLon) {
  const [minLat, minLon] = southWest;
  const [maxLat, maxLon] = northEast;
  const latSpan = Math.max(maxLat - minLat, 0.0001);
  const lonSpan = Math.max(maxLon - minLon, 0.0001);
  const innerW = SVG_WIDTH - SVG_PAD * 2;
  const innerH = SVG_HEIGHT - SVG_PAD * 2;

  return ([lat, lon]: LatLon): [number, number] => {
    const x = SVG_PAD + ((lon - minLon) / lonSpan) * innerW;
    const y = SVG_PAD + ((maxLat - lat) / latSpan) * innerH;
    return [Math.round(x * 10) / 10, Math.round(y * 10) / 10];
  };
}

function toPoints(ring: LatLon[], project: (pt: LatLon) => [number, number]): string {
  return ring
    .map((pt) => {
      const [x, y] = project(pt);
      return `${x},${y}`;
    })
    .join(' ');
}

/**
 * CampusMapScreen: OpenStreetMap campus outline, buildings and named places.
 * - Campus picker from `campuses`; one not mapped yet shows its line.
 * - Fits view to `south_west` and `north_east`.
 * - Draws `outline`, then each place's `outline` (a pin when it has none).
 * - Labels named ones; unnamed stay plain shapes, never guessed.
 * - Tap shows the place's name, or "No name yet".
 * - Shows `attribution` linked to `attribution_url` and `licence` linked to `licence_url`.
 * - Shows `notice` when `confirmed` is false.
 */
/** Above this many named places, the map names only the one you chose: dozens of names on a phone-sized map
 * cover each other (Rhodes has 149). The list under the map still names them all. */
export const MAX_PLACE_LABELS = 15;

/** Whether a place's name is drawn on the map: every name on a small campus, only the chosen one on a big one. */
export function showsLabel(place: MapPlace, namedCount: number, selectedId: string | null): boolean {
  return !!place.name && (namedCount <= MAX_PLACE_LABELS || place.id === selectedId);
}

/** Most road names on one map: more would cover the buildings. */
const MAX_STREET_LABELS = 6;

/**
 * Where each named road's name goes: once per name, in the middle of its longest stretch, longest roads first.
 */
export function streetLabels(streets: MapStreet[], project: (pt: LatLon) => [number, number]): { name: string; x: number; y: number }[] {
  const longest = new Map<string, { len: number; mid: [number, number] }>();
  for (const s of streets) {
    if (s.kind !== 'road' || !s.name) continue;
    const pts = s.line.map(project);
    let len = 0;
    for (let i = 1; i < pts.length; i++) len += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
    const best = longest.get(s.name);
    // The middle: between the two middle points, so a two-point road is labelled halfway, not at an end.
    const [a, b] = [pts[Math.floor((pts.length - 1) / 2)], pts[Math.ceil((pts.length - 1) / 2)]];
    if (!best || len > best.len) longest.set(s.name, { len, mid: [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2] });
  }
  return [...longest.entries()]
    .sort((a, b) => b[1].len - a[1].len)
    .slice(0, MAX_STREET_LABELS)
    .map(([name, v]) => ({ name, x: v.mid[0], y: v.mid[1] }));
}

/**
 * A tap on a map shape. On the web, react-native-svg turns onPress into a click and also hands the page
 * touch-responder props the browser doesn't know (React logs six "Unknown event handler" errors). There, a click
 * alone: onPress must be null, not left out, or the library copies the missing onPress over our onClick.
 */
const tap = (fn: () => void): object => (Platform.OS === 'web' ? { onClick: fn, onPress: null } : { onPress: fn });

export default function CampusMapScreen() {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const { id, campus: campusParam, place: placeParam } = useLocalSearchParams<{
    id: string;
    campus?: string;
    place?: string;
  }>();
  const [data, setData] = useState<UniversityMapAnswer | null>(null);
  const [selectedCampusId, setSelectedCampusId] = useState<string | null>(campusParam ?? null);
  const [selectedPlaceId, setSelectedPlaceId] = useState<string | null>(placeParam ?? null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    courseFinderApi
      .universityMap(id)
      .then((ans) => {
        setData(ans);
        setSelectedCampusId((prev) => {
          if (prev && ans.campuses.some((c) => c.id === prev)) return prev;
          const firstMapped = ans.campuses.find((c) => c.mapped);
          return firstMapped?.id ?? ans.campuses[0]?.id ?? null;
        });
      })
      .catch((e) => setError(errorText(e)))
      .finally(() => setLoading(false));
  }, [id]);

  const activeCampus: CampusMapView | null = useMemo(() => {
    if (!data?.campuses.length) return null;
    return (
      data.campuses.find((c) => c.id === selectedCampusId) ??
      data.campuses.find((c) => c.mapped) ??
      data.campuses[0]
    );
  }, [data, selectedCampusId]);

  const selectedPlace: MapPlace | null = useMemo(() => {
    if (!activeCampus || !selectedPlaceId) return null;
    return activeCampus.places.find((p) => p.id === selectedPlaceId) ?? null;
  }, [activeCampus, selectedPlaceId]);

  const selectedSupportServices = useMemo(() => {
    if (!activeCampus || !selectedPlace) return [];
    return activeCampus.support.filter((s) => s.place === selectedPlace.id);
  }, [activeCampus, selectedPlace]);

  const namedPlaces = useMemo(
    () => activeCampus?.places.filter((p) => !!p.name) ?? [],
    [activeCampus],
  );

  const unnamedPlaces = useMemo(
    () => activeCampus?.places.filter((p) => !p.name) ?? [],
    [activeCampus],
  );

  const namedCount = useMemo(() => activeCampus?.places.filter((p) => p.name).length ?? 0, [activeCampus]);

  const projector = useMemo(() => {
    if (!activeCampus?.mapped || !activeCampus.south_west || !activeCampus.north_east) return null;
    return makeProjector(activeCampus.south_west, activeCampus.north_east);
  }, [activeCampus]);

  return (
    <HeroScreen
      back
      title={data?.university?.name ?? t('courseFinder.campusMapTitle')}
      subtitle={t('courseFinder.campusMapSub')}>
      {loading ? <SkeletonCards count={3} /> : null}

      {error ? (
        <ErrorBox
          message={error}
          onRetry={() => {
            if (!id) return;
            setError(null);
            setLoading(true);
            courseFinderApi
              .universityMap(id)
              .then(setData)
              .catch((e) => setError(errorText(e)))
              .finally(() => setLoading(false));
          }}
        />
      ) : null}

      {!loading && !error && data ? (
        <View style={{ gap: 14 }}>
          {!data.confirmed && data.notice ? (
            <InfoNote icon="info">{data.notice}</InfoNote>
          ) : null}

          {/* Campus picker */}
          {data.campuses.length > 1 ? (
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chips}>
              {data.campuses.map((c) => {
                const on = activeCampus?.id === c.id;
                return (
                  <Pressable
                    key={c.id}
                    accessibilityRole="button"
                    accessibilityLabel={c.name}
                    accessibilityState={{ selected: on }}
                    onPress={() => {
                      setSelectedCampusId(c.id);
                      setSelectedPlaceId(null);
                    }}
                    style={[styles.chip, on && styles.chipOn]}>
                    <Text style={[styles.chipText, on && styles.chipTextOn]}>{c.name}</Text>
                  </Pressable>
                );
              })}
            </ScrollView>
          ) : null}

          {activeCampus ? (
            <>
              {/* Plain-words lines about what's mapped on this campus */}
              <Card style={styles.card}>
                <Title style={styles.campusTitle}>{activeCampus.name}</Title>
                {activeCampus.lines.map((line, i) => (
                  <Body key={i}>{line}</Body>
                ))}
                {activeCampus.source_url ? <SourceLink url={activeCampus.source_url} /> : null}
              </Card>

              {/* SVG Campus Map when mapped */}
              {activeCampus.mapped && projector ? (
                <Card style={styles.mapCard}>
                  <Muted>{t('courseFinder.mapTapHint')}</Muted>
                  <View style={styles.svgBox}>
                    <Svg
                      width="100%"
                      height={SVG_HEIGHT}
                      viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}>
                      {/* Campus outline */}
                      {activeCampus.outline.map((ring, idx) => (
                        <Polygon
                          key={`outline-${idx}`}
                          points={toPoints(ring, projector)}
                          fill={colors.iconTile}
                          stroke={colors.accentDeep}
                          strokeWidth={1.5}
                        />
                      ))}

                      {/* Roads around the campus and paths across it, under the buildings */}
                      {(activeCampus.streets ?? []).map((street, idx) => (
                        <Polyline
                          key={`street-${idx}`}
                          points={street.line.map((pt) => projector(pt).join(',')).join(' ')}
                          fill="none"
                          stroke={street.kind === 'road' ? colors.textFaint : colors.accentDeep}
                          strokeOpacity={street.kind === 'road' ? 0.45 : 0.5}
                          strokeWidth={street.kind === 'road' ? 3 : 1}
                          strokeDasharray={street.kind === 'path' ? '2,2' : undefined}
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      ))}
                      {streetLabels(activeCampus.streets ?? [], projector).map((label) => (
                        <SvgText
                          key={`street-name-${label.name}`}
                          x={label.x}
                          y={label.y - 3}
                          fill={colors.textMuted}
                          fontSize="6"
                          fontStyle="italic"
                          textAnchor="middle">
                          {label.name}
                        </SvgText>
                      ))}

                      {/* Building outlines and point pins; names as showsLabel says */}
                      {activeCampus.places.map((place) => {
                        const selected = selectedPlaceId === place.id;
                        const hasOutline = place.outline && place.outline.length >= 3;
                        const [cx, cy] = projector(place.centre);
                        return (
                          <G key={place.id}>
                            {hasOutline ? (
                              <Polygon
                                testID={`map-place-${place.id}`}
                                points={toPoints(place.outline, projector)}
                                fill={selected ? colors.marigold : place.name ? colors.jadeTint : colors.line}
                                stroke={selected ? colors.marigold : place.name ? colors.accentDeep : colors.textFaint}
                                strokeWidth={selected ? 2 : 1}
                                {...tap(() => setSelectedPlaceId(place.id))}
                              />
                            ) : (
                              <Circle
                                testID={`map-place-${place.id}`}
                                cx={cx}
                                cy={cy}
                                r={selected ? 6 : 4.5}
                                fill={selected ? colors.marigold : colors.accentDeep}
                                stroke={colors.ink}
                                strokeWidth={1}
                                {...tap(() => setSelectedPlaceId(place.id))}
                              />
                            )}
                            {showsLabel(place, namedCount, selectedPlaceId) ? (
                              <SvgText
                                x={cx}
                                y={cy - 6}
                                fill={colors.ink}
                                fontSize="8"
                                textAnchor="middle">
                                {place.name}
                              </SvgText>
                            ) : null}
                          </G>
                        );
                      })}
                    </Svg>
                  </View>
                </Card>
              ) : null}

              {/* Selected place detail card */}
              {selectedPlace ? (
                <Card style={styles.card}>
                  <View style={styles.selectedRow}>
                    <IconTile name={placeKindIcon(selectedPlace.kind)} />
                    <View style={{ flex: 1, gap: 2 }}>
                      <Strong style={styles.placeTitle}>
                        {selectedPlace.name ?? t('courseFinder.mapNoNameYet')}
                      </Strong>
                      <Muted>{placeKindLabel(selectedPlace.kind)}</Muted>
                    </View>
                  </View>
                  {selectedSupportServices.map((s, i) => (
                    <Body key={i}>{s.name}</Body>
                  ))}
                </Card>
              ) : null}

              {/* Named places list */}
              {activeCampus.mapped && namedPlaces.length > 0 ? (
                <Card style={styles.card}>
                  <Overline>{t('courseFinder.mapNamedPlaces')}</Overline>
                  <View style={{ gap: 8 }}>
                    {namedPlaces.map((place) => {
                      const selected = selectedPlaceId === place.id;
                      return (
                        <Pressable
                          key={place.id}
                          accessibilityRole="button"
                          accessibilityLabel={place.name!}
                          onPress={() => setSelectedPlaceId(place.id)}
                          style={[styles.placeRow, selected && styles.placeRowSelected]}>
                          <Feather
                            name={placeKindIcon(place.kind)}
                            size={15}
                            color={selected ? colors.pillText : colors.accentDeep}
                          />
                          <View style={{ flex: 1 }}>
                            <Text style={[styles.placeRowName, selected && styles.placeRowTextSelected]}>
                              {place.name}
                            </Text>
                            <Text style={[styles.placeRowKind, selected && styles.placeRowTextSelected]}>
                              {placeKindLabel(place.kind)}
                            </Text>
                          </View>
                        </Pressable>
                      );
                    })}
                  </View>
                </Card>
              ) : null}

              {/* Unnamed buildings selector (so tapping an unnamed shape is also reachable by button/screen-reader) */}
              {activeCampus.mapped && unnamedPlaces.length > 0 ? (
                <Card style={styles.card}>
                  <Overline>{t('courseFinder.mapUnnamedPlaces', { n: unnamedPlaces.length })}</Overline>
                  <Pressable
                    accessibilityRole="button"
                    accessibilityLabel={t('courseFinder.mapNoNameYet')}
                    onPress={() => setSelectedPlaceId(unnamedPlaces[0].id)}
                    style={styles.placeRow}>
                    <Feather name="map-pin" size={15} color={colors.textMuted} />
                    <Text style={styles.placeRowName}>{t('courseFinder.mapNoNameYet')}</Text>
                  </Pressable>
                </Card>
              ) : null}
            </>
          ) : null}

          {/* Always show OpenStreetMap attribution and ODbL licence */}
          <Card style={styles.card}>
            <Overline>{t('courseFinder.mapAboutData')}</Overline>
            <Pressable
              accessibilityRole="link"
              accessibilityLabel={data.attribution}
              onPress={() => WebBrowser.openBrowserAsync(data.attribution_url)}
              style={styles.linkRow}>
              <Feather name="external-link" size={14} color={colors.accentDeep} />
              <Text style={styles.linkText}>{data.attribution}</Text>
            </Pressable>
            <Pressable
              accessibilityRole="link"
              accessibilityLabel={data.licence}
              onPress={() => WebBrowser.openBrowserAsync(data.licence_url)}
              style={styles.linkRow}>
              <Feather name="external-link" size={14} color={colors.accentDeep} />
              <Text style={styles.linkText}>{data.licence}</Text>
            </Pressable>
          </Card>
        </View>
      ) : null}
    </HeroScreen>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
  chips: { gap: 8, paddingRight: 8 },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.white,
  },
  chipOn: { backgroundColor: colors.ink, borderColor: colors.ink },
  chipText: { fontFamily: fonts.semibold, fontSize: 14, color: colors.ink },
  chipTextOn: { color: colors.pillText },
  card: { gap: 10, padding: 14 },
  campusTitle: { fontSize: 18, lineHeight: 24, color: colors.text },
  mapCard: { gap: 10, padding: 12 },
  svgBox: {
    width: '100%',
    height: SVG_HEIGHT,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.glassElevated,
    overflow: 'hidden',
  },
  selectedRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  placeTitle: { fontSize: 16, color: colors.text },
  placeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingHorizontal: 12,
    paddingVertical: 9,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.iconTile,
  },
  placeRowSelected: {
    backgroundColor: colors.ink,
    borderColor: colors.ink,
  },
  placeRowName: { fontFamily: fonts.semibold, fontSize: 14.5, color: colors.text },
  placeRowKind: { fontFamily: fonts.body, fontSize: 13, color: colors.textMuted },
  placeRowTextSelected: { color: colors.pillText },
  linkRow: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingVertical: 2 },
  linkText: { fontFamily: fonts.semibold, fontSize: 14, color: colors.accentDeep },
});
