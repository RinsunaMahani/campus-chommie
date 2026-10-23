import { Feather } from '@expo/vector-icons';
import { useFocusEffect } from 'expo-router';
import { ComponentProps, useCallback, useEffect, useMemo, useState } from 'react';
import { Image, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { studentHeader } from '@/features/profile/components/HeaderTools';
import { errorText } from '@/shared/api/errors';
import { Card, IconTile, InfoNote, Tag } from '@/shared/components/Parts';
import { Screen } from '@/shared/components/Screen';
import { SourceLink } from '@/shared/components/SourceLink';
import { ErrorBox, Loading } from '@/shared/components/Status';
import { Body, Muted, Strong } from '@/shared/components/Text';
import { MessageKey, t } from '@/shared/i18n';
import { formatDay } from '@/shared/lib/dates';
import { Palette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import { moneyApi } from '../api/moneyApi';
import { CheapThing } from '../types';

type IconName = ComponentProps<typeof Feather>['name'];

function categoryIcon(category?: string | null): IconName {
  const cat = (category || '').toLowerCase();
  if (cat.includes('outdoor') || cat.includes('park') || cat.includes('nature') || cat.includes('garden')) return 'sun';
  if (cat.includes('museum') || cat.includes('art') || cat.includes('gallery')) return 'bookmark';
  if (cat.includes('heritage') || cat.includes('history') || cat.includes('monument')) return 'compass';
  if (cat.includes('sport') || cat.includes('walk') || cat.includes('hike')) return 'activity';
  if (cat.includes('market') || cat.includes('shop')) return 'shopping-bag';
  return 'map-pin';
}

function categoryLabel(category?: string | null): string {
  if (!category) return '';
  const key = `cheap.category.${category.toLowerCase()}` as MessageKey;
  const label = t(key);
  if (label !== key) return label;
  return category.charAt(0).toUpperCase() + category.slice(1);
}

type UniversityMeta = {
  id: string;
  name: string;
  confirmed?: boolean;
  notice?: string | null;
};

/**
 * Free and cheap places near the student's campus, each with its price as the place's own page gives it.
 * Used for both the Outdoors tab and the Money screen's "Cheap things nearby" route.
 */
export default function CheapThingsScreen({
  back,
  tab,
}: {
  back?: boolean;
  tab?: boolean;
} = {}) {
  const isTab = tab ?? !back;
  const hasBack = back ?? false;
  const styles = useStyles(makeStyles);

  const [things, setThings] = useState<CheapThing[] | null>(null);
  const [lines, setLines] = useState<string[]>([]);
  const [university, setUniversity] = useState<UniversityMeta | null>(null);
  const [campus, setCampus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState<string>('all');

  const load = useCallback(() => {
    return moneyApi
      .cheapThings()
      .then((a) => {
        setThings(a.cheap_things);
        setLines(a.lines);
        const u = (a as unknown as { university?: UniversityMeta | null }).university;
        const c = (a as unknown as { campus?: string | null }).campus;
        setUniversity(u ?? null);
        setCampus(c ?? null);
        setError(null);
      })
      .catch((e) => setError(errorText(e, t('common.error'))))
      .finally(() => setRefreshing(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  const categories = useMemo(() => {
    if (!things) return [];
    const set = new Set<string>();
    for (const t of things) {
      if (t.category) set.add(t.category);
    }
    return Array.from(set);
  }, [things]);

  const chips = useMemo(() => {
    return [
      { id: 'all', label: 'All' },
      { id: 'free', label: 'Free' },
      ...categories.map((cat) => ({ id: cat, label: categoryLabel(cat) })),
    ];
  }, [categories]);

  const filtered = useMemo(() => {
    if (!things) return [];
    if (filter === 'free') {
      return things.filter((c) => Boolean(c.free));
    }
    if (filter !== 'all') {
      return things.filter((c) => (c.category || '').toLowerCase() === filter.toLowerCase());
    }
    return things;
  }, [things, filter]);

  return (
    <Screen
      tab={isTab}
      back={hasBack}
      title={t('cheap.title')}
      subtitle={t('cheap.intro')}
      onRefresh={() => {
        setRefreshing(true);
        load();
      }}
      refreshing={refreshing}
      {...studentHeader(false)}>
      {campus && university ? (
        <View style={styles.metaRow}>
          <Muted>{`${university.name} · ${campus}`}</Muted>
        </View>
      ) : null}

      {university && !university.confirmed && university.notice ? (
        <InfoNote icon="info">{university.notice}</InfoNote>
      ) : null}

      {lines
        .filter((line) => line !== t('cheap.none'))
        .map((line, i) => (
          <InfoNote key={i} icon="info">
            {line}
          </InfoNote>
        ))}

      {error ? <ErrorBox message={error} /> : null}
      {!error && !things ? <Loading /> : null}

      {things && things.length > 0 ? (
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.chips}
          style={styles.chipsScroll}>
          {chips.map(({ id, label }) => {
            const on = filter === id;
            return (
              <Pressable
                key={id}
                accessibilityRole="button"
                accessibilityState={{ selected: on }}
                accessibilityLabel={label}
                onPress={() => setFilter(id)}
                style={[styles.chip, on && styles.chipOn]}>
                <Text style={[styles.chipText, on && styles.chipTextOn]}>{label}</Text>
              </Pressable>
            );
          })}
        </ScrollView>
      ) : null}

      {things && !filtered.length ? (
        <View style={styles.empty}>
          <IconTile name="sun" size={48} />
          <Body>{t('cheap.none')}</Body>
        </View>
      ) : null}

      {filtered.map((c, i) => (
        <Card key={`${c.name}-${i}`} style={styles.card}>
          <View style={styles.cardHeader}>
            {c.photo_url || c.photo ? (
              <Image source={{ uri: c.photo_url || c.photo || '' }} style={styles.photo} resizeMode="cover" accessible={false} />
            ) : (
              <IconTile name={categoryIcon(c.category)} size={44} />
            )}
            <View style={{ flex: 1, gap: 4 }}>
              <View style={styles.badgeRow}>
                <Tag label={categoryLabel(c.category)} tone="info" />
                {c.free ? <Tag label="Free" tone="jade" /> : null}
              </View>
              <Strong>{c.name}</Strong>
            </View>
          </View>
          {c.cost_note ? <Text style={styles.cost}>{c.cost_note}</Text> : null}
          {c.address ? <Muted>{c.address}</Muted> : null}
          {c.hours ? <Muted>{t('support.hours', { hours: c.hours })}</Muted> : null}
          <SourceLink url={c.source_url} />
          {c.read_on ? (
            <Muted>{t('cheap.priced', { date: formatDay(c.read_on) })}</Muted>
          ) : (
            <Muted>{t('support.notVerified')}</Muted>
          )}
        </Card>
      ))}
    </Screen>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
    metaRow: {
      gap: 4,
    },
    chipsScroll: {
      marginHorizontal: -20,
    },
    chips: {
      paddingHorizontal: 20,
      gap: 8,
      paddingVertical: 2,
    },
    chip: {
      paddingHorizontal: 14,
      paddingVertical: 8,
      borderRadius: radius.pill,
      borderWidth: 1,
      borderColor: colors.line,
      backgroundColor: colors.white,
    },
    chipOn: {
      backgroundColor: colors.ink,
      borderColor: colors.ink,
    },
    chipText: {
      fontFamily: fonts.semibold,
      fontSize: 14,
      color: colors.ink,
    },
    chipTextOn: {
      color: colors.pillText,
    },
    card: {
      gap: 10,
    },
    cardHeader: {
      flexDirection: 'row',
      alignItems: 'flex-start',
      gap: 12,
    },
    badgeRow: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: 6,
      alignItems: 'center',
    },
    photo: {
      width: 44,
      height: 44,
      borderRadius: radius.sm,
      backgroundColor: colors.iconTile,
    },
    cost: {
      fontFamily: fonts.medium,
      fontSize: 15,
      lineHeight: 20,
      color: colors.text,
    },
    empty: {
      alignItems: 'center',
      gap: 12,
      paddingVertical: 32,
    },
  });
