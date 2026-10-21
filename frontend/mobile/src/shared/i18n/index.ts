/**
 * i18n plumbing. English is the only visible language until a fluent speaker
 * signs a translation off (docs/translation_review.md); then its dictionary is
 * added to MESSAGES and to LANGUAGES, and nothing else changes.
 *
 * A missing key in another language falls back to English, so a half-done
 * translation can never show a blank.
 */
import { en, MessageKey } from './en';

export type { MessageKey } from './en';

type Dictionary = Partial<Record<MessageKey, string>>;

/** Languages a learner can pick. Visible only once signed off. */
export const LANGUAGES = { en: 'English' } as const;
export type Language = keyof typeof LANGUAGES;

const MESSAGES: Record<Language, Dictionary> = { en };

let current: Language = 'en';

export function language(): Language {
  return current;
}

/** Switch language (only to a signed-off one). */
export function setLanguage(lang: Language) {
  if (lang in MESSAGES) current = lang;
}

/** The text for a key, with {placeholders} filled in. */
export function t(key: MessageKey, values?: Record<string, string | number>): string {
  const text = MESSAGES[current][key] ?? en[key];
  if (!values) return text;
  return text.replace(/\{(\w+)\}/g, (whole, name: string) => (name in values ? String(values[name]) : whole));
}

