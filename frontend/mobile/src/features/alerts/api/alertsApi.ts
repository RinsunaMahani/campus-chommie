/** Today's alerts and the student's updates: signed in, scoped to the student. */
import { api } from '@/shared/api/client';

import { AlertsAnswer } from '../types';

const auth = { auth: true };

export const alertsApi = {
  today: () => api<AlertsAnswer>('GET', '/alerts', undefined, auth),
};
