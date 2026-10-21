/** The student's own updates and the switches for them. */
import { api } from '@/shared/api/client';

import { Switch, Update } from '../types';

const auth = { auth: true };

export const updatesApi = {
  list: () => api<{ notifications: Update[] }>('GET', '/me/notifications', undefined, auth).then((d) => d.notifications),

  read: (id: string) => api<unknown>('POST', `/me/notifications/${id}/read`, undefined, auth),

  readAll: () => api<unknown>('POST', '/me/notifications/read-all', undefined, auth),

  switches: () => api<{ switches: Switch[] }>('GET', '/me/notifications/switches', undefined, auth).then((d) => d.switches),

  setSwitch: (topic: string, on: boolean) =>
    api<{ switches: Switch[] }>('PUT', '/me/notifications/switches', { [topic]: on }, auth).then((d) => d.switches),
};
