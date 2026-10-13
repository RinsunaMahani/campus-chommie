/** The signed-in student's profile, and the universities and campuses to choose from (the catalogue is public). */
import { api } from '@/shared/api/client';

import { Campus, Me, StudentProfile, UniversityChoice } from '../types';

const auth = { auth: true };

export const profileApi = {
  get: () => api<{ profile: StudentProfile }>('GET', '/me/profile', undefined, auth).then((d) => d.profile),

  save: (university: string, campus: string | null) =>
    api<{ profile: StudentProfile }>('PUT', '/me/profile', { university, campus }, auth).then((d) => d.profile),

  me: () => api<Me>('GET', '/me', undefined, auth),

  universities: () => api<{ universities: UniversityChoice[] }>('GET', '/universities').then((d) => d.universities),

  campuses: (university: string) =>
    api<{ university: { campuses: Campus[] } }>('GET', `/universities/${encodeURIComponent(university)}`).then((d) => d.university.campuses),
};
