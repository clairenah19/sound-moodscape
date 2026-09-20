# Moodscape — Rule-Based Prompt vs. AI-Predicted Prompt: Comparison Report

> **Historical comparison (superseded 2026-09-20).** This report describes the earlier
> predictor, which asked Gemini to choose tempo and mode independently. The live pipeline now
> keeps the score-derived BPM, pitch centre, mode, and vocal treatment fixed, and asks Gemini
> only for photo-grounded genre, instrumentation, mood, and arrangement. Those locked values
> are then sent to Suno in custom mode. The observations below remain useful evidence for why
> that contract was changed, but they no longer describe the current request shape.

## Purpose

At the time of this comparison, Moodscape had two separate ways of deciding what a place's
music should sound like:

1. **The rule-based path** (`prompt.js`): `getSunoBpm()`, `getMusicalKey()`, `getSunoStyle()`,
   `getVocalDirective()` — deterministic keyword/threshold rules, feeding `buildSunoPrompt()`.
2. **The AI-predicted path** (`prompt.js`, `predictMusicStyleWithAI()`): sends Gemini the
   place's text data **and its real photo**, asking it to predict genre/instrumentation/
   tempo/key/mood from scratch — feeding `buildSunoPromptFromAIPrediction()`.

This report checks how similar these two paths actually are, for 5 places chosen to span
different score bands and categories (urban/youth, palace, memorial, beach, industrial).

## Methodology and an important limitation, stated up front

**No Gemini API key was available for this report, so no live call to `predictMusicStyleWithAI()`
was made.** What follows for "the AI prediction" is **not a real Gemini output** — it's a
prediction produced by directly following that function's exact system prompt and JSON
schema, using the same inputs Gemini would get: the place's real text data, **and its actual
photo, downloaded and viewed for this report** (not guessed from the filename or the text
alone — the same multimodal grounding the real feature uses). This is the closest verifiable
substitute available without a key, but it should be read as **"what a careful reading of the
same prompt+photo produces," not "what Gemini said."** Re-running this with a real key (tracked
in `DEVELOPMENT_PLAN.md` Priority 5) is the only way to confirm whether the actual model agrees
with this approximation.

The rule-based side, by contrast, is **not an approximation** — every value below was traced
directly through the real functions in `prompt.js`/`data.js` as they exist right now.

## Per-place comparison

### 1. Hongdae (Seoul, score 0.94, "Youth & arts district")

**Photo observed:** an overcast, lightly rainy daytime street — moderate foot traffic in
casual clothes, several people carrying umbrellas, shop signage, muted grey sky. Notably
**not** the "packed midnight nightlife" scene the place's `character` text describes.

| | Rule-based (`buildSunoPrompt`) | AI-predicted (photo-grounded) |
|---|---|---|
| Key | **Minor** — no traditional/nature override applies; falls to default, which reads Seoul's Visitor Pleasantness (75.8) against the 17-region median (77.7) — below it, so minor | **Major** — the actual photo reads as a mellow, cozy daytime stroll, not a somber scene; nothing in the visible mood supports minor |
| Genre | "energetic K-indie rock, electric guitar riffs, lively drums, youthful band vibe, upbeat" | "chill K-indie / city pop, unhurried" |
| Tempo | 145 BPM (from `score×110+42`) | "unhurried, mid-tempo" |
| Mood | (implicit in genre) | "cozy, drizzly, unhurried, youthful, low-key" |

**Verdict: MISMATCH.** This is the one real divergence in the sample, and it's mechanically
explained: the rule-based key comes from Seoul's *regional* Pleasantness survey number, which
has no way to know this specific photo shows a quiet rainy afternoon rather than a packed
night. The AI path, grounded in the actual image, would have no reason to output minor here.
This is a direct, concrete illustration of the gap `DEVELOPMENT_PLAN.md` Priority 3 already
names: place-level output riding on a region-level number.

### 2. Gyeongbokgung Palace (Seoul, score 0.22, "Historic royal palace")

**Photo observed:** bright, clear blue sky, sunny midday — not the "dawn" the character text
claims. Grand, orderly, monumental palace roofs against green mountains, visible but modest
crowd.

| | Rule-based | AI-predicted (photo-grounded) |
|---|---|---|
| Key | **Major** — hardcoded override, `type.includes("palace")` | **Major** |
| Genre | "serene traditional Korean meditation music, peaceful daegeum flute and gayageum pluck" | "serene traditional Korean court music" |
| Tempo | 66 BPM | "slow, spacious" |
| Mood | (implicit) | "grand, majestic, orderly, sunlit, monumental" |

**Verdict: MATCH.** Both land on major, both land on traditional/serene. Worth noting as an
aside, not a mismatch: the photo is sunlit midday, not dawn — the *character text* (which both
paths read) already contains that inaccuracy; it isn't something either music-prediction path
introduced.

