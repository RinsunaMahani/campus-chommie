/**
 * The course finder's calls. No account: nothing is signed in, so no token is
 * sent. Marks travel in the request body only, never in a URL (a URL lands in
 * browser history and server logs), and nothing here stores or logs them.
 */
import { api } from '@/shared/api/client';

import { AssessAnswer, FundingCard, Mark, Plan, PointsAnswer } from '../types';

export const courseFinderApi = {
  /** Your points at every university we cover, each by its own rule, and how many programmes you meet. */
  points: (marks: Mark[]) => api<PointsAnswer>('POST', '/pathways/points', { marks }),

  assess: (university: string, marks: Mark[]) => api<AssessAnswer>('POST', '/pathways/assess', { university, marks }),

  plan: (university: string, goal: string, marks: Mark[]) =>
    api<{ plan: Plan }>('POST', '/pathways/plan', { university, goal, marks }).then((d) => d.plan),

  /** The funding list (public, nothing sent): for what's open now. */
  funding: () => api<{ funders: FundingCard[] }>('GET', '/funding').then((d) => d.funders),
};

/** Every message in a 422's field errors (marshmallow's nested shape), flattened. */
export function fieldMessages(errors: unknown): string[] {
  if (typeof errors === 'string') return [errors];
  if (Array.isArray(errors)) return errors.flatMap(fieldMessages);
  if (errors && typeof errors === 'object') return Object.values(errors).flatMap(fieldMessages);
  return [];
}

