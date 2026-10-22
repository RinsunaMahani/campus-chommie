import * as WebBrowser from 'expo-web-browser';
import { router, useLocalSearchParams } from 'expo-router';
import { ComponentProps, useCallback, useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { useSession } from '@/features/auth/session/SessionProvider';
import { Button } from '@/shared/components/Button';
import { Card, Tag } from '@/shared/components/Parts';
import { PhotoHero } from '@/shared/components/PhotoHero';
import { SourceLink } from '@/shared/components/SourceLink';
import { ErrorBox } from '@/shared/components/Status';
import { Body, Muted, Overline, Strong } from '@/shared/components/Text';
import { Monogram } from '@/shared/components/UniMonogram';
import { t } from '@/shared/i18n';
import { formatRand } from '@/shared/lib/money';
import { SkeletonCards } from '@/shared/motion/Shimmer';
import { Palette, useStyles } from '@/shared/theme/palette';
import { fonts } from '@/shared/theme/tokens';

import { courseFinderApi } from '../api/courseFinderApi';
import { ApplyWindows } from '../components/ApplyBox';
import { funderMonogram, funderPhoto } from '../funderPhotos';
import { ApplyWindow, FunderDetail } from '../types';
import { errorText, formatDay } from '../words';

type TagTone = NonNullable<ComponentProps<typeof Tag>['tone']>;

function tagTone(status: string): TagTone {
  if (status === 'open') return 'jade';
  if (status === 'closing_soon' || status === 'late_open') return 'marigold';
  if (status === 'closed' || status === 'not_published') return 'muted';
  return 'info';
}

function useSignedIn(): boolean {
  try {
    return useSession().status === 'active';
  } catch {
    return false;
  }
}

/**
 * Funder detail screen: public information about one funder in full.
 * 1. The field's photo on top (none for a funder of any field) with Save on it; who runs it and what kind,
 *    its name, and chips: status, closing date, fields, stages. The dates in full are in How to apply, once.
 * 2. What it covers (amount check or not published)
 * 3. Who can apply
 * 4. What you owe back (hidden if null)
 * 5. How to apply, fee, documents, windows, apply on site button
 * 6. Sources with retrieval date
 */
export default function FunderDetailScreen() {
  const styles = useStyles(makeStyles);
  const { id } = useLocalSearchParams<{ id: string }>();
  const signedIn = useSignedIn();
  const [funder, setFunder] = useState<FunderDetail | null>(null);
  const [savedOn, setSavedOn] = useState<string | null>(null);
  const [signInPrompt, setSignInPrompt] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    courseFinderApi
      .funder(id)
      .then(setFunder)
      .catch((e) => setError(errorText(e)))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    if (!signedIn || !id) return;
    courseFinderApi
      .savedFundingList()
      .then((res) => {
        const found = res.funders.find((f) => f.id === id);
        setSavedOn(found?.saved_on ?? null);
      })
      .catch(() => undefined);
  }, [signedIn, id]);

  const activeSavedOn = signedIn ? savedOn : null;

  const toggleSave = useCallback(async () => {
    if (!funder) return;
    if (!signedIn) {
      setSignInPrompt(true);
      return;
    }
    const prev = activeSavedOn;
    if (prev) {
      setSavedOn(null);
      try {
        await courseFinderApi.unsaveFunder(funder.id);
      } catch {
        setSavedOn(prev);
      }
    } else {
      try {
        const saved = await courseFinderApi.saveFunder(funder.id);
        setSavedOn(saved.saved_on);
      } catch (e) {
        setError(errorText(e));
      }
    }
  }, [funder, signedIn, activeSavedOn]);

  const photo = funder ? funderPhoto(funder) : null;

  return (
    <PhotoHero
      photo={photo}
      action={
        funder
          ? {
              icon: 'bookmark',
              label: activeSavedOn ? t('courseFinder.unsaveFunder', { name: funder.name }) : t('courseFinder.saveFunder', { name: funder.name }),
              on: !!activeSavedOn,
              onPress: toggleSave,
            }
          : undefined
      }
      head={
        <>
          {funder ? (
            <View style={styles.headRow}>
              <Monogram label={funderMonogram(funder)} size={48} />
              <View style={{ flex: 1, gap: 2 }}>
                <Text style={styles.kind}>{`${funder.sector_label} ${funder.kind_label?.toLowerCase() ?? ''}`.trim()}</Text>
                {funder.short_name && funder.short_name !== funder.name ? <Strong>{funder.short_name}</Strong> : null}
              </View>
            </View>
          ) : null}
          <Text style={styles.title} accessibilityRole="header">
            {funder?.name ?? t('courseFinder.fundingTitle')}
          </Text>
          {funder ? (
            <View style={styles.chipRow}>
              <Tag label={funder.label} tone={tagTone(funder.status)} />
              {funder.closes ? <Tag label={formatDay(funder.closes)} tone="info" /> : null}
              {funder.fields?.slice(0, 2).map((f) => <Tag key={f.id} label={f.label} tone="jade" />)}
              {funder.stages?.map((st) => <Tag key={st.id} label={st.label} tone="info" />)}
            </View>
          ) : null}
          {activeSavedOn ? <Muted>{t('courseFinder.savedOn', { date: formatDay(activeSavedOn) })}</Muted> : null}
        </>
      }>
      {loading ? <SkeletonCards count={3} /> : null}

      {error ? (
        <ErrorBox
          message={error}
          onRetry={() => {
            if (!id) return;
            setError(null);
            setLoading(true);
            courseFinderApi
              .funder(id)
              .then(setFunder)
              .catch((e) => setError(errorText(e)))
              .finally(() => setLoading(false));
          }}
        />
      ) : null}

      {funder ? (
        <View style={{ gap: 14 }}>
          {signInPrompt && !signedIn ? (
            <Card style={styles.card}>
              <Body>{t('courseFinder.saveSignInPrompt')}</Body>
              <Button
                title={t('courseFinder.saveSignInButton')}
                variant="accent"
                compact
                icon="log-in"
                onPress={() => router.push('/(auth)/sign-in')}
              />
            </Card>
          ) : null}

          {/* 2. What it covers */}
          <Card style={styles.card}>
            <Overline>{t('courseFinder.funderCovers')}</Overline>
            {funder.covers == null ? (
              <Body>{t('courseFinder.funderNotPublished')}</Body>
            ) : (
              <>
                {funder.covers.items.map((item, i) => (
                  <View key={i} style={styles.item}>
                    <Text style={styles.bullet}>•</Text>
                    <Text style={styles.itemText}>{item}</Text>
                  </View>
                ))}
                {!funder.covers.items.some((item) => /\bR\s?\d/i.test(item)) ? (
                  <Text style={styles.noteLine}>{t('courseFinder.funderNoAmount')}</Text>
                ) : null}
                <SourceLink url={funder.covers.source_url} />
              </>
            )}
          </Card>

          {/* 3. Who can apply */}
          <Card style={styles.card}>
            <Overline>{t('courseFinder.funderWho')}</Overline>
            {funder.who_can_apply == null ? (
              <Body>{t('courseFinder.funderNotPublished')}</Body>
            ) : (
              <>
                {funder.who_can_apply.items.map((item, i) => (
                  <View key={i} style={styles.item}>
                    <Text style={styles.bullet}>•</Text>
                    <Text style={styles.itemText}>{item}</Text>
                  </View>
                ))}
                <SourceLink url={funder.who_can_apply.source_url} />
              </>
            )}
          </Card>

          {/* 4. What you owe back (hidden if null) */}
          {funder.obligations != null ? (
            <Card style={styles.card}>
              <Overline>{t('courseFinder.funderOwe')}</Overline>
              {funder.obligations.items.map((item, i) => (
                <View key={i} style={styles.item}>
                  <Text style={styles.bullet}>•</Text>
                  <Text style={styles.itemText}>{item}</Text>
                </View>
              ))}
              <SourceLink url={funder.obligations.source_url} />
            </Card>
          ) : null}

          {/* 5. How to apply */}
          <Card style={styles.card}>
            <Overline>{t('courseFinder.funderApply')}</Overline>
            {funder.apply.how ? <Text style={styles.line}>{funder.apply.how}</Text> : null}

            <View style={{ gap: 2 }}>
              <Strong>{t('courseFinder.fee')}</Strong>
              <Text style={styles.line}>
                {funder.apply.fee_cents != null
                  ? formatRand(funder.apply.fee_cents)
                  : t('courseFinder.funderNoFee')}
              </Text>
              {funder.apply.fee_note ? <Muted>{funder.apply.fee_note}</Muted> : null}
            </View>

            {funder.apply.documents?.items?.length ? (
              <View style={{ gap: 6 }}>
                <Strong>{t('courseFinder.funderDocuments')}</Strong>
                {funder.apply.documents.items.map((item, i) => (
                  <View key={i} style={styles.item}>
                    <Text style={styles.bullet}>•</Text>
                    <Text style={styles.itemText}>{item}</Text>
                  </View>
                ))}
                <SourceLink url={funder.apply.documents.source_url} />
              </View>
            ) : null}

            {funder.apply.windows?.length ? (
              <View style={{ gap: 6 }}>
                <Strong>{t('courseFinder.applyDates')}</Strong>
                <ApplyWindows windows={funder.apply.windows as unknown as ApplyWindow[]} />
              </View>
            ) : null}

            {funder.apply.url ? (
              <Button
                title={t('courseFinder.applyOnSite')}
                variant="primary"
                icon="external-link"
                onPress={() => WebBrowser.openBrowserAsync(funder.apply.url!)}
              />
            ) : null}
            <SourceLink url={funder.apply.source_url} />
          </Card>

          {/* 6. Sources */}
          {funder.sources?.length ? (
            <Card style={styles.card}>
              <Overline>{t('courseFinder.funderSources')}</Overline>
              {funder.sources.map((s, i) => (
                <View key={`${s.url}-${i}`} style={{ gap: 2 }}>
                  <SourceLink url={s.url} />
                  {s.retrieved ? (
                    <Muted style={{ fontSize: 13 }}>
                      {t('courseFinder.readOn', { date: formatDay(s.retrieved) })}
                    </Muted>
                  ) : null}
                </View>
              ))}
            </Card>
          ) : null}

          {!funder.confirmed && funder.notice ? <Muted>{funder.notice}</Muted> : null}
        </View>
      ) : null}
    </PhotoHero>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
  card: { gap: 10, padding: 14 },
  headRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  kind: { fontFamily: fonts.bold, fontSize: 13, letterSpacing: 0.8, textTransform: 'uppercase', color: colors.textMuted },
  title: { fontFamily: fonts.display, fontSize: 28, lineHeight: 33, letterSpacing: -0.4, color: colors.ink },
  chipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  line: { fontFamily: fonts.body, fontSize: 14.5, lineHeight: 20, color: colors.text },
  noteLine: { fontFamily: fonts.body, fontSize: 14, lineHeight: 19, color: colors.textMuted },
  item: { flexDirection: 'row', gap: 8 },
  bullet: { fontFamily: fonts.bold, fontSize: 15, lineHeight: 20, color: colors.textFaint },
  itemText: { flex: 1, fontFamily: fonts.body, fontSize: 14.5, lineHeight: 20, color: colors.text },
});
