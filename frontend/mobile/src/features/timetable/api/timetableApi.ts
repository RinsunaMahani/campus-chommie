/** The signed-in student's own timetable: owner-only on the server. */
import { api } from '@/shared/api/client';

import { EntryInput, TimetableAnswer, TimetableEntry } from '../types';

const auth = { auth: true };

export const timetableApi = {
  mine: () => api<TimetableAnswer>('GET', '/me/timetable', undefined, auth),
  add: (input: EntryInput) => api<TimetableAnswer & { entry: TimetableEntry }>('POST', '/me/timetable', input, auth),
  change: (id: string, input: Partial<EntryInput>) =>
    api<TimetableAnswer & { entry: TimetableEntry }>('PATCH', `/me/timetable/${encodeURIComponent(id)}`, input, auth),
  remove: (id: string) => api<TimetableAnswer>('DELETE', `/me/timetable/${encodeURIComponent(id)}`, undefined, auth),
};