### 3. 5.18 National Cemetery (Gwangju, score 0.08, "Democracy memorial cemetery")

**Photo observed:** a large white ceremonial canopy/monument, overcast sky, small groups of
ordinary visitors.

| | Rule-based | AI-predicted (photo-grounded) |
|---|---|---|
| Key | **Minor** — hardcoded override, `name.includes("5.18")` | **Minor** |
| Genre | "solemn cinematic ambient, deep emotional orchestral drone, moving cello, respectful, quiet" | "solemn ambient orchestral" |
| Tempo | 51 BPM | "slow, spacious" |
| Mood | (implicit) | "solemn, respectful, overcast, monumental, quiet" |

**Verdict: MATCH.** Strong agreement — the hardcoded memorial override and a direct photo
read arrive at essentially the same place independently.

### 4. Haeundae Beach (Busan, score 0.8, "Beach & resort strip")

**Photo observed:** bright sunny day, golden sand, turquoise water, sunbathers and beach
umbrellas, a dramatic skyline of very tall glass towers behind.

| | Rule-based | AI-predicted (photo-grounded) |
|---|---|---|
| Key | **Major** — hardcoded override, `type.includes("beach")` | **Major** |
| Genre | "tropical house, sun-drenched coastal synth groove, warm summer beach vibe, uplifting" | "bright tropical house / summer pop" |
| Tempo | 130 BPM | "upbeat, driving" |
| Mood | (implicit) | "sun-drenched, glamorous, energetic, coastal, vibrant" |

**Verdict: MATCH — the strongest agreement in the sample.** The photo visually confirms the
character text almost exactly, so both paths converge tightly.

### 5. POSCO Pohang Steelworks (Gyeongsangbuk-do, score 0.7, "Integrated steelworks")

**Photo observed:** a vast waterfront industrial panorama, blast-furnace towers, clean bright
blue sky — monumental and orderly, not grimy or dark.

| | Rule-based | AI-predicted (photo-grounded) |
|---|---|---|
| Key | **Major** — falls to default; Gyeongsangbuk-do's Pleasantness (77.7) sits exactly *at* the 17-region median, and the code's `>=` comparison resolves ties to major | **Major** — the bright, clean, monumental visual supports major over minor |
| Genre | "futuristic progressive electronic, clean high-tech synth layers, driving modular rhythm, sleek" | "modern industrial ambient / cinematic tech" |
| Tempo | 119 BPM | "steady, driving but controlled" |
| Mood | (implicit) | "monumental, industrial-clean, vast, humming, bright" |

**Verdict: MATCH on key, partial on genre.** Both land on major and on an
electronic/industrial-coded palette, but "futuristic progressive electronic" (rule) and
"industrial ambient/cinematic" (photo-grounded) aren't the same genre — related family,
different specific style. Worth flagging separately: Gyeongsangbuk-do's Pleasantness landing
*exactly* on the national median is a coincidence of this particular dataset, not a designed
tie-break — the `>=` in `getMusicalKey()` is what silently decides it, and that's worth a code
comment if it isn't already documented (checked: it isn't).

## Summary

| Place | Key match | Genre overlap | Overall |
|---|---|---|---|
| Hongdae | ✗ | Medium (same family, opposite energy) | **Mismatch** |
| Gyeongbokgung Palace | ✓ | High | Match |
| 5.18 National Cemetery | ✓ | High | Match |
| Haeundae Beach | ✓ | High | Match |
| POSCO Pohang Steelworks | ✓ | Medium-High | Mostly match |

**4 of 5 places agree on musical key; genre wording is never identical but stays in the same
family in every case except Hongdae.** The one real mismatch has a clear, traceable cause: the
rule-based path's default key comes from a *region-wide* survey number, with no way to see
what a specific place's photo actually shows, while a photo-grounded prediction naturally
picks up on the actual scene. This isn't a bug exactly — it's the fundamental limitation of
using a region-level Pleasantness proxy for a place-level decision, already tracked as a gap
in `DEVELOPMENT_PLAN.md` Priority 3 — but this report is the first place it's been shown
concretely, with a real photo, rather than described abstractly.

## Recommendation

- Re-run this exact comparison with a real Gemini key once available (`DEVELOPMENT_PLAN.md`
  Priority 5's "confirm Gemini features actually complete" item) to see whether the live model
  agrees with this report's photo-grounded approximation, especially for Hongdae.
- If the mismatch pattern holds — hardcoded-category places agree, default-case places don't —
  that's evidence the fix belongs in Priority 3 (a real per-place signal) rather than in the
  key-selection formula itself, since the formula behaves exactly as designed; it just has no
  place-level information to work with in the default case.
