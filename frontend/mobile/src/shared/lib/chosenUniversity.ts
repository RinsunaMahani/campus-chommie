/**
 * The university a learner chose in the course finder before creating an
 * account, so onboarding can preselect it after sign-up and email
 * verification (which don't pass route parameters on). In memory only: never
 * stored, gone when the app closes. Only the university's id: never marks.
 */
let chosen: string | null = null;

export function rememberUniversity(id: string): void {
  chosen = id;
}

/** The remembered id, once: reading it clears it. */
export function takeUniversity(): string | null {
  const id = chosen;
  chosen = null;
  return id;
}
