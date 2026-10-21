/** My money's calls: signed in, and only ever the student's own (the server scopes every one). */
import { api } from '@/shared/api/client';

import { CheapThing, IncomeInput, IncomeSource, Payment, Settings, SpendingDay, Summary } from '../types';

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

  cheapThings: () =>
    api<{ cheap_things: CheapThing[]; lines: string[] }>('GET', '/money/cheap-things', undefined, auth),
};
