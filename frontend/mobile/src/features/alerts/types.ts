/** Home's alerts (backend: GET /alerts), worked out on each request and never stored. */

import { Service } from '@/features/support/types';

export type { Service };

export type ActionTarget = 'week' | 'money' | 'cheap_things' | 'marks' | 'support';

export type AlertAction = {
  text: string;
  target: ActionTarget;
  support_kind: string | null;
  /** A support action may carry the campus's own service. */
  service: Service | null;
};

export type Alert = {
  /** combined (a heavy week while money runs short), heavy_week, money, or module (a target out of reach). */
  kind: string;
  title: string;
  message: string;
  actions: AlertAction[];
};

export type AlertsAnswer = { today: string; alerts: Alert[]; notes: string[] };
