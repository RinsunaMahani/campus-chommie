/** The signed-in student's own timetable and exams: owner-only on the server. A PDF sent to import is read and
 * dropped there; only what the student then saves with addMany is kept. */
import { api } from '@/shared/api/client';

import {
  ActivitiesAnswer,
  Activity,
  ActivityInput,
  EntryInput,
  FindTimeAnswer,
  ExamEntry,
  ExamInput,
  ExamsAnswer,
  ImportAnswer,
  ImportLayout,
  PickedPdf,
  TimetableAnswer,
  TimetableEntry,
} from '../types';

const auth = { auth: true };

export const timetableApi = {
  mine: () => api<TimetableAnswer>('GET', '/me/timetable', undefined, auth),
  add: (input: EntryInput) => api<TimetableAnswer & { entry: TimetableEntry }>('POST', '/me/timetable', input, auth),
  addMany: (entries: EntryInput[], replace: boolean) =>
    api<TimetableAnswer>('POST', '/me/timetable/batch', { entries, replace }, auth),
  change: (id: string, input: Partial<EntryInput>) =>
    api<TimetableAnswer & { entry: TimetableEntry }>('PATCH', `/me/timetable/${encodeURIComponent(id)}`, input, auth),
  remove: (id: string) => api<TimetableAnswer>('DELETE', `/me/timetable/${encodeURIComponent(id)}`, undefined, auth),
  importPdf: (pdf: PickedPdf, layout: ImportLayout) => {
    const form = new FormData();
    form.append('layout', layout);
    // A browser hands over the File itself; a phone a uri that React Native's FormData uploads.
    if (pdf.file) form.append('file', pdf.file, pdf.name);
    else form.append('file', { uri: pdf.uri, name: pdf.name, type: pdf.mimeType ?? 'application/pdf' } as unknown as Blob);
    return api<ImportAnswer>('POST', '/me/timetable/import', form, auth);
  },
};

export const examsApi = {
  mine: () => api<ExamsAnswer>('GET', '/me/exams', undefined, auth),
  add: (input: ExamInput) => api<ExamsAnswer & { exam: ExamEntry }>('POST', '/me/exams', input, auth),
  addMany: (exams: ExamInput[], replace: boolean) => api<ExamsAnswer>('POST', '/me/exams/batch', { exams, replace }, auth),
  remove: (id: string) => api<ExamsAnswer>('DELETE', `/me/exams/${encodeURIComponent(id)}`, undefined, auth),
};

export const activitiesApi = {
  mine: () => api<ActivitiesAnswer>('GET', '/me/activities', undefined, auth),
  add: (input: ActivityInput) => api<ActivitiesAnswer & { activity: Activity }>('POST', '/me/activities', input, auth),
  change: (id: string, input: Partial<ActivityInput>) =>
    api<ActivitiesAnswer & { activity: Activity }>('PATCH', `/me/activities/${encodeURIComponent(id)}`, input, auth),
  remove: (id: string) => api<ActivitiesAnswer>('DELETE', `/me/activities/${encodeURIComponent(id)}`, undefined, auth),
  findTime: (minutes: number, days = 7) => api<FindTimeAnswer>('POST', '/me/activities/find-time', { minutes, days }, auth),
};
