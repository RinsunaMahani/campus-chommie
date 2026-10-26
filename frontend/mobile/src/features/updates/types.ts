/** The student's updates (backend: GET /me/notifications): class updates, funding reminders, security alerts. */

export type Update = {
  id: string;
  kind: string;
  title: string;
  body: string;
  icon: string | null;
  /** Where it leads: a class ({type: "class", id}), a funder ({type: "funding", id}) or the week in review ({type: "review", id}). */
  link: { type: string; id: string } | null;
  created_at: string;
  read_at: string | null;
};

/** An alert topic the student may switch off (security alerts are always on). */
export type Switch = { topic: string; label: string; on: boolean };
