/**
 * "Remember my marks on this phone": off unless the learner switches it on. Then their subjects and marks
 * are kept in the phone's secure storage (Android Keystore / iOS Keychain), never sent anywhere except to
 * work out an answer, and switching it off deletes them. On the web preview there's no secure storage, so
 * nothing is kept there. Only subjects and percentages: no name, school or anything else.
 */
import * as SecureStore from 'expo-secure-store';

import { MarkRow } from './marks';

const KEY = 'campus-chommie.marks.v1';

function isRows(value: unknown): value is MarkRow[] {
  return (
    Array.isArray(value) &&
    value.length <= 20 &&
    value.every((r) => r && typeof r.subject === 'string' && r.subject.length <= 40 && typeof r.percent === 'string' && r.percent.length <= 5)
  );
}

/** The marks this phone remembers, or null when it remembers none. */
export async function loadMarks(): Promise<MarkRow[] | null> {
  try {
    const raw = await SecureStore.getItemAsync(KEY);
    if (!raw) return null;
    const rows: unknown = JSON.parse(raw);
    return isRows(rows) ? rows.map((r) => ({ subject: r.subject, percent: r.percent })) : null;
  } catch {
    return null;
  }
}

export async function saveMarks(rows: MarkRow[]): Promise<void> {
  try {
    await SecureStore.setItemAsync(KEY, JSON.stringify(rows.map((r) => ({ subject: r.subject, percent: r.percent }))));
  } catch {
    // No secure storage here (the web preview): the marks last for this visit only.
  }
}

export async function forgetMarks(): Promise<void> {
  try {
    await SecureStore.deleteItemAsync(KEY);
  } catch {
    // Nothing was kept.
  }
}
