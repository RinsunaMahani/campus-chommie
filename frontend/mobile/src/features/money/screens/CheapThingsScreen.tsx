import { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { errorText } from '@/shared/api/errors';
import { Card, InfoNote, Tag } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { SourceLink } from '@/shared/components/SourceLink';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Body, Muted, Strong, Title } from '@/shared/components/Text';
import { MessageKey, t } from '@/shared/i18n';
import { formatDay } from '@/shared/lib/dates';
import { colors, fonts } from '@/shared/theme/tokens';

import { moneyApi } from '../api/moneyApi';
import { CheapThing } from '../types';

function categoryLabel(category: string): string {
  const key = `cheap.category.${category}` as MessageKey;
  const label = t(key);
  return label === key ? category : label;
}

/** Cheap things near the student's campus, each with its price as the place's own page gives it. */
export default function CheapThingsScreen() {
  const [things, setThings] = useState<CheapThing[] | null>(null);
  const [lines, setLines] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    moneyApi
      .cheapThings()
      .then((a) => {
        setThings(a.cheap_things);
        setLines(a.lines);
      })
      .catch((e) => setError(errorText(e, t('common.error'))));
  }, []);

  return (
    <Screen back>
      <View style={{ gap: 4 }}>
        <Title>{t('cheap.title')}</Title>
        <Muted>{t('cheap.intro')}</Muted>
      </View>
      {lines.map((line, i) => (
        <InfoNote key={i} icon="info">
          {line}
        </InfoNote>
      ))}
      {error ? <ErrorBox message={error} /> : null}
      {!error && !things ? <Loading /> : null}
      {things && !things.length ? <Body>{t('cheap.none')}</Body> : null}
      {things?.map((c, i) => (
        <Card key={`${c.name}-${i}`} style={{ gap: 6 }}>
          <Tag label={categoryLabel(c.category)} tone="info" />
          <Strong>{c.name}</Strong>
          {c.cost_note ? <Text style={styles.cost}>{c.cost_note}</Text> : null}
          {c.address ? <Muted>{c.address}</Muted> : null}
          {c.hours ? <Muted>{t('support.hours', { hours: c.hours })}</Muted> : null}
          <SourceLink url={c.source_url} />
          {c.read_on ? <Muted>{t('cheap.priced', { date: formatDay(c.read_on) })}</Muted> : null}
        </Card>
      ))}
    </Screen>
  );
}

const styles = StyleSheet.create({
  cost: { fontFamily: fonts.medium, fontSize: 14, lineHeight: 20, color: colors.text },
});
