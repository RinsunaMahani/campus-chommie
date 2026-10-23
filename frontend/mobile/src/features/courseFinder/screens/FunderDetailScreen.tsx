import * as WebBrowser from 'expo-web-browser';
import { Feather } from '@expo/vector-icons';
import { router, useLocalSearchParams } from 'expo-router';
import { ComponentProps, ReactNode, useCallback, useEffect, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

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
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts } from '@/shared/theme/tokens';

import { courseFinderApi } from '../api/courseFinderApi';
import { ApplyWindows } from '../components/ApplyBox';
import { funderMonogram, funderPhoto } from '../funderPhotos';
import { ApplyWindow, FunderDetail } from '../types';
import { errorText, formatDay } from '../words';

type TagTone = NonNullable<ComponentProps<typeof Tag>['tone']>;

function tagTone(status?: string | null): TagTone {
  if (status === 'open') return 'jade';
  if (status === 'closing_soon' || status === 'late_open') return 'marigold';
  if (status === 'closed' || status === 'not_published') return 'muted';
  return 'muted';
}

/**
 * Applications status in words: the closing or opening date when we have it, otherwise the server's own label for
 * the status ("No application needed", "Apply through the university", "Check the dates"...). Only a funder with
 * neither says "Not published".
 */
export function applicationStatusWords(funder: {
  status?: string | null;
  label?: string | null;
  opens?: string | null;
  closes?: string | null;
}): string {
  const { status, label, opens, closes } = funder;
  if (status === 'closing_soon' && closes) return `Closes on ${formatDay(closes)}`;
  if (status === 'opens_later' && opens) return `Opens on ${formatDay(opens)}`;
  return label || 'Not published';
}

function useSignedIn(): boolean {
  try {
    return useSession().status === 'active';
  } catch {
    return false;
  }
}

function SectionHeader({ icon, title }: { icon: ComponentProps<typeof Feather>['name']; title: string }) {
  const styles = useStyles(makeStyles);
  const colors = usePalette();
  return (
    <View style={styles.cardHeaderRow}>
      <Feather name={icon} size={16} color={colors.accentDeep} />
      <Overline>{title}</Overline>
    </View>
  );
}

/**
 * Long lists show the first 4 items, then a "Show all" button.
 */
function ExpandableList({
  items,
  renderItem,
}: {
  items: string[];
  renderItem?: (item: string, index: number) => ReactNode;
}) {
  const styles = useStyles(makeStyles);
  const [showAll, setShowAll] = useState(false);

  if (!items || items.length === 0) return null;

  const visible = showAll || items.length <= 4 ? items : items.slice(0, 4);
  const hasMore = items.length > 4 && !showAll;

  return (
    <View style={{ gap: 6 }}>
      {visible.map((item, i) =>
        renderItem ? (
          renderItem(item, i)
        ) : (
          <View key={i} style={styles.item}>
            <Text style={styles.bullet}>•</Text>
            <Text style={styles.itemText}>{item}</Text>
          </View>
        )
      )}
      {hasMore ? (
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Show all"
          onPress={() => setShowAll(true)}
          style={styles.showAllPressable}>
          <Text style={styles.showAllText}>Show all</Text>
        </Pressable>
      ) : null}
    </View>
  );
}

