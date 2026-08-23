# Moodscape — Session Report, 2026-08-16

A record of today's work, grounded in actual git commits and file diffs rather than memory —
this project spans multiple real work sessions (Jul 26, Aug 9, and today), and this report
covers only what actually happened today to avoid conflating separate days' work.

## Summary

Today added five things: a full generalization of the mood formula's language-accessibility
term (from English-only to any of 12 languages, AI-estimated live), a plain-language "why does
it sound like this" narrative generated for every province and place, a second real photo per
place, a corrected and widened BPM range plus context-aware vocal handling in the Suno prompts,
and a multimodal AI music-style predictor. Two of these shipped as commits; the rest were found
sitting complete but uncommitted in the working tree while preparing this report, and were
committed as part of writing it.

## 1. Language accessibility — generalized from English-only

The mood formula's second term was hard-coded to English proficiency (EF EPI), quietly assuming
every listener is or wants to be understood in English. It's now a listener-selectable
**Language proficiency** term: a dropdown (English plus Mandarin, Japanese, Spanish, French,
German, Vietnamese, Russian, Arabic, Hindi, Portuguese, Thai) in both the site header and each
province's panel, with the province's accessibility score for the *chosen* language estimated
live via Gemini — the same bring-your-own-key mechanism already used by "Ask a Local" and the AI
music predictor, so no new key is needed if one is already saved.

English is the only language with a real citable index (EF EPI) behind it; the model is told to
anchor on that real number when English is selected. Every other language gets an explicitly
labeled reasoned estimate built from proxy signals (tourism volume, expat communities, signage
prevalence) — same estimate-what's-uncited-rather-than-invent-it discipline used throughout this
project's research. Results are cached per province/language pair in `localStorage` so they
aren't re-queried on every visit.

`about.html` §03 was corrected to match: the formula term is now labeled "Language proficiency,"
and the weighting-rationale prose was updated to explain this generalization rather than
describe English as a fixed input.

## 2. Vibe Narrative — plain-language "why does it sound like this"

New file: `narrative.js`. For every province and every place, a paragraph is generated
instantly from data already on the page — no API key, unlike the Gemini-backed features — that
explains the data→music link explicitly: what real-world category the place falls into, what
mood score that earns it, what note/BPM/key/timbre that score becomes, and *why* the key landed
where it did. The goal is making the sonification legible rather than a black box: a listener
can now read exactly why a place sounds the way it does instead of just hearing it.

Deterministic phrasing variation (seeded by place name, not random) means the same place always
reads the same way on repeat visits, while different places get different opening phrasing.

## 3. Second real photo per place

`data.js` places now carry an optional `photos: [...]` array (two additional real, attributed
Wikimedia Commons photos per place, on top of the existing primary photo), rendered as a small
gallery in the UI (`.real-photo-gallery` in `style.css`) with the same artist/license/source-link
attribution pattern as the primary photo. **Confirmed only 6 of 75 places have it — Seoul's six
— so this is a first pass, not a completed feature.** The other 69 places fall back to the
single-photo layout, which still works correctly since the UI checks for the array's presence.

## 4. BPM range widened + context-aware vocals

Two corrections to `buildSunoPrompt()`:

- **BPM range widened from 40–120 to 42–152.** The original ceiling meant even Hongdae — the
  single highest-scoring place across all 75 — only reached ~115 BPM, well below real K-indie/
  dance-pop energy (120–150+), so the "most energetic" place in the app could never actually
  sound fast. The calm end stays about the same (~42 BPM).
- **Context-aware vocal directive.** Previously every prompt ended in a blanket "no vocals, no
  lyrics." A few places' own instrumentation text contradicts that — pansori is inherently sung,
  monk chant is vocal, Hongdae's character is literally "buskers" — so those now get a wordless-
  vocal directive instead (e.g. "wordless pansori-style vocal cries, no full lyrics"), keeping
  the human voice as texture without introducing unrelated lyrics. Everywhere else stays fully
  instrumental. `suno-prompts.md` was regenerated from the live code to match.

## 5. AI music-style prediction (multimodal Gemini)

