/** A student's classes: join, start, leave, the rep's tools, announcements and their confirmation. */
import { api } from '@/shared/api/client';
import { ClassEvent } from '@/features/week/types';

import { Candidate, ClassSummary, ConfirmBody, RepCode } from '../types';

const auth = { auth: true };

export const classesApi = {
  mine: () => api<{ classes: ClassSummary[] }>('GET', '/classes/mine', undefined, auth).then((d) => d.classes),

  create: (body: { university: string; campus: string | null; module_code: string; module_name: string | null; year: number }) =>
    api<{ class: ClassSummary }>('POST', '/classes', body, auth).then((d) => d.class),

  join: (code: string) => api<{ class: ClassSummary; joined: boolean }>('POST', '/classes/join', { code }, auth),

  repCode: (classId: string) => api<RepCode>('POST', `/classes/${classId}/reps`, undefined, auth),

  events: (classId: string) =>
    api<{ events: ClassEvent[] }>('GET', `/classes/${classId}/events`, undefined, auth).then((d) => d.events),

  announce: (classId: string, text: string) =>
    api<{ candidate: Candidate }>('POST', `/classes/${classId}/announcements`, { text }, auth).then((d) => d.candidate),

  candidates: (classId: string) =>
    api<{ candidates: Candidate[] }>('GET', `/classes/${classId}/candidates`, undefined, auth).then((d) => d.candidates),

  confirm: (candidateId: string, body: ConfirmBody) =>
    api<{ event: ClassEvent; lines: string[] }>('POST', `/candidates/${candidateId}/confirm`, body, auth),

  /** Leave the class. Its confirmed dates go from your week; the class stays for everyone else. */
  leave: (classId: string) => api<Record<string, never>>('DELETE', `/classes/${classId}/membership`, undefined, auth),

  discard: (candidateId: string) => api<Record<string, never>>('POST', `/candidates/${candidateId}/discard`, undefined, auth),
};
