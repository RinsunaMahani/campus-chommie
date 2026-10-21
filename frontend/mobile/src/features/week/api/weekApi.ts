/** The week strip and flags on events: signed in, scoped to the student's own classes. */
import { api } from '@/shared/api/client';

import { ClassEvent, FlagReason, WeekAnswer } from '../types';

const auth = { auth: true };

export const weekApi = {
  weeks: (weeks = 8, from?: string) =>
    api<WeekAnswer>('GET', `/week?weeks=${weeks}${from ? `&from=${from}` : ''}`, undefined, auth),

  flag: (eventId: string, reason: FlagReason) =>
    api<{ event: ClassEvent }>('POST', `/events/${eventId}/flag`, { reason }, auth).then((d) => d.event),

  unflag: (eventId: string) => api<{ event: ClassEvent }>('DELETE', `/events/${eventId}/flag`, undefined, auth).then((d) => d.event),
};
