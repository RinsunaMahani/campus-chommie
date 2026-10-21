/**
 * Find my course's state for one visit: the marks first, then your points at
 * every university, the university you open and its programmes, and the
 * plan. It lives in memory only: nothing is saved on the phone or logged
 * (CLAUDE.md: POPIA and minors; learners may be under 18), so leaving the
 * course finder forgets it all. Changing a mark forgets every answer built
 * on the old marks.
 */
import { createContext, ReactNode, useContext, useMemo, useState } from 'react';

import { MarkRow, startingRows } from './marks';
import { AssessAnswer, Plan, PointsAnswer, UniversitySummary } from './types';

type CourseFinder = {
  rows: MarkRow[];
  points: PointsAnswer | null;
  /** The university open in step 3, from its answer. */
  university: UniversitySummary | null;
  answer: AssessAnswer | null;
  plan: Plan | null;
  setRows: (rows: MarkRow[]) => void;
  setPoints: (p: PointsAnswer) => void;
  setAnswer: (a: AssessAnswer) => void;
  setPlan: (p: Plan) => void;
  reset: () => void;
};

const Context = createContext<CourseFinder | null>(null);

export function CourseFinderProvider({ children }: { children: ReactNode }) {
  const [rows, setRows] = useState<MarkRow[]>(startingRows);
  const [points, setPoints] = useState<PointsAnswer | null>(null);
  const [answer, setAnswer] = useState<AssessAnswer | null>(null);
  const [plan, setPlan] = useState<Plan | null>(null);

  const value = useMemo<CourseFinder>(
    () => ({
      rows,
      points,
      university: answer?.university ?? null,
      answer,
      plan,
      setRows: (next) => {
        setRows(next);
        setPoints(null);
        setAnswer(null);
        setPlan(null);
      },
      setPoints,
      // Another university: its plan starts again; the marks and points stay.
      setAnswer: (a) => {
        setAnswer(a);
        setPlan(null);
      },
      setPlan,
      reset: () => {
        setRows(startingRows());
        setPoints(null);
        setAnswer(null);
        setPlan(null);
      },
    }),
    [rows, points, answer, plan],
  );

  return <Context.Provider value={value}>{children}</Context.Provider>;
}

export function useCourseFinder(): CourseFinder {
  const value = useContext(Context);
  if (!value) throw new Error('useCourseFinder must be used inside CourseFinderProvider');
  return value;
}
