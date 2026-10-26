/**
 * Every kind of support for the campus (brief, M5), in the order the server
 * gives: each service with its contact, hours, its source and when it was read
 * or checked. A kind with nothing to show says why, never a blank; crisis lines
 * stay hidden until a person has checked them (the server holds them back).
 * Each service leads with its name, then what it's for, then a Call button (and
 * Email, when it has an address) taken exactly from the contact the university
 * published: a button never dials a number that isn't in the words above it.
 */
import { Feather } from '@expo/vector-icons';
import { ComponentProps } from 'react';
import { Linking, StyleSheet, Text, View } from 'react-native';

import { Button } from '@/shared/components/Button';
import { SourceLink } from '@/shared/components/SourceLink';
import { Card, RowTone, toneColours } from '@/shared/components/Parts';
import { Muted, Overline, Strong } from '@/shared/components/Text';
import { MessageKey, t } from '@/shared/i18n';
import { fonts, radius, space } from '@/shared/theme/tokens';

import { Service, SupportKind } from '../types';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';

type IconName = ComponentProps<typeof Feather>['name'];

/** Each kind's heading icon and its tile's colour. */
const KIND_ICON: Record<string, [IconName, RowTone]> = {
  counselling: ['message-circle', 'mint'],
  crisis: ['heart', 'rose'],
  financial_aid: ['credit-card', 'mint'],
  food_support: ['shopping-bag', 'amber'],
  tutoring: ['book-open', 'mint'],
  chaplaincy: ['sun', 'sand'],
  health: ['activity', 'mint'],
  careers: ['briefcase', 'sand'],
  disability: ['users', 'mint'],
};

/**
 * The first South African phone number in a contact, digits only ("012 521 4614 / 4500" -> "0125214614"):
 * a 0 and nine more digits, with single spaces allowed between them. Short codes (SMS 31393, USSD) aren't
 * numbers to dial, so they're left alone.
 */
export function firstPhone(contact: string | null): string | null {
  const m = contact?.match(/(?:^|[^\d*])(0(?: ?\d){9})(?!\d)/);
  return m ? m[1].replace(/ /g, '') : null;
}

/** The first email address in a contact, as written. */
export function firstEmail(contact: string | null): string | null {
  const m = contact?.match(/[\w.+-]+@[\w-]+(?:\.[\w-]+)+/);
  return m ? m[0] : null;
}

/** "Financial Aid Office: fee blocks and financial clearance" -> the name, and what it's for. */
export function splitName(name: string): [string, string | null] {
  const at = name.indexOf(': ');
  if (at < 3) return [name, null];
  const rest = name.slice(at + 2);
  return [name.slice(0, at), rest.charAt(0).toUpperCase() + rest.slice(1) + (/[.)]$/.test(rest) ? '' : '.')];
}

export function kindLabel(kind: string): string {
  const key = `support.kind.${kind}` as MessageKey;
  const label = t(key);
  return label === key ? kind.replace(/_/g, ' ') : label;
}

export function ServiceCard({
  service,
  onShowOnMap,
}: {
  service: Service;
  onShowOnMap?: () => void;
}) {
  const styles = useStyles(makeStyles);
  const [name, about] = splitName(service.name);
  const phone = firstPhone(service.contact);
  const email = firstEmail(service.contact);
  return (
    <Card style={{ gap: 6 }}>
      <Strong style={styles.name}>{name}</Strong>
      {about ? <Text style={styles.about}>{about}</Text> : null}
      {service.contact ? (
        <Text selectable style={styles.contact}>
          {service.contact}
        </Text>
      ) : null}
      {service.hours ? <Muted>{t('support.hours', { hours: service.hours })}</Muted> : null}
      {service.note ? <Text style={styles.note}>{service.note}</Text> : null}
      {phone || email ? (
        <View style={styles.actions}>
          {phone ? (
            <View style={styles.action}>
              <Button title={t('support.call')} icon="phone" onPress={() => Linking.openURL(`tel:${phone}`)} />
            </View>
          ) : null}
          {email ? (
            <View style={styles.action}>
              <Button title={t('support.email')} variant="secondary" icon="mail" onPress={() => Linking.openURL(`mailto:${email}`)} />
            </View>
          ) : null}
        </View>
      ) : null}
      {onShowOnMap ? (
        <Button
          title={t('support.showOnMap')}
          variant="secondary"
          compact
          icon="map-pin"
          onPress={onShowOnMap}
        />
      ) : null}
      <SourceLink url={service.source_url} />
    </Card>
  );
}

export function SupportSections({
  kinds,
  placeByService,
  onShowOnMap,
}: {
  kinds: SupportKind[];
  placeByService?: Record<string, string>;
  onShowOnMap?: (placeId: string) => void;
}) {
  const styles = useStyles(makeStyles);
  return (
    <View style={{ gap: 16 }}>
      {kinds.map((k) => (
        <View key={k.kind} style={{ gap: 8 }}>
          <KindHeading kind={k.kind} />
          {k.services.map((s, i) => {
            const placeId = placeByService?.[s.name];
            return (
              <ServiceCard
                key={`${k.kind}-${i}`}
                service={s}
                onShowOnMap={placeId && onShowOnMap ? () => onShowOnMap(placeId) : undefined}
              />
            );
          })}
          {k.line ? <Text style={styles.line}>{k.line}</Text> : null}
        </View>
      ))}
    </View>
  );
}

/** A kind's name with its icon on a tile tinted by meaning (rose for crisis lines). */
function KindHeading({ kind }: { kind: string }) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const [icon, tone] = KIND_ICON[kind] ?? (['life-buoy', 'sand'] as [IconName, RowTone]);
  const tile = toneColours(colors, tone);
  return (
    <View style={styles.heading}>
      <View style={[styles.headingIcon, { backgroundColor: tile.tint }]}>
        <Feather name={icon} size={14} color={tile.color} />
      </View>
      <Overline>{kindLabel(kind)}</Overline>
    </View>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  name: { fontSize: 16.5, lineHeight: 22 },
  about: { fontFamily: fonts.body, fontSize: 15, lineHeight: 21, color: colors.text },
  contact: { fontFamily: fonts.medium, fontSize: 13.5, lineHeight: 18, color: colors.textMuted },
  actions: { flexDirection: 'row', gap: space.sm, marginTop: space.xs },
  action: { flex: 1 },
  heading: { flexDirection: 'row', alignItems: 'center', gap: space.sm },
  headingIcon: { width: 26, height: 26, borderRadius: radius.sm, alignItems: 'center', justifyContent: 'center' },
  note: { fontFamily: fonts.body, fontSize: 14, lineHeight: 19, color: colors.text },
  line: { fontFamily: fonts.medium, fontSize: 14.5, lineHeight: 20, color: colors.textMuted },
});
