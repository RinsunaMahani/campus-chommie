/** Support for the signed-in student's campus. */
import { api } from '@/shared/api/client';

import { SupportAnswer } from '../types';

export const supportApi = {
  forMyCampus: () => api<SupportAnswer>('GET', '/support', undefined, { auth: true }),
};
