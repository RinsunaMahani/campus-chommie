import { LegalDocument } from './types';

/**
 * Terms of Use. Plain words first; a legal professional checks the final
 * text. Bump the version (here and in the backend's TERMS_VERSION) when it
 * changes, so users are asked again.
 */
export const TERMS_OF_USE: LegalDocument = {
  version: '0.1-draft',
  title: 'Terms of Use',
  effectiveDate: '9 October 2026',
  draftNotice: 'Draft for team review. A legal professional must check these terms before Campus Chommie is offered to the public.',
  sections: [
    {
      heading: '1. What Campus Chommie is',
      paragraphs: [
        'Campus Chommie is an app that helps students plan: which programmes fit their marks, what their week looks like, how long their money lasts, and where to find support on campus.',
        'It is a planning tool. It is not run by any university, NSFAS or bank, and it does not make admission, funding or academic decisions.',
      ],
    },
    {
      heading: '2. Check before you rely on it',
      paragraphs: [
        'Admission rules, dates and contacts in the app come from official sources, each with the date it was last checked. They can change. Always confirm with the university or funder before you act.',
        'Anything we have not checked yet is marked "Not verified yet". Meeting a minimum requirement never guarantees a place.',
      ],
    },
    {
      heading: '3. Your own numbers',
      paragraphs: [
        'Money and marks in the app are the amounts you enter yourself. Forecasts and projections are estimates from your own entries, not financial or academic advice.',
        'Campus Chommie never moves money and never asks for your bank or NSFAS login details.',
      ],
    },
    {
      heading: '4. Your account',
      paragraphs: [
        'You must be 18 or older to have an account. Keep your password to yourself: you are responsible for what is done with your account.',
        'You can close your account at any time from Account security.',
      ],
    },
    {
      heading: '5. Using the app fairly',
      paragraphs: [
        'Do not post anyone else\'s personal information, and do not use the app to mislead, harass or harm anyone. Do not try to reach information that is not yours, or to disrupt the service.',
        'We may remove content or close accounts that break these rules.',
      ],
    },
    {
      heading: '6. Your wellbeing',
      paragraphs: [
        'Campus Chommie does not give medical, psychological or financial advice. If you are struggling, please contact the support services on your campus. In an emergency, contact emergency services.',
      ],
    },
    {
      heading: '7. Changes',
      paragraphs: [
        'When these terms change, the version number goes up and the app asks you to agree again before you carry on.',
      ],
    },
  ],
};
