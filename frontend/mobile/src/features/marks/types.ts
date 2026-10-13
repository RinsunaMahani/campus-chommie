/** My marks (backend: domains/student/academics). Owner-only; weights and marks are percentages. */

export type Assessment = { id: string; name: string; weight: number; mark: number | null };

export type Module = {
  id: string;
  code: string;
  name: string | null;
  target: number;
  total_weight: number;
  assessments: Assessment[];
  /** Where the student stands, and the average needed on the rest for the target. */
  standing: {
    completed_weight: number;
    remaining_weight: number;
    current: number | null;
    needed: number | null;
    status: string;
    message: string;
  };
  /** A projected final mark with a likely range, from the results so far. */
  projection: {
    based_on: number;
    projected: number | null;
    low: number | null;
    high: number | null;
    below_target: boolean;
    message: string;
  } | null;
  lines: string[];
};
