import { Linking, Pressable, StyleSheet, Text, View } from 'react-native';

import { CAMPUS_PHOTOS } from '@/features/courseFinder/campusPhotos';
import { PHOTOS as FIELD_PHOTOS } from '@/features/courseFinder/facultyPhotos';
import { PLACE_PHOTOS } from '@/features/outdoors/placePhotos';
import { Card } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { Muted, Overline, Title } from '@/shared/components/Text';
import { Palette, useStyles } from '@/shared/theme/palette';
import { fonts } from '@/shared/theme/tokens';

type Credit = { key: string; what: string; credit: string; source: string };

/** Every photo the app shows, in one list: what it shows, its author and licence, and its Wikimedia Commons page. */
export function photoCredits(): { title: string; items: Credit[] }[] {
  return [
    {
      title: 'University campuses',
      items: Object.entries(CAMPUS_PHOTOS).map(([id, p]) => ({
        key: `campus-${id}`,
        what: `${id.toUpperCase()}: ${p.caption}`,
        credit: p.credit,
        source: p.source,
      })),
    },
    {
      title: 'Fields of study and funders',
      items: Object.entries(FIELD_PHOTOS).map(([art, p]) => ({
        key: `field-${art}`,
        what: art.charAt(0).toUpperCase() + art.slice(1),
        credit: p!.credit,
        source: p!.source,
      })),
    },
    {
      title: 'Outdoors',
      items: Object.values(PLACE_PHOTOS)
        .flat()
        .map((p, i) => ({ key: `place-${i}`, what: p.caption, credit: p.credit, source: p.source })),
    },
  ];
}

/**
 * Photo credits: the photos come from Wikimedia Commons under free licences (CC0, CC BY, CC BY-SA), whose one
 * condition is crediting the author. The credits live here, linked beside the Privacy Policy and Terms, instead of
 * under every photo. Tapping a credit opens the photo's own page (author, licence, the original).
 */
export default function PhotoCreditsScreen() {
  const styles = useStyles(makeStyles);
  return (
    <Screen back>
      <Title>Photo credits</Title>
      <Muted>
        Every photo in Campus Chommie is from Wikimedia Commons, used under its free licence. Tap a credit to see the
        original and its licence.
      </Muted>
      {photoCredits().map((section) => (
        <View key={section.title} style={{ gap: 8 }}>
          <Overline>{section.title}</Overline>
          <Card style={{ gap: 12 }}>
            {section.items.map((c) => (
              <Pressable key={c.key} accessibilityRole="link" onPress={() => Linking.openURL(c.source)}>
                <Text style={styles.what}>{c.what}</Text>
                <Text style={styles.credit}>{c.credit}</Text>
              </Pressable>
            ))}
          </Card>
        </View>
      ))}
    </Screen>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    what: { fontFamily: fonts.semibold, fontSize: 14, color: colors.text },
    credit: { fontFamily: fonts.body, fontSize: 13, color: colors.accentDeep },
  });
