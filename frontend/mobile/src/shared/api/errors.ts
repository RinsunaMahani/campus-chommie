/**
 * An API failure as one plain sentence for the screen: the server's own
 * words, or every field message on a 422 (marshmallow's nested shape).
 */
import { ApiError } from './client';

/** Every message in a 422's field errors, flattened. */
export function fieldMessages(errors: unknown): string[] {
  if (typeof errors === 'string') return [errors];
  if (Array.isArray(errors)) return errors.flatMap(fieldMessages);
  if (errors && typeof errors === 'object') return Object.values(errors).flatMap(fieldMessages);
  return [];
}

export function errorText(error: unknown, fallback: string): string {
  if (error instanceof ApiError) {
    if (error.code === 'VALIDATION_ERROR') {
      const messages = [...new Set(fieldMessages(error.errors))];
      if (messages.length) return messages.join(' ');
    }
    return error.message;
  }
  return fallback;
}
