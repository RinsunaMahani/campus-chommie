/** The student's own profile (backend: domains/student/profile) and who is signed in (GET /me). */

export type StudentProfile = {
  /** Null until onboarding: the app then asks for it. */
  university: string | null;
  university_name: string | null;
  campus: string | null;
  campus_name: string | null;
  confirmed_18_or_older_at: string | null;
};

export type Me = {
  id: string;
  email: string;
  /** A judge's demo account (`flask seed`): its data is fictional and the app says so. */
  demo: boolean;
};

export type Campus = { id: string; name: string; note?: string | null };

export type UniversityChoice = { id: string; name: string };
