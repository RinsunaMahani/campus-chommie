/**
 * The colleges calls. Public: no account, no token. A search travels in the URL (it's a college's name,
 * never anything about the learner), and the server neither stores nor logs it.
 */
import { api } from '@/shared/api/client';

import { CheckAnswer, CollegeAnswer, CollegeFilters, CollegeListAnswer } from '../types';

function toQuery(filters: CollegeFilters): string {
  const entries = Object.entries(filters).filter(([, v]) => v !== undefined && v !== '' && v !== null);
  return entries.length ? `?${entries.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`).join('&')}` : '';
}

export const collegesApi = {
  /** Public TVET colleges and DHET's registers, searched and filtered, a page at a time. */
  list: (filters: CollegeFilters = {}) => api<CollegeListAnswer>('GET', `/colleges${toQuery(filters)}`),

  /** One college in full. */
  college: (id: string) => api<CollegeAnswer>('GET', `/colleges/${encodeURIComponent(id)}`),

  /** "Is this college registered?" by name or DHET registration number. */
  check: (name: string) => api<CheckAnswer>('GET', `/colleges/check?name=${encodeURIComponent(name)}`),
};
