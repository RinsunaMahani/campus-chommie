/** The signed-in student's week in review. Nothing is stored: the server works it out on each request. */
import { api } from '@/shared/api/client';

import { WeekReview, WhichWeek } from '../types';

export const reviewApi = {
  mine: (week: WhichWeek = 'auto') => api<WeekReview>('GET', `/me/week-review?week=${week}`, undefined, { auth: true }),
};