/**
 * Funder detail screen: public information about one funder in full.
 * Scannable in 10 seconds:
 * Top: funder name, funding group, application status in words.
 * Sections in order (cards with heading and icon, only shown when API sent that part):
 * 1. Who can apply
 * 2. What it covers
 * 3. What you give back
 * 4. Income limit
 * 5. How to apply (with link button)
 * 6. Dates
 * 7. At registration
 * 8. Tips
 * 9. Watch out
 * Bottom button: "Apply on their page" when there's an application link.
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
  const applyUrl = funder?.apply?.url || funder?.url || null;

  const rawIncomeLimit = funder ? funder.income_says ?? funder.income_limit : null;
  const incomeText =
    typeof rawIncomeLimit === 'string'
      ? rawIncomeLimit
      : typeof rawIncomeLimit === 'object' && rawIncomeLimit !== null
      ? (rawIncomeLimit as { text?: string }).text
      : null;
  const incomeItems: string[] | null =
    typeof rawIncomeLimit === 'object' && rawIncomeLimit !== null && Array.isArray((rawIncomeLimit as { items?: string[] }).items)
      ? (rawIncomeLimit as { items: string[] }).items
      : null;
  const incomeSourceUrl =
    typeof rawIncomeLimit === 'object' && rawIncomeLimit !== null
      ? (rawIncomeLimit as { source_url?: string | null }).source_url ?? null
      : (funder as { income_source_url?: string | null } | null)?.income_source_url ?? null;
  const hasIncomeLimit = Boolean(incomeText || (incomeItems && incomeItems.length > 0));

  const hasApply = Boolean(
    funder?.apply &&
      (funder.apply.how ||
        funder.apply.fee_cents != null ||
        funder.apply.fee_note ||
        funder.apply.documents?.items?.length ||
        funder.apply.url ||
        funder.apply.contact)
  );

  const atReg = funder?.at_registration;
  const afterItems = funder?.apply?.after?.length ? funder.apply.after : null;
  const hasAtRegistration = Boolean(
    atReg
      ? typeof atReg === 'string'
        ? atReg.length > 0
        : Boolean((atReg as { text?: string }).text || (atReg as { items?: string[] }).items?.length)
      : afterItems?.length
  );

  const tipsGroup = funder ? funder.tips ?? funder.apply?.tips : null;
  const warningsGroup = funder ? funder.warnings ?? funder.apply?.warnings : null;

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
                <Text style={styles.kind}>
                  {`${funder.sector_label || ''} ${funder.kind_label?.toLowerCase() || ''}`.trim() || funder.kind_label || funder.sector_label || ''}
                </Text>
                {funder.short_name && funder.short_name !== funder.name ? <Strong>{funder.short_name}</Strong> : null}
              </View>
            </View>
          ) : null}
          <Text style={styles.title} accessibilityRole="header">
            {funder?.name ?? t('courseFinder.fundingTitle')}
          </Text>
          {funder ? (
            <View style={styles.chipRow}>
              <Tag label={applicationStatusWords(funder)} tone={tagTone(funder.status)} />
              {funder.closes && funder.status === 'open' ? <Tag label={formatDay(funder.closes)} tone="info" /> : null}
              {funder.fields?.slice(0, 2).map((f) => <Tag key={f.id} label={f.label} tone="jade" />)}
              {funder.stages?.map((st) => <Tag key={st.id} label={st.label} tone="info" />)}
            </View>
          ) : null}
          {activeSavedOn ? <Muted>{t('courseFinder.savedOn', { date: formatDay(activeSavedOn) })}</Muted> : null}
        </>
      }
      footer={
        applyUrl ? (
          <Button
            title="Apply on their page"
            variant="primary"
            icon="external-link"
            onPress={() => WebBrowser.openBrowserAsync(applyUrl)}
          />
        ) : undefined
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

          {/* 1. Who can apply */}
          {funder.who_can_apply?.items?.length ? (
            <Card style={styles.card}>
              <SectionHeader icon="users" title={t('courseFinder.funderWho')} />
              <ExpandableList items={funder.who_can_apply.items} />
              <SourceLink url={funder.who_can_apply.source_url} />
            </Card>
          ) : null}

          {/* 2. What it covers */}
          {funder.covers?.items?.length ? (
            <Card style={styles.card}>
              <SectionHeader icon="shield" title={t('courseFinder.funderCovers')} />
              <ExpandableList items={funder.covers.items} />
              {!funder.covers.items.some((item) => /\bR\s?\d/i.test(item)) ? (
                <Text style={styles.noteLine}>{t('courseFinder.funderNoAmount')}</Text>
              ) : null}
              <SourceLink url={funder.covers.source_url} />
            </Card>
          ) : null}

          {/* 3. What you give back */}
          {funder.obligations?.items?.length ? (
            <Card style={styles.card}>
              <SectionHeader icon="repeat" title="What you give back" />
              <ExpandableList items={funder.obligations.items} />
              <SourceLink url={funder.obligations.source_url} />
            </Card>
          ) : null}

          {/* 4. Income limit */}
          {hasIncomeLimit ? (
            <Card style={styles.card}>
              <SectionHeader icon="credit-card" title="Income limit" />
              {incomeText ? <Text style={styles.line}>{incomeText}</Text> : null}
              {incomeItems?.length ? <ExpandableList items={incomeItems} /> : null}
              {incomeSourceUrl ? <SourceLink url={incomeSourceUrl} /> : null}
            </Card>
          ) : null}

          {/* 5. How to apply */}
          {hasApply ? (
            <Card style={styles.card}>
              <SectionHeader icon="send" title={t('courseFinder.funderApply')} />
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
                  <ExpandableList items={funder.apply.documents.items} />
                  <SourceLink url={funder.apply.documents.source_url} />
                </View>
              ) : null}

              {funder.apply.contact ? <Muted>{funder.apply.contact}</Muted> : null}

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
          ) : null}

          {/* 6. Dates */}
          {funder.apply?.windows?.length ? (
            <Card style={styles.card}>
              <SectionHeader icon="calendar" title="Dates" />
              <ApplyWindows windows={funder.apply.windows as unknown as ApplyWindow[]} />
            </Card>
          ) : null}

          {/* 7. At registration */}
          {hasAtRegistration ? (
            <Card style={styles.card}>
              <SectionHeader icon="clipboard" title="At registration" />
              {typeof atReg === 'string' ? (
                <Text style={styles.line}>{atReg}</Text>
              ) : (atReg as { text?: string })?.text ? (
                <>
                  <Text style={styles.line}>{(atReg as { text: string }).text}</Text>
                  {(atReg as { source_url?: string | null }).source_url ? (
                    <SourceLink url={(atReg as { source_url: string }).source_url} />
                  ) : null}
                </>
              ) : (atReg as { items?: string[] })?.items?.length ? (
                <>
                  <ExpandableList items={(atReg as { items: string[] }).items} />
                  {(atReg as { source_url?: string | null }).source_url ? (
                    <SourceLink url={(atReg as { source_url: string }).source_url} />
                  ) : null}
                </>
              ) : afterItems?.length ? (
                <>
                  <ExpandableList items={afterItems.map((a) => a.text)} />
                  {afterItems[0]?.source_url ? <SourceLink url={afterItems[0].source_url} /> : null}
                </>
              ) : null}
            </Card>
          ) : null}

          {/* 8. Tips */}
          {tipsGroup?.items?.length ? (
            <Card style={styles.card}>
              <SectionHeader icon="help-circle" title="Tips" />
              <ExpandableList items={tipsGroup.items} />
              <SourceLink url={tipsGroup.source_url} />
            </Card>
          ) : null}

          {/* 9. Watch out */}
          {warningsGroup?.items?.length ? (
            <Card style={styles.card}>
              <SectionHeader icon="alert-triangle" title="Watch out" />
              <ExpandableList items={warningsGroup.items} />
              <SourceLink url={warningsGroup.source_url} />
            </Card>
          ) : null}

          {/* Sources */}
          {funder.sources?.length ? (
            <Card style={styles.card}>
              <SectionHeader icon="book-open" title={t('courseFinder.funderSources')} />
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
    cardHeaderRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
    headRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
    kind: { fontFamily: fonts.bold, fontSize: 13, letterSpacing: 0.8, textTransform: 'uppercase', color: colors.textMuted },
    title: { fontFamily: fonts.display, fontSize: 28, lineHeight: 33, letterSpacing: -0.4, color: colors.ink },
    chipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
    line: { fontFamily: fonts.body, fontSize: 14.5, lineHeight: 20, color: colors.text },
    noteLine: { fontFamily: fonts.body, fontSize: 14, lineHeight: 19, color: colors.textMuted },
    item: { flexDirection: 'row', gap: 8 },
    bullet: { fontFamily: fonts.bold, fontSize: 15, lineHeight: 20, color: colors.textFaint },
    itemText: { flex: 1, fontFamily: fonts.body, fontSize: 14.5, lineHeight: 20, color: colors.text },
    showAllPressable: { paddingVertical: 4, alignSelf: 'flex-start' },
    showAllText: { fontFamily: fonts.semibold, fontSize: 13.5, color: colors.accentDeep },
  });
