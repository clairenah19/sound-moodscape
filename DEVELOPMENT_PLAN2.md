# Moodscape — Development Plan

Last updated: 2026-09-06

Consolidated from `about.html` §06–§07, `out/Log.md` §8, `SESSION_REPORT_2026-08-16.md`,
and `research/soundscape_relationship_validation_protocol.md`. Those remain the detailed
sources; this file is the single ordered view of what is done and what is next.

---

## Where the project stands

Two structural corrections have landed, in this order:

1. **2026-08-30 — scoring.** Hand-assigned Pleasantness/Eventfulness estimates were replaced
   by a reproducible Activity Proxy computed from official data for all 17 regions (density,
   tourism trips, noise complaints, noise-emitting facilities, crowding pressure), with
   Visitor Pleasantness kept as a separate score. Inputs are measured; weights are stated
   hypotheses. Documented in `out/Log.md`.
2. **2026-09-06 — accessibility.** The map itself became accessible rather than accessibility
   living behind a separate mode. Details in "Done" below.

The project is now *reproducible*. It is not yet *validated*. Everything below is ordered by
how much it closes that gap.

---

## Priority 1 — Validation pilot

The protocol exists (`research/soundscape_relationship_validation_protocol.md`); no data has
been collected against it. This is the one thing that moves the project from "reproducible
model" to "tested model", and it has the longest lead time, so it starts first.

Scoped to what is actually reachable — the protocol's full 30-site design is not required for
a defensible pilot:

- 6–10 sites across 1–2 provinces you can physically reach
- 2 time windows per site (weekday daytime, evening or weekend)
- ~5 independent ratings per site-time
- Record LAeq, pedestrians/min, vehicles/min, land use, lat/long, time, weather
- Use `research/soundwalk_observation_template.csv` for entry

Analysis: participant-level ISO Pleasantness and Eventfulness, site-time means with 95% CIs,
every predictor plotted against Eventfulness before any model is fitted.

**Decision rule (from the protocol, keep it):** if the contextual proxies do not improve
held-out prediction, say so in the writeup. A negative result reported honestly is a result.
With only two labelled provinces, province-level regression is invalid — the unit of analysis
is the site-time observation.

**Blocked on:** physical fieldwork. Cannot be automated.
**Preparable now:** the ISO P/E calculation, the scatter plots, and the Korean participant
questionnaire can all be built before any rows exist.

## Priority 2 — Pleasantness has no live path

`out/Log.md` §4 states Visitor Pleasantness "does not currently control the audio". The whole
ISO 12913 framing is two-axis; the app sonifies one. Either:

- wire Pleasantness to a distinct audio parameter — key/mode is its natural home, leaving
  tempo and density to activity — or
- state plainly on the site that only one axis is sonified.

Right now the framing promises two axes and delivers one.

## Priority 3 — Landmark level is still illustrative

75 places carry illustrative offsets because no landmark-level measurements exist. This is the
largest remaining gap between what the app shows and what it can support: the most engaging
layer of the map is the least grounded.

- Cheap and honest: label the offsets as illustrative in the UI.
- Better: measure a handful of landmarks during the Priority 1 fieldwork so some places have
  real data.

## Priority 4 — Listener experiment

Tests Moodscape's own contribution rather than borrowed data: does the generated music
communicate the score it came from? Play 8–10 clips to ~15 listeners, have them rate each on
the same pleasant/eventful scales, correlate against the generating score. Already called for
by the protocol's last line and by §06's "User study" roadmap item.

## Priority 5 — Finish what is live but incomplete

- **Gemini features never confirmed working.** AI music-style prediction and the
  language-proficiency estimate have never completed once with a real key. A feature that has
  never run is a demo risk — do these first, they are quick.
- **`photos[]` gallery**: 6 of 75 places populated (Seoul only).
- **Accessibility gaps** carried forward — see "Open" under Done below.

## Priority 6 — Writeup

`about.html` §§01–09 already maps closely onto a paper outline: 01 → research question,
02 + 08 → background and related work, 03 + 05 → method, 04 → results, 06 + 07 → limitations
and future work. What is missing is a Results section with real numbers, which Priority 1
gates. Write method and background now — they are stable.

---

## Done

### 2026-09-06 — accessibility

- **Map is keyboard-navigable.** All 17 provinces are tab stops with `role="button"` and an
  `aria-label` carrying region name, modelled activity score, mood label, and whether a direct
  soundscape study backs it. Enter/Space opens. Place cards inside a province match. Focus
  indicator follows each province's own shape rather than a bounding box.
- **Screen readers are cooperated with, not competed against.** The previous design spoke
  through the Web Speech API and captured arrow keys globally, both of which fight a real
  screen reader. Announcements now go through one small `aria-live="polite"` region — not the
  whole panel, which would re-read every control and API-key field on each click.
- **Navigation cue carries the data.** Focusing a province plays its own activity score as a
  pentatonic pitch. The mapping is stretched across the observed score spread (~33–61), not
  the theoretical 0–100: mapping the full range collapsed all 17 regions onto 4 pitches, 9 of
  them identical. This normalization is a design choice and needs documenting in the writeup.
- **Deaf and hard-of-hearing path.** Every place carries a "The music, without hearing it"
  panel — pitch and frequency, tempo with a pulse at the real BPM, key, timbre family,
  density, instrumentation — read from the same functions that drive the audio.
- **Untranslated text declares its own language** (`lang="en"` inside a `ko` document), so a
  Korean voice does not read English words aloud.
- **`prefers-reduced-motion` honoured** — the tempo pulse, waveform, and the guided tour's
  previously-endless pulsing ring all stop.
- **Toggle renamed** from "♿ Accessibility Mode" to "🔊 Sound navigation" in all 13 languages,
  with `aria-pressed`. The wheelchair symbol denotes mobility access and is read aloud as
  "wheelchair symbol"; this feature serves blind and low-vision users.

### Open, within accessibility

- Stereo/spatial panning by longitude — iSonic (§08) is the precedent.
- Directional movement (north/south/east/west from current position) instead of the fixed
  17-item list, so the guided tour teaches geography.
- Full stat readout in announcements — the official inputs behind the proxy, not just the score.
- **No testing with blind or low-vision users.** Everything above is an informed correction
  from standards and published practice, not from watching anyone use it. This is the item
  that matters most.

---

## Housekeeping

- **Working tree is uncommitted.** The 2026-08-30 scoring reform, `i18n.js`, the new research
  CSVs, `out/Log.md`, and today's accessibility work are all unstaged. Commit before anything
  else.
- **`about.html` §06 has stale entries.** "AI mood narrative generator" is listed as not built,
  but `narrative.js` ships a deterministic version of it; "Open dataset" is largely satisfied by
  the CSVs in `research/`. Reconcile the roadmap with what actually exists.
