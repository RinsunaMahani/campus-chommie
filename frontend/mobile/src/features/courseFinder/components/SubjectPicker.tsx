/**
 * Find my course's subject picker: every subject in folders of related
 * subjects, one folder open at a time, so a learner ticks all their subjects
 * (every language at once) and taps Done. Closing it any other way changes
 * nothing. Show it only while picking: it starts from `chosen` each time.
 */
import { Feather } from '@expo/vector-icons';
import { useRef, useState } from 'react';
import { Modal, Pressable, ScrollView, StyleSheet, Text, useWindowDimensions, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Button } from '@/shared/components/Button';
import { t } from '@/shared/i18n';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import {
  Blocked,
  blocked,
  FolderId,
  FOLDERS,
  folderHint,
  folderName,
  MAX_POINTS_ONLY,
  MAX_SUBJECTS,
  pointsOnlyCount,
  Subject,
  subjectName,
} from '../subjects';

type Props = { chosen: string[]; onDone: (chosen: string[]) => void; onClose: () => void };

export function SubjectPicker({ chosen, onDone, onClose }: Props) {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const { height } = useWindowDimensions();
  const [draft, setDraft] = useState<string[]>(chosen);
  const [open, setOpen] = useState<FolderId | null>('languages');
  const scroll = useRef<ScrollView>(null);
  // The folder just opened: once laid out, it scrolls to the top of the sheet,
  // since closing a long folder above it moves it out of view.
  const opening = useRef<FolderId | null>(null);

  function toggleFolder(id: FolderId) {
    const next = open === id ? null : id;
    opening.current = next;
    setOpen(next);
  }

  function toggle(id: string) {
    if (draft.includes(id)) setDraft(draft.filter((s) => s !== id));
    else if (!blocked(draft, id)) setDraft([...draft, id]);
  }

  const full = draft.length >= MAX_SUBJECTS;
  const pointsFull = pointsOnlyCount(draft) >= MAX_POINTS_ONLY;

  function subtitle(subject: Subject, block: Blocked | null): string | null {
    if (block?.why === 'chosen_in') return t('courseFinder.chosenIn', { folder: folderName(block.folder) });
    // The further-languages folder says it once, under its name.
    if (subject.kind === 'points' && subject.folder !== 'more_languages') return t('courseFinder.pointsOnly');
    return null;
  }

  return (
    <Modal visible transparent animationType="fade" onRequestClose={onClose}>
      <View style={styles.backdrop}>
        <Pressable style={{ flex: 1 }} onPress={onClose} accessibilityLabel={t('courseFinder.close')} />
        <SafeAreaView edges={['bottom']} style={styles.sheet}>
          <View style={styles.handle} />
          <Text style={styles.title}>{t('courseFinder.chooseSubjects')}</Text>
          <Text style={styles.hint}>{t('courseFinder.pickerHint')}</Text>
          {full ? (
            <Text style={styles.limit}>{t('courseFinder.pickerFull', { n: MAX_SUBJECTS })}</Text>
          ) : pointsFull ? (
            <Text style={styles.limit}>{t('courseFinder.pointsOnlyFull', { n: MAX_POINTS_ONLY })}</Text>
          ) : null}

          <ScrollView ref={scroll} style={{ maxHeight: Math.round(height * 0.6) }} contentContainerStyle={{ paddingBottom: 6 }}>
            {FOLDERS.map((f, fi) => {
              const isOpen = open === f.id;
              const picked = f.subjects.filter((s) => draft.includes(s.id));
              const hint = folderHint(f.id);
              return (
                <View
                  key={f.id}
                  style={fi < FOLDERS.length - 1 && styles.folderRule}
                  onLayout={(e) => {
                    if (opening.current !== f.id) return;
                    opening.current = null;
                    scroll.current?.scrollTo({ y: e.nativeEvent.layout.y, animated: true });
                  }}>
                  <Pressable
                    accessibilityRole="button"
                    accessibilityState={{ expanded: isOpen }}
                    accessibilityLabel={`${folderName(f.id)}${picked.length ? `, ${t('courseFinder.folderChosen', { n: picked.length })}` : ''}`}
                    onPress={() => toggleFolder(f.id)}
                    style={styles.folder}>
                    <Feather name={isOpen ? 'chevron-down' : 'chevron-right'} size={18} color={colors.ink} />
                    <View style={{ flex: 1 }}>
                      <Text style={styles.folderName}>{folderName(f.id)}</Text>
                      {picked.length ? (
                        <Text style={styles.folderPicked} numberOfLines={1}>
                          {picked.map((s) => subjectName(s.id)).join(', ')}
                        </Text>
                      ) : null}
                    </View>
                    {picked.length ? (
                      <View style={styles.count}>
                        <Text style={styles.countText}>{picked.length}</Text>
                      </View>
                    ) : null}
                  </Pressable>

                  {isOpen ? (
                    <View style={styles.options}>
                      {hint ? <Text style={styles.folderHint}>{hint}</Text> : null}
                      {f.subjects.map((s, i) => {
                        const on = draft.includes(s.id);
                        const block = blocked(draft, s.id);
                        const sub = subtitle(s, block);
                        return (
                          <Pressable
                            key={s.id}
                            accessibilityRole="checkbox"
                            accessibilityState={{ checked: on, disabled: !!block }}
                            disabled={!!block}
                            onPress={() => toggle(s.id)}
                            style={[styles.option, i < f.subjects.length - 1 && styles.optionRule, !!block && styles.optionOff]}>
                            <View style={{ flex: 1 }}>
                              <Text style={styles.optLabel}>{subjectName(s.id)}</Text>
                              {sub ? <Text style={styles.optSub}>{sub}</Text> : null}
                            </View>
                            <View style={[styles.check, on && styles.checkOn]}>
                              {on ? <Feather name="check" size={14} color={colors.pillText} /> : null}
                            </View>
                          </Pressable>
                        );
                      })}
                    </View>
                  ) : null}
                </View>
              );
            })}
          </ScrollView>

          <Button
            title={draft.length ? t('courseFinder.doneCount', { n: draft.length }) : t('courseFinder.done')}
            onPress={() => onDone(draft)}
          />
        </SafeAreaView>
      </View>
    </Modal>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
  backdrop: { flex: 1, backgroundColor: colors.overlay },
  sheet: {
    backgroundColor: colors.white,
    borderTopLeftRadius: 22,
    borderTopRightRadius: 22,
    paddingHorizontal: 20,
    paddingBottom: 14,
    gap: 8,
  },
  handle: { alignSelf: 'center', width: 40, height: 4, borderRadius: 2, backgroundColor: colors.line, marginTop: 10, marginBottom: 4 },
  title: { fontFamily: fonts.display, fontSize: 20, letterSpacing: -0.3, color: colors.ink },
  hint: { fontFamily: fonts.body, fontSize: 14, color: colors.textMuted, marginTop: -4 },
  limit: { fontFamily: fonts.semibold, fontSize: 14, color: colors.marigoldDeep },
  folderRule: { borderBottomWidth: 1, borderBottomColor: colors.line },
  folder: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 14 },
  folderName: { fontFamily: fonts.semibold, fontSize: 15.5, color: colors.ink },
  folderPicked: { fontFamily: fonts.body, fontSize: 13.5, color: colors.textMuted, marginTop: 2 },
  count: {
    minWidth: 24,
    height: 24,
    paddingHorizontal: 7,
    borderRadius: radius.pill,
    backgroundColor: colors.accentTint,
    alignItems: 'center',
    justifyContent: 'center',
  },
  countText: { fontFamily: fonts.bold, fontSize: 13.5, color: colors.accentDeep },
  options: { paddingLeft: 28, paddingBottom: 6 },
  folderHint: { fontFamily: fonts.body, fontSize: 13.5, color: colors.textMuted, marginTop: -6, marginBottom: 2 },
  option: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 12 },
  optionRule: { borderBottomWidth: 1, borderBottomColor: colors.line },
  optionOff: { opacity: 0.45 },
  optLabel: { fontFamily: fonts.semibold, fontSize: 16, color: colors.text },
  optSub: { fontFamily: fonts.body, fontSize: 13.5, color: colors.textMuted, marginTop: 2 },
  check: { width: 22, height: 22, borderRadius: 6, borderWidth: 2, borderColor: colors.line, alignItems: 'center', justifyContent: 'center' },
  checkOn: { backgroundColor: colors.accent, borderColor: colors.accent },
});
