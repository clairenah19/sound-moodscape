# Moodscape — Development Plan

Last updated: 2026-09-06

This is the single ordered view of what is done and what is next. It lives here, at the
repo root, on purpose — not scattered across `about.html`, and not duplicated into a second
file (the old `DEVELOPMENT_PLAN2.md` copy has been folded back into this one). Detailed
sourcing remains in `about.html` §06–§07, `out/Log.md`, and
`research/soundscape_relationship_validation_protocol.md`.

---

## Where the project stands

Three structural corrections have landed, in this order:

1. **2026-08-30 — scoring.** Hand-assigned Pleasantness/Eventfulness estimates were replaced
   by a reproducible Activity Proxy computed from official data for all 17 regions (density,
   tourism trips, noise complaints, noise-emitting facilities, crowding pressure), with
   Visitor Pleasantness kept as a separate score. Inputs are measured; weights are stated
   hypotheses. Documented in `out/Log.md`.
2. **2026-09-06 — accessibility.** The map itself became accessible rather than accessibility
   living behind a separate mode.
3. **2026-09-06 (same day, second pass) — Pleasantness went live, and the plan's own
   housekeeping got done.** Pleasantness now actually selects musical key/mode instead of
   sitting unused; every place score is labeled illustrative; the Priority 1 tooling that
   didn't need fieldwork got built; a real hidden gem was added per province; and the whole
   working tree got committed and pushed as two PRs instead of sitting unstaged.

The project is now *reproducible*, with one axis of its own ISO framing actually *sonified*
end to end. It is still not *validated*. Everything below is ordered by how much it closes
that remaining gap.

