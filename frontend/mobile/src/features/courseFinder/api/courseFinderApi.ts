/**
 * The course finder's calls. No account: nothing is signed in, so no token is
 * sent. Marks travel in the request body only, never in a URL (a URL lands in
 * browser history and server logs), and nothing here stores or logs them.
 */
import { api } from '@/shared/api/client';

import { ApplyInfoAnswer, AssessAnswer, DeadlinesAnswer, FirstStepsAnswer, FunderAnswer, FunderDetail, FundingCard, FundingFilters, FundingListAnswer, Mark, Plan, PointsAnswer, ProgrammeListAnswer, SavedFundingCard, SavedFundingListAnswer, UniversityCardInfo, UniversityMapAnswer } from '../types';

function toQuery(filters?: FundingFilters): string {
  if (!filters) return '';
  const entries = Object.entries(filters).filter(([, v]) => typeof v === 'string' && v.length > 0);
  if (!entries.length) return '';
  const qs = entries.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v as string)}`).join('&');
  return `?${qs}`;
}

export const courseFinderApi = {
  /** Every university, A to Z, with its fee and where its applications stand today. */
  universities: () => api<{ universities: UniversityCardInfo[] }>('GET', '/universities').then((d) => d.universities),

  /** Every programme, without marks: one university's, or a search across all of them. */
  programmes: (filters: { q?: string; university?: string; page?: number }) => {
    const entries = Object.entries(filters).filter(([, v]) => v !== undefined && v !== '');
    const qs = entries.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`).join('&');
    return api<ProgrammeListAnswer>('GET', `/programmes${qs ? `?${qs}` : ''}`);
  },

  /** What closes soonest across universities and funders. */
  deadlines: () => api<DeadlinesAnswer>('GET', '/deadlines'),

  /** How to apply to one university, without marks. */
  applyInfo: (university: string) => api<ApplyInfoAnswer>('GET', `/pathways/apply/${encodeURIComponent(university)}`),

  /** Your points at every university we cover, each by its own rule, and how many programmes you meet. */
  points: (marks: Mark[]) => api<PointsAnswer>('POST', '/pathways/points', { marks }),

  assess: (university: string, marks: Mark[]) => api<AssessAnswer>('POST', '/pathways/assess', { university, marks }),

  plan: (university: string, goal: string, marks: Mark[]) =>
    api<{ plan: Plan }>('POST', '/pathways/plan', { university, goal, marks }).then((d) => d.plan),

  /** The funding list (public, nothing sent): for what's open now. */
  funding: () => api<{ funders: FundingCard[] }>('GET', '/funding').then((d) => d.funders),

  /** The full funding list with counts, fields and optional filters. */
  fundingList: (filters?: FundingFilters) =>
    api<FundingListAnswer>('GET', `/funding${toQuery(filters)}`),

  /** One funder in full: who can apply, covers, obligations, how to apply and sources. */
  funder: (id: string): Promise<FunderDetail> =>
    api<FunderAnswer>('GET', `/funding/${id}`).then((d) => ({
      ...d.funder,
      confirmed: d.confirmed,
      notice: d.notice,
    })),

  /** The signed-in student's saved funding list, open first, each with saved_on. */
  savedFundingList: () => api<SavedFundingListAnswer>('GET', '/me/funding', undefined, { auth: true }),

  /** Save a funder to the signed-in student's list. */
  saveFunder: (id: string) =>
    api<{ funder: SavedFundingCard }>('PUT', `/me/funding/${id}`, undefined, { auth: true }).then((d) => d.funder),

  /** Remove a funder from the signed-in student's saved list. */
  unsaveFunder: (id: string) => api<Record<string, never>>('DELETE', `/me/funding/${id}`, undefined, { auth: true }),

  /** Steps from accepting an offer to your first lecture. */
  firstSteps: (universityId: string): Promise<FirstStepsAnswer> =>
    api<FirstStepsAnswer>('GET', `/universities/${universityId}/first-steps`),

  /** A university's campus maps from OpenStreetMap, with attribution and ODbL licence. */
  universityMap: (universityId: string, campus?: string): Promise<UniversityMapAnswer> => {
    const qs = campus ? `?campus=${encodeURIComponent(campus)}` : '';
    return api<UniversityMapAnswer>('GET', `/universities/${universityId}/map${qs}`);
  },
};

/** Every message in a 422's field errors (marshmallow's nested shape), flattened. */
export function fieldMessages(errors: unknown): string[] {
  if (typeof errors === 'string') return [errors];
  if (Array.isArray(errors)) return errors.flatMap(fieldMessages);
  if (errors && typeof errors === 'object') return Object.values(errors).flatMap(fieldMessages);
  return [];
}

