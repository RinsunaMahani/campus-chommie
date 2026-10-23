/** My money's calls: signed in, and only ever the student's own (the server scopes every one). */
import { api } from '@/shared/api/client';

import {
  AffordAnswer,
  CheapThing,
  CheckinInput,
  CheckinStatus,
  FixedCost,
  FixedCostInput,
  GoalInput,
  IncomeInput,
  IncomeSource,
  MoneyGoal,
  MoneyPlan,
  Payment,
  Settings,
  SpendingDay,
  Summary,
} from '../types';

const auth = { auth: true };

export const moneyApi = {
  summary: (late = false) => api<Summary>('GET', `/money/summary${late ? '?late=true' : ''}`, undefined, auth),

  settings: () => api<{ settings: Settings | null }>('GET', '/money/settings', undefined, auth).then((d) => d.settings),
  saveSettings: (settings: Settings) =>
    api<{ settings: Settings }>('PUT', '/money/settings', settings, auth).then((d) => d.settings),

  incomeSources: () =>
    api<{ income_sources: IncomeSource[] }>('GET', '/money/income-sources', undefined, auth).then((d) => d.income_sources),
  addIncome: (input: IncomeInput) =>
    api<{ income_source: IncomeSource }>('POST', '/money/income-sources', input, auth).then((d) => d.income_source),
  updateIncome: (id: string, input: IncomeInput) =>
    api<{ income_source: IncomeSource }>('PUT', `/money/income-sources/${id}`, input, auth).then((d) => d.income_source),
  removeIncome: (id: string) => api<Record<string, never>>('DELETE', `/money/income-sources/${id}`, undefined, auth),

  payments: () => api<{ payments: Payment[] }>('GET', '/money/payments', undefined, auth).then((d) => d.payments),
  setReceived: (id: string, received: boolean) =>
    api<{ payment: Payment }>('PATCH', `/money/payments/${id}`, { received }, auth).then((d) => d.payment),

  spending: (days = 30) =>
    api<{ spending: SpendingDay[] }>('GET', `/money/spending?days=${days}`, undefined, auth).then((d) => d.spending),
  setSpending: (day: string, amountCents: number) =>
    api<{ spending: SpendingDay }>('PUT', `/money/spending/${day}`, { amount_cents: amountCents }, auth).then((d) => d.spending),
  removeSpending: (day: string) => api<Record<string, never>>('DELETE', `/money/spending/${day}`, undefined, auth),

  /** Nothing is stored: the price is used once on the server and dropped. */
  afford: (amountCents: number) => api<AffordAnswer>('POST', '/money/afford', { amount_cents: amountCents }, auth),
  plan: () => api<MoneyPlan>('GET', '/money/plan', undefined, auth),
  addGoal: (input: GoalInput) => api<{ goal: MoneyGoal }>('POST', '/money/goals', input, auth).then((d) => d.goal),
  changeGoal: (id: string, input: Partial<GoalInput>) =>
    api<{ goal: MoneyGoal }>('PATCH', `/money/goals/${encodeURIComponent(id)}`, input, auth).then((d) => d.goal),
  removeGoal: (id: string) => api<Record<string, never>>('DELETE', `/money/goals/${encodeURIComponent(id)}`, undefined, auth),

  cheapThings: () =>
    api<{ cheap_things: CheapThing[]; lines: string[] }>('GET', '/money/cheap-things', undefined, auth),

  fixedCosts: () =>
    api<{ fixed_costs: FixedCost[] }>('GET', '/money/fixed-costs', undefined, auth).then((d) => d.fixed_costs),
  addFixedCost: (input: FixedCostInput) =>
    api<{ fixed_cost: FixedCost }>('POST', '/money/fixed-costs', input, auth).then((d) => d.fixed_cost),
  updateFixedCost: (id: string, input: Partial<FixedCostInput>) =>
    api<{ fixed_cost: FixedCost }>('PATCH', `/money/fixed-costs/${encodeURIComponent(id)}`, input, auth).then((d) => d.fixed_cost),
  removeFixedCost: (id: string) =>
    api<Record<string, never>>('DELETE', `/money/fixed-costs/${encodeURIComponent(id)}`, undefined, auth),

  checkinStatus: () => api<CheckinStatus>('GET', '/money/checkin', undefined, auth),
  submitCheckin: (input: CheckinInput) => api<CheckinStatus>('POST', '/money/checkin', input, auth),
};