**Open PRs — merge these before anything else below:**
- [#1 — Add a real, sourced hidden gem per province](https://github.com/clairenah19/sound-moodscape/pull/1)
- [#2 — Reproducible scoring, accessible navigation, and plan follow-through](https://github.com/clairenah19/sound-moodscape/pull/2)

Both are open against `main` as of this update. #2's `data.js`/`ui.js` already include #1's
changes (they shared one uncommitted working tree before either was branched), so merge
either order — the second merge will just show as already-included, not conflicting.

---

## Priority 1 — Validation pilot

Still the single highest-leverage item: it's what moves the project from *reproducible* to
*tested*, and it has the longest lead time of anything on this list.

**Done, this pass:** the parts that didn't need fieldwork.
- `research/iso_pe_calculator.js` — the actual ISO 12913 Pleasantness/Eventfulness formula,
  plus site-time aggregation (mean, 95% CI) and scatter-plot data shaping. Math-checked
  against the protocol's formula; runs against clearly-labeled example data only.
- `research/soundwalk_questionnaire_ko.md` — Korean translation of the 8-item participant
  questionnaire, ready for a pilot. Still needs a real back-translation/pilot pass before
  being used as a validated instrument, per the protocol's own caveat.

**Still blocked on physical fieldwork** — cannot be automated:
- 6–10 sites across 1–2 provinces you can physically reach
- 2 time windows per site (weekday daytime, evening or weekend)
- ~5 independent ratings per site-time
- Record LAeq, pedestrians/min, vehicles/min, land use, lat/long, time, weather
- Enter into `research/soundwalk_observation_template.csv` (still empty), then run
  `research/iso_pe_calculator.js` against the real rows

**Decision rule (from the protocol, keep it):** if the contextual proxies do not improve
held-out prediction, say so in the writeup. A negative result reported honestly is a result.
With only two labelled provinces (Seoul, Daejeon), province-level regression is invalid — the
unit of analysis is the site-time observation.

## Priority 2 — Pleasantness has no live path

**Done.** `getMusicalKey()` now selects major/minor from the region's Visitor Pleasantness
*relative to the median across all 17 regions* (a fixed threshold doesn't work — pleasantness
sits in a narrow ~75–80 band everywhere), instead of the place's own activity-derived score.
Tempo, pitch, and timbre stay driven by activity. Verified: Gangnam (Seoul) now gets a minor
key because Seoul's Pleasantness sits below the national median — previously it was forced
major purely by its high activity score. The plain-language narrative and the "music,
without hearing it" panel both explain the real reason now, not a stale score-threshold line.

**Follow-up worth doing:** this has only been verified against the *narrative text* and the
accessible spec panel — not against an actual generated Suno track. Worth spot-checking that
a real generated MP3 for a flipped place (e.g. Gangnam) audibly sounds different in mode once
a Suno key is available to test with.

## Priority 3 — Landmark level is still illustrative

**Cheap fix done:** every place's mood ring shows an "Illustrative offset, not measured"
badge with a tooltip explaining why.

**Still open — the better fix:** measure a handful of real landmarks during the Priority 1
fieldwork so at least some places carry real data instead of an offset. This is the largest
remaining gap between what the app shows and what it can support: the most engaging layer of
the map (individual places) is still the least grounded.

## Priority 4 — Listener experiment

Untouched this pass. Tests Moodscape's own contribution rather than borrowed data: does the
generated music communicate the score it came from? Play 8–10 clips to ~15 listeners, have
them rate each on the same pleasant/eventful scales, correlate against the generating score.
Called for by the validation protocol's last line and by `about.html`'s "User study" roadmap
item — but unlike Priority 1, this one doesn't even have a written protocol yet. **Next
concrete step: write the listener-experiment protocol** (stimulus set, rating scale,
recruitment target, analysis plan) as its own file under `research/`, mirroring how the
soundwalk protocol is documented — that part doesn't need fieldwork either and could be
prepared now.

## Priority 5 — Finish what is live but incomplete

- **Gemini features never confirmed working.** AI music-style prediction and the
  language-proficiency estimate have never completed once with a real key. Still true — I
  don't have a Gemini key to test with. A feature that has never run end-to-end is a demo
  risk; test this before relying on it live in front of anyone.
- **`photos[]` gallery: 6 of 75 places populated (Seoul only).** Unchanged. A real, bounded
  piece of work — sourcing 2 free-licensed photos for the other 69 places, the same way
  Seoul's 6 were done.
- **Accessibility gaps** — see "Open, within accessibility" below, unchanged.

## Priority 6 — Writeup

Untouched, still stable to write now: `about.html` §§01–09 already maps onto a paper outline
(01 → research question, 02+08 → background, 03+05 → method, 04 → results, 06+07 →
limitations/future work). The missing piece is a real Results section, gated on Priority 1.

---

## Done

### 2026-09-06 — accessibility

- **Map is keyboard-navigable.** All 17 provinces are tab stops with `role="button"` and an
  `aria-label` carrying region name, modelled activity score, mood label, and whether a direct
  soundscape study backs it. Enter/Space opens. Place cards inside a province match. Focus
  indicator follows each province's own shape rather than a bounding box.
- **Screen readers are cooperated with, not competed against.** Announcements go through one
  small `aria-live="polite"` region — not the whole panel, which would re-read every control
  and API-key field on each click.
- **Navigation cue carries the data.** Focusing a province plays its own activity score as a
  pentatonic pitch, stretched across the observed score spread (~33–61), not the theoretical
  0–100 — mapping the full range collapsed all 17 regions onto 4 pitches, 9 of them identical.
- **Deaf and hard-of-hearing path.** Every place carries a "The music, without hearing it"
  panel — pitch/frequency, tempo pulse at the real BPM, key, timbre family, density,
  instrumentation — read from the same functions that drive the audio.
- **Untranslated text declares its own language** (`lang="en"` inside a `ko` document).
- **`prefers-reduced-motion` honoured** throughout.
- **Toggle renamed** from "♿ Accessibility Mode" to "🔊 Sound navigation" in all 13 languages.

### 2026-09-06 (second pass) — Pleasantness, illustrative labeling, hidden gems, housekeeping

- Pleasantness wired into `getMusicalKey()` (Priority 2, above).
- Illustrative-offset badge on every place (Priority 3 cheap fix, above).
- `research/iso_pe_calculator.js` and `research/soundwalk_questionnaire_ko.md` built
  (Priority 1 preparable-now items, above).
- One real, sourced hidden gem added per province — surfaced from an independent travel
  blog, not curated by the app, with the blog's own quote and a source link
  (`data.js`'s `hiddenGem`, `ui.js`'s `renderHiddenGem`).
- `about.html` §06 reconciled: "AI mood narrative generator" and "Open dataset" were listed
  as fully unbuilt but are each partly satisfied already.
- `README.md` written.
- The entire previously-unstaged working tree committed and pushed as two reviewable PRs
  (#1, #2) instead of sitting uncommitted.
- This file and `DEVELOPMENT_PLAN2.md` de-duplicated back into one file, per stored
  preference: the plan lives in `DEVELOPMENT_PLAN.md` at the repo root, not scattered.

### Open, within accessibility

- Stereo/spatial panning by longitude — iSonic (`about.html` §08) is the precedent.
- Directional movement (north/south/east/west from current position) instead of the fixed
  17-item list, so the guided tour teaches geography.
- Full stat readout in announcements — the official inputs behind the proxy, not just the score.
- **No testing with blind or low-vision users.** Everything above is an informed correction
  from standards and published practice, not from watching anyone use it. This is the item
  that matters most, and no amount of further code changes substitutes for it.

---

## Housekeeping

- **Merge #1 and #2.** Nothing above should get built on top of these branches until they're
  in `main` — new work should start from a clean, merged base.
- **Random files in the repo root should get sorted or removed**: `korea_provinces.docx`,
  `korea_provinces2.docx`, a screenshot PNG, and a UUID-named `.mp3` don't obviously belong
  in version control. Not touched in this pass since it wasn't clear which are still
  referenced — worth a deliberate look, not a silent delete.
- **No LICENSE file.** `README.md` now says so explicitly; add one if this is meant to be
  shared or reused by others (KSEF judges included).
