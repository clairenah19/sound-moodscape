# Moodscape — Language Accessibility Model Verification Report

Covers `predictLanguageProficiencyWithAI()` (`prompt.js`) — the Gemini-based feature that
estimates how navigable a province is for a visitor who speaks a chosen language and no
Korean. Same verification standard as `PROMPT_OUTPUT_COMPARISON_REPORT.md`: check the actual
prompt against the code, check what the output actually connects to, then test plausibility.

## What it actually connects to — checked first

`predictLanguageProficiencyWithAI()`'s result is rendered only by `renderLanguageScoreArea()`
in `ui.js`, inside the province panel's "Language accessibility" section. It is **not** read
by `REGION_MODEL`, `place.score`, `getMusicalKey()`, or `buildSunoPrompt()` — grepped for it
directly, zero references outside the language-panel rendering path. It's a standalone,
display-only feature: choosing a different language changes what a listener *reads*, not
anything they *hear*. Worth stating plainly since it's easy to assume a "province accessibility
score" feeds the same formula as the audio, and it doesn't.

## The actual prompt (verbatim from `prompt.js:539-543`)

> "You are estimating a 'language accessibility' score for Moodscape... Base your estimate on
> real, general knowledge of [province]: things like international airport/tourism volume,
> presence of [language]-speaking expat or immigrant communities, international schools or
> universities, prevalence of translated signage and menus... If [language] is English, you
> may anchor on South Korea's real EF English Proficiency Index (nationally 'moderate', roughly
> 520-550 in major metro areas) but still reason about this specific province rather than just
> repeating the national number. For every other language there is no equivalent published
> index, so this is a reasoned estimate from proxy signals, not a citation — say so plainly."

Schema requested: `score` (0-100 integer), `label` (string), `reasoning` (1-2 sentences).

## Methodology and the same limitation as before

**No Gemini key was available, so no live call was made.** What follows is a reasoned estimate
produced by following the prompt's own instructions directly — the same discipline it asks of
Gemini — not a verified model output. Unlike the music-prediction report, this prompt is
text-only (no photo), so there's no multimodal grounding step to add here; the only available
check is against the one real citable number the prompt itself names: EF EPI, for English only.

## Test 1 — English, against the one real anchor that exists

`about.html`'s four reference provinces already carry real 2024 EF EPI numbers. These are on
EF's own scale (roughly 400-700, banded Very Low/Low/Moderate/High/Very High), not the 0-100
scale this feature asks for — so this isn't a unit conversion, it's a check of whether a
reasoned 0-100 estimate **preserves the same relative order** as the real cited numbers.

| Province | Real EF EPI 2024 | My reasoned 0-100 estimate | Reasoning (following the prompt's own instructions) |
|---|---|---|---|
| Seoul | 550 (highest in Korea) | **~78** | Capital, dense international-school/expat presence, English signage and service-staff coverage in central districts is high in practice even though the *population-average* test score is only "moderate-high" |
| Incheon | 532 | **~68** | Boosted specifically by Incheon International Airport (~70M annual passengers) and Songdo's international business district — an atypical English-heavy enclave rather than city-wide proficiency |
| Busan | 520 | **~62** | Second city with real international infrastructure (APEC, BIFF) but far less concentrated than Seoul's or Incheon's, and it shows in the lower EF number too |
| Jeju | below national average, no city EF EPI | **~52** | Jeju's real tourism draw is heavily China/domestic-Korea oriented (historically visa-free for many Asian nationalities), which doesn't translate into English signage/service the way a Western-tourism-oriented destination would |

**Result: my reasoned order (Seoul > Incheon > Busan > Jeju) matches the real EF EPI order
exactly.** This is a genuine positive signal, not a foregone conclusion — the prompt explicitly
tells the model to reason about the *specific province* rather than just repeat the national
number, which creates real room for the reasoning to scramble the order (e.g., overweighting
Incheon's airport enough to rank it above Seoul). It didn't, here. This should be read as one
data point in favor of the feature's plausibility, not proof it would replicate with a live
model — the actual test (`DEVELOPMENT_PLAN.md` Priority 5) still requires a real key.

## Test 2 — a language with no citable index, for plausibility only

The prompt explicitly tells the model that for any language besides English, "there is no
equivalent published index, so this is a reasoned estimate from proxy signals, not a
citation." Two examples, checked for whether the *reasoning itself* stays honest about that,
not for numeric accuracy (there is nothing to check the number against):

**Vietnamese, Ulsan** (industrial shipbuilding city) — reasoned estimate: **~35/100**, label
"Low-moderate." Reasoning: Ulsan and nearby Gyeongsangnam-do industrial areas have a real,
sizeable Vietnamese migrant-worker population, which is exactly the kind of "expat/immigrant
community" proxy signal the prompt asks for — but that population is concentrated in
manufacturing workplaces, not in tourist-facing signage or services, so a visitor's actual
day-to-day navigability stays low despite the community's real presence. This is the kind of
distinction ("a proxy signal exists, but it doesn't translate to visitor-facing accessibility")
a good response should be able to draw — a response that only checked "is there a Vietnamese
community here" and returned a high score without that distinction would be a shallower one.

**Mandarin Chinese, Jeju** — reasoned estimate: **~55/100**, label "Moderate." Reasoning:
Jeju's Chinese tourism volume has historically been very large, with visa-free entry policies
specifically benefiting Chinese visitors, producing real Chinese-language signage and service
infrastructure at tourist sites — plausibly making Jeju's Mandarin accessibility *higher* than
its English accessibility (~52 above), despite Jeju scoring lowest of the four reference
provinces on English. This is a genuine, checkable-in-principle claim (real Chinese signage at
Jeju tourist sites is a verifiable fact, not invented), even though the specific 0-100 number
is still an unverified estimate.

## Findings

1. **The feature is architecturally isolated** — confirmed by code search, not assumed. It
   affects only what's displayed in the language panel, never what's heard.
2. **For the one language with a real anchor (English), a reasoned estimate following the
   prompt's own instructions preserves the real ranking** across all four reference provinces.
   That's evidence the prompt is well-constructed, not evidence the live model behaves this way
   — those are different claims, and only a real API call resolves the second one.
3. **For languages with no citable index, the prompt's demand — reason from real proxy
   signals, and say plainly that it's an estimate — is satisfiable** with real, checkable
   proxy facts (Vietnamese labor migration to industrial provinces, Chinese tourism to Jeju).
   The prompt doesn't ask for something ungroundable; it asks for exactly the kind of
   reasoning that's actually available for these cases.

## What this report does not establish

It does not confirm the actual Gemini model produces estimates like these — that's still
untested with a real key, same gap as `DEVELOPMENT_PLAN.md` Priority 5 already names for the
music predictor. It also doesn't validate the *feature's underlying premise* (that a 0-100
language-accessibility number is a meaningful, comparable construct across languages) — that
would need real visitor-experience data, which doesn't exist for this project any more than
the ISO soundscape field data does.

## Recommendation

Fold this into the same Priority 5 re-test as the music predictor: run both
`predictMusicStyleWithAI()` and `predictLanguageProficiencyWithAI()` with a real key on the
same 4 reference provinces used here, and check whether the live output's English ranking
still matches EF EPI's real order. If it doesn't, that's a concrete, specific finding — not
just "the feature is untested."