**Commit [`2879389`](https://github.com/clairenah19/sound-moodscape/commit/2879389)** — *Add
AI music-style prediction (Gemini, multimodal)*

A **"🤖 Let AI predict the best music style"** button per place. Sends Gemini both the place's
real research data (character, type, instrumentation tags, mood score) and its actual Wikimedia
photo as inline base64 image data — genuinely multimodal, not text-only — and gets back
structured JSON (genre, instrumentation, tempo feel, key, mood descriptors, reasoning) via a
`responseSchema`, which rewrites the Suno prompt live. Reuses the existing Gemini key; purely
additive if none is set.

**Verified:** JS parses cleanly; the multimodal request shape was checked against the real
Gemini endpoint with a dummy key — `400 API key not valid` rather than a request-format error,
ruling out a malformed request. An actual successful prediction with a real key hasn't been
confirmed yet.

## 6. `about.html` — formula documentation and honest gap-tracking

**Commit [`e1a8dd9`](https://github.com/clairenah19/sound-moodscape/commit/e1a8dd9)** plus
today's further edits:

- **"Why this weighting"** section explaining the 30/25/25/20 formula weights as a stated design
  judgment, not a derived result — Safety leads because it can flip a place's whole character;
  Language proficiency and Density are matched deliberately; Temperature is weighted lowest
  because it has the narrowest real spread across provinces.
- **Density term correction.** An earlier version of the doc labeled the density term "inverse"
  — backwards. Seoul has both the highest density *and* the highest mood score; Jeju has the
  lowest of both. Density scales the score *up*, not down. Fixed in the formula and its prose.
- **Research pipeline & process section** — the six-stage methodology (literature search →
  framework selection → parallel data compilation → fusion → narrative synthesis → service
  integration) from the Aug 9 process report, now documented on the live site, plus its headline
  findings (2 of 17 regions have a direct soundscape study; 15 of 17 emotional scores are
  estimates; ~3× speedup from parallelizing the research).
- **New "Improvements needed" section** for the Accessibility Mode specifically — tracked
  separately from the roadmap because it's a feature that's *live* but incomplete, not one that
  doesn't exist yet. Documents plainly what's real (keyboard navigation across all 17 provinces
  with audio ticks and spoken narration via Web Speech API) versus what the original design
  intent still lacks (no stereo/spatial panning, the navigation tick isn't the place's actual
  mapped pitch, spoken narration omits the underlying sourced stats, and it hasn't been tested
  with blind or low-vision users yet).

## 7. Data exports — full research dataset as CSV

- **`research/moodscape_region_data.csv`** — 17 rows (one per region): Pleasantness/Eventfulness
  scores, sourcing status, citation basis, cultural-character summary.
- **`research/moodscape_places_data.csv`** — 75 rows (one per place): region, mood score, type,
  instrumentation, a newly-written 2–3 sentence expanded narrative per place, and photo/Maps
  attribution.

Both verified by parsing back with Python's `csv` module before delivery.

## What's still open

- AI music-style prediction needs a live test with a real Gemini key.
- Language-proficiency estimates likewise haven't been tested live end-to-end.
- The `photos[]` gallery is only populated for Seoul's 6 places — 69 of 75 still need it.
- The mood-score formula, including today's corrections and weighting rationale, still isn't
  computed live — scores remain hand-assigned, a gap the app's own "Research status" notice
  already discloses.
- Accessibility Mode's own documented gaps (stereo panning, real pitch preview, full stat
  readout, user testing) remain open per the new "Improvements needed" section.

## Repository state at end of day

```
[today]   Report + uncommitted feature work from today, committed together
e1a8dd9   Explain the design judgment behind the mood-score formula weights      2026-08-16 12:48
2879389   Add AI music-style prediction (Gemini, multimodal)                     2026-08-16 12:03
ba32b2b   Update region taglines with research-backed facts from fused report    2026-08-09 13:19
b169276   Fix review findings: duplicate photos, GeoJSON payload, BYOK clarity   2026-08-09 13:04
6915ba1   Fix Ask a Local: migrate dead gemini-1.5-flash to gemini-3.5-flash-lite 2026-08-09 11:52
```

Live site: https://clairenah19.github.io/sound-moodscape/
