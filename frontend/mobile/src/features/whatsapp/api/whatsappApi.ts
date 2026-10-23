/** Linking the student's WhatsApp number to the bot: status, a one-time code, unlinking. */
import { api } from '@/shared/api/client';

import { LinkCode, WhatsAppStatus } from '../types';

const auth = { auth: true };

export const whatsappApi = {
  status: () => api<WhatsAppStatus>('GET', '/me/whatsapp', undefined, auth),

  code: () => api<LinkCode>('POST', '/me/whatsapp/code', undefined, auth),

  unlink: () => api<unknown>('DELETE', '/me/whatsapp', undefined, auth),
};
