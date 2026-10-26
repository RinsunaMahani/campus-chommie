/**
 * One place, previewed in the Outdoors sheet: a slideshow of its photos (3 to 5, when we have them), what it is,
 * what it costs as its own page says, when it's open and where, with "Open in maps" (the phone's own maps app,
 * searching its public address) and its source.
 */
import { Linking, StyleSheet, Text, View } from 'react-native';

import { CheapThing } from '@/features/money/types';
import { Button } from '@/shared/components/Button';
import { IconTile, Tag } from '@/shared/components/Parts';
import { SourceLink } from '@/shared/components/SourceLink';
import { Strong } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { Palette, useStyles } from '@/shared/theme/palette';
import { fonts, radius, space, type } from '@/shared/theme/tokens';

import { photosFor } from '../placePhotos';
import { categoryIcon, categoryLabel, mapsUrl } from '../places';
import { PhotoSlideshow } from './PhotoSlideshow';

export function PlacePreview({ place }: { place: CheapThing }) {
  const styles = useStyles(makeStyles);
  const url = mapsUrl(place);
  const photos = photosFor(place.name);
  return (
    <View style={{ gap: space.md }}>
      {photos.length ? <PhotoSlideshow photos={photos} place={place.name} /> : null}
      <View style={styles.head}>
        {photos.length ? null : <IconTile name={categoryIcon(place.category)} size={56} />}
        <View style={{ flex: 1, gap: 6 }}>
          <View style={styles.tags}>
            <Tag label={categoryLabel(place.category)} tone="info" />
            {place.free ? <Tag label="Free" tone="jade" /> : null}
          </View>
          <Strong style={styles.name}>{place.name}</Strong>
        </View>
      </View>

      <View style={styles.facts}>
        <Fact label={t('outdoors.cost')} value={place.cost_note ?? t('support.notVerified')} />
        <Fact label={t('outdoors.hours')} value={place.hours ?? t('outdoors.hoursUnknown')} />
        <Fact label={t('outdoors.where')} value={place.address ?? t('outdoors.noAddress')} last />
      </View>

      {url ? (
        <Button
          title={t('outdoors.openMaps')}
          icon="navigation"
          variant="accent"
          onPress={() => Linking.openURL(url).catch(() => undefined)}
        />
      ) : null}
      <SourceLink url={place.source_url} />
    </View>
  );
}

function Fact({ label, value, last }: { label: string; value: string; last?: boolean }) {
  const styles = useStyles(makeStyles);
  return (
    <View style={[styles.fact, last && { borderBottomWidth: 0 }]}>
      <Text style={styles.factLabel}>{label}</Text>
      <Text style={styles.factValue}>{value}</Text>
    </View>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    head: { flexDirection: 'row', gap: space.md, alignItems: 'center' },
    tags: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
    name: { ...type.headline, color: colors.ink },
    facts: {
      borderRadius: radius.md,
      borderWidth: 1,
      borderColor: colors.line,
      backgroundColor: colors.porcelain,
      paddingHorizontal: space.md,
    },
    fact: { paddingVertical: 10, gap: 2, borderBottomWidth: StyleSheet.hairlineWidth, borderBottomColor: colors.line },
    factLabel: { fontFamily: fonts.semibold, fontSize: 12, color: colors.textFaint, textTransform: 'uppercase', letterSpacing: 0.6 },
    factValue: { fontFamily: fonts.body, fontSize: 15, lineHeight: 21, color: colors.ink },
  });
