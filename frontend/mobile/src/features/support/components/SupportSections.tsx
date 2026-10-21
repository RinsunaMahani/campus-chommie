/**
 * Every kind of support for the campus (brief, M5), in the order the server
 * gives: each service with its contact, hours, its source and when it was read
 * or checked. A kind with nothing to show says why, never a blank; crisis lines
 * stay hidden until a person has checked them (the server holds them back).
 */
import { StyleSheet, Text, View } from 'react-native';

import { Button } from '@/shared/components/Button';
import { SourceLink } from '@/shared/components/SourceLink';
import { Card } from '@/shared/components/Parts';
import { Muted, Overline, Strong } from '@/shared/components/Text';
import { MessageKey, t } from '@/shared/i18n';
import { formatDay } from '@/shared/lib/dates';
import { fonts } from '@/shared/theme/tokens';

import { Service, SupportKind } from '../types';
import { Palette, useStyles } from '@/shared/theme/palette';

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
  return (
    <Card style={{ gap: 4 }}>
      <Strong>{service.name}</Strong>
      {service.contact ? (
        <Text selectable style={styles.contact}>
          {service.contact}
        </Text>
      ) : null}
      {service.hours ? <Muted>{t('support.hours', { hours: service.hours })}</Muted> : null}
      {service.note ? <Text style={styles.note}>{service.note}</Text> : null}
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
      {service.last_verified ? (
        <Muted>{t('support.checked', { date: formatDay(service.last_verified) })}</Muted>
      ) : service.read_on ? (
        <Muted>{t('support.readOn', { date: formatDay(service.read_on) })}</Muted>
      ) : (
        <Muted>{t('support.notVerified')}</Muted>
      )}
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
          <Overline>{kindLabel(k.kind)}</Overline>
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

const makeStyles = (colors: Palette) => StyleSheet.create({
  contact: { fontFamily: fonts.bold, fontSize: 14, color: colors.ink },
  note: { fontFamily: fonts.body, fontSize: 13, lineHeight: 19, color: colors.text },
  line: { fontFamily: fonts.medium, fontSize: 13.5, lineHeight: 20, color: colors.textMuted },
});
