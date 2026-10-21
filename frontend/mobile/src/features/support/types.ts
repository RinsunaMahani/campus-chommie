/** The Support screen's data (backend: GET /support): every kind of support for the student's campus. */

/** A campus support service, from the university's own page. */
export type Service = {
  name: string;
  contact: string | null;
  hours: string | null;
  note: string | null;
  source_url: string | null;
  /** When we read it on the university's page. */
  read_on: string | null;
  /** When a person last checked it: null until then. */
  last_verified: string | null;
};

export type SupportKind = {
  kind: string;
  /** Why there's nothing to show ("Not verified yet", or why crisis lines aren't shown yet). */
  line: string | null;
  services: Service[];
};

export type SupportAnswer = {
  university: { id: string; name: string; confirmed: boolean; notice: string | null } | null;
  campus: string | null;
  campus_name: string | null;
  kinds: SupportKind[];
  lines: string[];
};
