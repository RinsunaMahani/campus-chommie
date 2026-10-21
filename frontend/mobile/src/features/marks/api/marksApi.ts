/** My marks' calls: the student's own modules and assessments only. */
import { api } from '@/shared/api/client';

import { Module } from '../types';

const auth = { auth: true };

type ModuleBody = { code: string; name: string | null; target?: number };
type AssessmentBody = { name: string; weight: number; mark: number | null };

export const marksApi = {
  modules: () => api<{ modules: Module[] }>('GET', '/academics/modules', undefined, auth).then((d) => d.modules),

  addModule: (body: ModuleBody) => api<{ module: Module }>('POST', '/academics/modules', body, auth).then((d) => d.module),

  removeModule: (id: string) => api<Record<string, never>>('DELETE', `/academics/modules/${id}`, undefined, auth),

  addAssessment: (moduleId: string, body: AssessmentBody) =>
    api<{ module: Module }>('POST', `/academics/modules/${moduleId}/assessments`, body, auth).then((d) => d.module),

  updateAssessment: (moduleId: string, assessmentId: string, body: AssessmentBody) =>
    api<{ module: Module }>('PUT', `/academics/modules/${moduleId}/assessments/${assessmentId}`, body, auth).then((d) => d.module),

  removeAssessment: (moduleId: string, assessmentId: string) =>
    api<{ module: Module }>('DELETE', `/academics/modules/${moduleId}/assessments/${assessmentId}`, undefined, auth).then((d) => d.module),
};
