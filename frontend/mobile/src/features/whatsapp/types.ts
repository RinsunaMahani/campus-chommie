export type Bot = { number: string | null; chat_link: string | null };

export type WhatsAppStatus = {
  available: boolean;
  linked: number;
  linked_on: string[];
  bot: Bot | null;
};

export type LinkCode = {
  code: string;
  message: string;
  expires_at: string;
  minutes: number;
  bot: Bot;
  send_link: string | null;
};
