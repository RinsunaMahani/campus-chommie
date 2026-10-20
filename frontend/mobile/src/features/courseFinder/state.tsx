/**
 * Find my course's state: the marks first, then your points at every university, the university you open
 * and its programmes, and the plan. It lives in memory for one visit (CLAUDE.md: POPIA and minors; learners
 * may be under 18), unless the learner switches on "Remember my marks on this phone": then only their
 * subjects and marks are kept in the phone's secure storage, and switching it off deletes them. Nothing is
 * ever kept on our server or logged. Changing a mark forgets every answer built on the old marks.
 */
import { createContext, ReactNode, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import { MarkRow, startingRows } from './marks';
import { forgetMarks, loadMarks, saveMarks } from './rememberMarks';
import { AssessAnswer, Plan, PointsAnswer, UniversitySummary } from './types';

type CourseFinder = {
  rows: MarkRow[];
  points: PointsAnswer | null;
  /** The university open in step 3, from its answer. */
  university: UniversitySummary | null;
  answer: AssessAnswer | null;
  plan: Plan | null;
  /** Whether this phone keeps the marks between visits (off unless the learner switches it on). */
  remember: boolean;
  setRows: (rows: MarkRow[]) => void;
  setPoints: (p: PointsAnswer) => void;
  setAnswer: (a: AssessAnswer) => void;
  setPlan: (p: Plan) => void;
  setRemember: (on: boolean) => void;
  reset: () => void;
};

const Context = createContext<CourseFinder | null>(null);

export function CourseFinderProvider({ children }: { children: ReactNode }) {
  const [rows, setRowsState] = useState<MarkRow[]>(startingRows);
  const [points, setPoints] = useState<PointsAnswer | null>(null);
  const [answer, setAnswerState] = useState<AssessAnswer | null>(null);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [remember, setRememberState] = useState(false);

  // Marks this phone remembers from an earlier visit (only if the learner switched remembering on).
  useEffect(() => {
    let live = true;
    loadMarks().then((saved) => {
      if (!live || !saved) return;
      setRowsState(saved);
      setRememberState(true);
    });
    return () => {
      live = false;
    };
  }, []);

  const setRows = useCallback(
    (next: MarkRow[]) => {
      setRowsState(next);
      setPoints(null);
      setAnswerState(null);
      setPlan(null);
      if (remember) void saveMarks(next);
    },
    [remember],
  );

  const setRemember = useCallback(
    (on: boolean) => {
      setRememberState(on);
      void (on ? saveMarks(rows) : forgetMarks());
    },
    [rows],
  );

  const value = useMemo<CourseFinder>(
    () => ({
      rows,
      points,
      university: answer?.university ?? null,
      answer,
      plan,
      remember,
      setRows,
      setPoints,
      // Another university: its plan starts again; the marks and points stay.
      setAnswer: (a) => {
        setAnswerState(a);
        setPlan(null);
      },
      setPlan,
      setRemember,
      reset: () => {
        setRowsState(startingRows());
        setPoints(null);
        setAnswerState(null);
        setPlan(null);
        if (remember) void saveMarks(startingRows());
      },
    }),
    [rows, points, answer, plan, remember, setRows, setRemember],
  );

  return <Context.Provider value={value}>{children}</Context.Provider>;
}

export function useCourseFinder(): CourseFinder {
  const value = useContext(Context);
  if (!value) throw new Error('useCourseFinder must be used inside CourseFinderProvider');
  return value;
}
