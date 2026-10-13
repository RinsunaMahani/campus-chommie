/**
 * Find my course's state for one visit: the university, the marks, the
 * matches and the plan. It lives in memory only: nothing is saved on the
 * phone or logged (CLAUDE.md: POPIA and minors; learners may be under 18),
 * so leaving the course finder forgets it all.
 */
import { createContext, ReactNode, useContext, useMemo, useState } from 'react';

import { MarkRow, startingRows } from './marks';
import { AssessAnswer, Plan, UniversitySummary } from './types';

type CourseFinder = {
  university: UniversitySummary | null;
  rows: MarkRow[];
  answer: AssessAnswer | null;
  plan: Plan | null;
  chooseUniversity: (u: UniversitySummary) => void;
  setRows: (rows: MarkRow[]) => void;
  setAnswer: (a: AssessAnswer) => void;
  setPlan: (p: Plan) => void;
  reset: () => void;
};

const Context = createContext<CourseFinder | null>(null);

export function CourseFinderProvider({ children }: { children: ReactNode }) {
  const [university, setUniversity] = useState<UniversitySummary | null>(null);
  const [rows, setRows] = useState<MarkRow[]>(startingRows);
  const [answer, setAnswer] = useState<AssessAnswer | null>(null);
  const [plan, setPlan] = useState<Plan | null>(null);

  const value = useMemo<CourseFinder>(
    () => ({
      university,
      rows,
      answer,
      plan,
      // Another university: its matches and plan start again; the marks stay.
      chooseUniversity: (u) => {
        setUniversity(u);
        setAnswer(null);
        setPlan(null);
      },
      setRows,
      setAnswer: (a) => {
        setAnswer(a);
        setPlan(null);
      },
      setPlan,
      reset: () => {
        setUniversity(null);
        setRows(startingRows());
        setAnswer(null);
        setPlan(null);
      },
    }),
    [university, rows, answer, plan],
  );

  return <Context.Provider value={value}>{children}</Context.Provider>;
}

export function useCourseFinder(): CourseFinder {
  const value = useContext(Context);
  if (!value) throw new Error('useCourseFinder must be used inside CourseFinderProvider');
  return value;
}
