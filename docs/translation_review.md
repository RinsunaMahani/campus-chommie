# Translation review

As of 26 October 2026, English is the only interface language exposed in
`frontend/mobile/src/shared/i18n/index.ts`. No translated dictionary or fluent-speaker approval is recorded.
This file records approvals; creating an entry does not itself approve a translation.

Before enabling another language, the owner selects it and a fluent speaker reviews its complete dictionary,
screen context, placeholders, accessibility labels, admissions terminology and wellbeing wording. Translated
admission rules must appear beside the original English and source. Do not machine-translate for release.

Record each completed review here:

| Language | Dictionary path and revision | Fluent reviewer | Review date | Issues resolved | Approved for release |
|---|---|---|---|---|---|
| None yet | — | — | — | — | No |

Only after sign-off should the reviewed dictionary be added to `MESSAGES` and `LANGUAGES`. Check missing-key
fallbacks and interpolated values, and test layouts with the translated text on narrow screens.

Named school-language subjects in course assessment are separate from translating the interface. Supporting an
Afrikaans, isiZulu or Sepedi school mark does not imply that an interface translation has been reviewed.
