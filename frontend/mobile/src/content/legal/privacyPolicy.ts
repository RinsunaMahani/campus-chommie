import { LegalDocument } from './types';

/**
 * Privacy Policy, written for POPIA (Protection of Personal Information
 * Act 4 of 2013). Every item here must match what the app and backend
 * actually do; when a feature starts collecting something new, this
 * changes first and the version goes up (here and in the backend's
 * PRIVACY_POLICY_VERSION).
 */
export const PRIVACY_POLICY: LegalDocument = {
  version: '0.1-draft',
  title: 'Privacy Policy',
  effectiveDate: '9 October 2026',
  draftNotice: 'Draft for team review. A legal professional must check this policy before Campus Chommie is offered to the public.',
  sections: [
    {
      heading: '1. Who we are',
      paragraphs: [
        'Campus Chommie helps South African students from choosing a course to graduating. In this policy "Campus Chommie", "we" and "us" means the operator of the Campus Chommie app, who is the responsible party for your personal information under POPIA.',
        'Information officer and contact details: not confirmed yet. They will be added here before the app is offered to the public.',
      ],
    },
    {
      heading: '2. Who can have an account',
      paragraphs: [
        'You must be 18 or older to create an account. You confirm this when you sign up.',
      ],
    },
    {
      heading: '3. What we collect, and why',
      paragraphs: [
        'Account: your email address, and a password that is stored only as a one-way hash nobody can read back. Why: to create your account, let you sign in and send you sign-in codes and security alerts.',
        'Your agreement: which version of this policy and of the Terms of Use you accepted, your confirmation that you are 18 or older, when you did so, and the IP address and app details at that moment. Why: POPIA requires us to be able to show what you agreed to, and when.',
        'Sign-in security: the phones you sign in on (the kind of phone and a name for it), when each was last used, and a security key your phone creates (we only ever receive its public part). Why: to ask for an email code on a new phone, and to let you see and sign out your other phones.',
        'Security records: sign-ups, sign-ins, failed attempts and password changes, with the time, the email address used and the IP address. Why: to protect accounts and to investigate misuse.',
        "Your timetable, if you add one: each class's module code, kind (lecture, tutorial or practical), day, start and end time, and the venue and name if you type them. Why: to show your week as a calendar. Only you can see it; it is in your data export and is deleted with your account.",
      ],
    },
    {
      heading: '4. What we never collect',
      paragraphs: [
        'We never ask for your ID number or passport, bank or account numbers, or your NSFAS or banking login details. We never ask about your race, religion or health.',
        'We do not sell your personal information, and we do not use it for advertising.',
      ],
    },
    {
      heading: '5. As the app grows',
      paragraphs: [
        'Before a feature that uses new personal information is released (for example your university and campus, your marks, or your money entries), this policy is updated to say what is collected, why, who can see it and how long it is kept. The version number goes up and the app asks you to agree again.',
      ],
    },
    {
      heading: '6. Who can see your information',
      paragraphs: [
        'Your account details are yours. The people who run Campus Chommie can see technical and security records only to keep the service working and safe.',
        'The companies that host the app and send our emails process your information for us, only to provide those services.',
      ],
    },
    {
      heading: '7. How long we keep it',
      paragraphs: [
        'Sign-ups whose email is never confirmed are deleted after 7 days. Email codes are deleted a day after they are used or expire. Signed-out sessions and phones you no longer use are deleted 30 days later. In-app alerts are deleted after 90 days.',
        'How long security records are kept, and how a closed account\'s information is removed, is still being decided. It will be stated here before the app is offered to the public.',
      ],
    },
    {
      heading: '8. Your rights',
      paragraphs: [
        'You may ask what personal information we hold about you and get a copy, ask us to correct it, close your account, and object to how we use it.',
        'If you are unhappy with how we handle your information, you may complain to the Information Regulator (South Africa).',
      ],
    },
    {
      heading: '9. How we protect it',
      paragraphs: [
        'Passwords and codes are stored only as hashes. Sign-in on a new phone needs a code sent to your email. Repeated attempts are slowed down and blocked. Every request is checked so that you can only ever reach your own information.',
      ],
    },
  ],
};
