# Moodscape — Development Plan

Last updated: 2026-09-06

Single ordered view of what is done and what is next, at the repo root on purpose — not
scattered across `about.html`, not duplicated into a second file. Every task below has a
concrete deliverable (a file, a function, a specific number of items) and a way to check it's
actually finished, not just a direction. Detailed sourcing remains in `about.html` §06–§07,
`out/Log.md`, and `research/soundscape_relationship_validation_protocol.md`.

---

## Do this first

- [x] **Merge [PR #1](https://github.com/clairenah19/sound-moodscape/pull/1)** (hidden gems)
      and **[PR #2](https://github.com/clairenah19/sound-moodscape/pull/2)** (scoring +
      accessibility + Pleasantness) into `main`. Either order — #2 already contains #1's
      `data.js`/`ui.js` changes, so the second merge shows as already-included, not
      conflicting. Nothing below should branch off until this is done.

---

## Priority 0 (new) — Fix the synth-fallback claim

**Found while writing this update, not previously tracked.** `about.html` (§03) and
`audio/README.md` both state the app has "a built-in Web Audio synth fallback so the player
is never silent." It doesn't. Read `playCurrentSoundscape()` in `audio.js` end to end: if
there's no cached URL, no `window.SUNO_TRACKS` entry, no local MP3 in `audio/`, and no Suno
key saved, it sets a status string and stays silent. The only `createOscillator()` call in
the whole file is the two fixed UI beeps for accessibility navigation (880 Hz / 320 Hz) —
unrelated to any place's pitch/tempo/key. This is a documentation-vs-code mismatch a judge or
a live demo will find in minutes.

Two ways to close it — pick one, don't leave it open:

- [ ] **(Recommended) Build the real fallback.** Add a function to `audio.js`, e.g.
      `playSynthFallback(place, stateName)`, that:
      - reads `noteForScore(place.score)` (from `narrative.js`) for pitch,
      - reads `getSunoBpm(place)` for tempo,
      - reads `getMusicalKey(place, stateName)` for major/minor,
      - builds a simple loop with 2–3 `OscillatorNode`s (a root + a fifth, switched
        major/minor third) through a `GainNode` envelope, looped at the real BPM via
        `setInterval` or scheduled with `AudioContext.currentTime`,
      - is called from `playCurrentSoundscape()` as the last fallback, replacing the current
        "No real track found" message with actual sound.
      - **Done when:** opening any place with no MP3 and no Suno key, pressing ▶, produces
        audible sound whose pitch/tempo audibly changes between two places with very different
        scores (e.g. Gyeongbokgung vs. Hongdae).
- [x] **(Faster) Fix the documentation instead.** Change the §03 sentence and
      `audio/README.md` to say the player shows a status message and needs either a dropped
      MP3 or a Suno key — stop claiming a fallback that isn't there. Lower effort, but it's
      admitting a gap instead of closing one.

---

## Priority 1 — Validation pilot

Still the highest-leverage item for making the project *tested*, not just *reproducible*.

**Already built, this session** (nothing further needed unless the pilot data reveals a bug):
- `research/iso_pe_calculator.js` — `isoCoordinates()`, `aggregateSiteTime()`,
  `eventfulnessScatterData()`. Math-verified against the protocol's formula.
- `research/soundwalk_questionnaire_ko.md` — Korean 8-item questionnaire.

**Gap found while speccing this out, now closed:** the calculator had no code path that
reads an actual CSV — only the hand-written example in `runExample()`.

- [x] **`research/analyze_soundwalk.py`** — reads the observation CSV, groups rows by
      `site_name` + `date` + `start_time`, computes ISO Pleasantness/Eventfulness per
      participant, aggregates to site-time means with 95% CIs, and prints both a results
      table and the predictor-vs-Eventfulness scatter rows. Run it with
      `python3 research/analyze_soundwalk.py`; `--predictor` selects the x-axis column
      (default `laeq_db`), `--csv` points at another file.
      - Against the still-empty template it prints "0 rows found — no field data collected
        yet" and exits 0, so running it early does not look like a crash. Verified.
      - Rows with blank, non-numeric, or out-of-range ratings are skipped individually with
        a line number and the specific reason, rather than failing the whole run.
      - Small-cell 95% CIs use a t-interval, not the normal approximation: pilot cells are
        ~5–10 ratings, where 1.96 is too narrow.
      - **Written in Python, not the Node script this plan originally specified.** Every
        analysis script in `research/` is already Python, and Node is not installed on the
        development machine, so a Node script could not be run or verified.
        `iso_pe_calculator.js` is unchanged and still available for browser use; the ported
        math is checked against its documented worked example by `test_research.py`.
- [x] **Seven regression tests added** to `research/test_research.py` (`SoundwalkTests`):
      formula agreement with the protocol, neutral-maps-to-origin and extremes-reach-±1,
      out-of-range rejection, site-time (not site-only) grouping, distinct blank vs
      non-numeric skip reasons, t-interval width, and the clean empty-template exit.
- [x] **Observation template corrected against the protocol.** An audit of all 41 columns
      found `age_band` missing — a field the protocol's participant questionnaire explicitly
      requires — along with the required `land_use_category` predictor and four recommended
      ones (`fluctuation_strength_vacil`, `poi_types_in_buffer`, `sound_event_count`,
      `sound_event_diversity`). Template is now 47 columns and matches the protocol. Had this
      not been caught, the pilot would have collected data missing a required field, and no
      amount of later analysis could recover it.

**Everything printable is now prepared:**
- [x] **`research/field_pack.html`** — the print-ready paper pack. Page 1 is the recorder
      sheet (one per site-time: identity, time, weather, LAeq, counts, the recommended
      psychoacoustic fields); page 2 is the participant questionnaire (one per person).
      Open it and print at A4, 100%. Every one of the CSV's 47 columns has a slot on paper,
      verified programmatically, and each rating row is labelled with the exact column name
      it feeds — so transcription into the CSV is mechanical rather than a guess.
- [x] **`research/pilot_results.md`** — the write-up scaffold, currently `[PENDING]`. It
      already contains the protocol's decision rule quoted verbatim, the
      measured-vs-Activity-Proxy comparison table, and the limitations that are known in
      advance regardless of outcome (pilot sample size, unit of analysis, the questionnaire
      not being a validated instrument, convenience sampling, single observer).

**Fieldwork — the only remaining blocker. Cannot be automated:**
- [ ] Pick 1–2 physically reachable provinces and 6–10 sites covering: a commercial street, a
      residential street, a park/natural area, a transit area, and a market/heritage area.
- [ ] For each site, 2 time windows (weekday daytime + evening/weekend), ~5 independent
      participant ratings per site-time, using the printed field pack.
- [ ] Record simultaneously: LAeq (any calibrated/documented phone SPL meter app is fine per
      the protocol — write down which app), pedestrians/min, vehicles/min, lat/long,
      date/time, weather, land use.
- [ ] Enter every row into `research/soundwalk_observation_template.csv`.
- [ ] Run `python3 research/analyze_soundwalk.py` and fill in `research/pilot_results.md`,
      applying the protocol's decision rule explicitly: state in writing whether the
      official-data proxy actually predicted Eventfulness better than chance, even if the
      honest answer is no.

**Deliberately not built yet:** the protocol's analysis steps 4–9 — the mixed-effects model
with participant and site grouping, held-out-by-site validation, coefficients/RMSE/R², and
sensitivity analysis. Steps 1–3 (participant ISO coordinates, site-time means with CIs,
predictor scatter) are what a pilot of this size can actually support. The inferential layer
should be written against the real data's shape, not against imagined data.

## Priority 2 — Pleasantness → audio

- [x] Gangnam's current prompt requests a minor key using regional Pleasantness.
- [x] Added `research/live_feature_checks.html` for actual API calls and a separate human listening record.
- [x] **Generate a real Gangnam track and check the mode. No longer blocked — done on
      2026-09-13 (`6bc9ded`) with the user's own key.** The answer is negative and is
      recorded in `research/pleasantness_to_audio_analysis.md`: Gangnam requested **minor**
      and came back **A# major** at 0.921 detection confidence. Tempo in the same clip was
      near-perfect (115 requested, 114.8 detected, 0.2% error), so the prompt was not ignored
      wholesale — the tempo instruction survived and the mode instruction did not. Across all
      ten generated tracks the major/minor match rate is 5/10.
- [x] **Quantified how far Pleasantness actually reaches** (same analysis file). It is
      attenuated three times before anything is audible:
      1. `getMusicalKey()` checks two hard-coded category overrides first, so Pleasantness
         decides the key for only **34 of 75 places (45%)** — 6 are solemn overrides, 35 are
         nature/traditional overrides.
      2. It reads a *regional* value, so all default-branch places in a region share one key.
         That is **17 decisions, not 75**.
      3. `PLEASANTNESS_MEDIAN` is the median of the 17 regions themselves, so **~half get
         minor by construction** regardless of absolute pleasantness. The 17 values span only
         75.05–81.74, and Gyeongsangbuk-do sits *exactly* on the median — major only because
         the comparison is `>=`. Three more regions are within 0.6 of the line.
      End to end: 45% × ~50% ≈ **23%** of places have a Pleasantness-derived key that is
      actually audible. **Pleasantness is wired to the prompt, not reliably to the audio.**
- [x] **Decide what to do about it.** Chose the conservative wording-only option: `README.md`,
      `about.html`, and `research/paper_draft.md` now distinguish requested parameters from
      measured audio and state the observed 5/10 mode match. The scoring rule is unchanged.
      Four options and their trade-offs remain documented at the end
      of `research/pleasantness_to_audio_analysis.md`: correct the wording only; replace the
      median split with an absolute or spread-aware threshold; move Pleasantness onto a
      parameter Suno honours more reliably; or wait for `research/prompt_ablation_experiment.py`,
      which is already testing why the mode request gets dropped.

## Priority 3 — Landmark-level data

- [x] `research/fetch_landmark_pageviews.py` retrieves Wikimedia REST pageviews and writes CSV/JSON for all 75 places, including explicit missing-data rows.
- [x] Actual 2025-09 through 2026-08 pull: 58 complete, one partial, 16 with no linked Wikipedia article.
- [x] Documented log1p min–max 0–100 popularity offset in `research/landmark_pageviews_method.md`; it is not a soundscape measurement.
- [x] Detail panel shows popularity evidence alongside the existing illustrative score and offset; scoring and audio mappings are unchanged.
- [ ] Measure 3–5 real landmarks during Priority 1 fieldwork. Defaults are `measured: false`; set true only with linked actual observations.

## Priority 4 — Listener experiment

- [x] `research/listener_experiment_protocol.md`: ten places across the observed score range, blinded randomized clips, eight adjective ratings, consent/recruitment, target 24 adults (minimum 15 complete sessions for exploratory analysis).
- [x] Static `research/listener_rating_form.html`: resume, playback-coverage checks, validated ratings, CSV export and delete. Collection stays disabled until ten genuine clips are prepared and hashed.
- [x] `research/prepare_listener_clips.py` prepares reviewed real tracks; `research/analyze_listener_experiment.py` implements clip-level Spearman with permutation test and participant bootstrap intervals, plus (added 2026-09-20) pairwise ordering accuracy, Lin's CCC, normalised WAPE/MAE, ICC and Kendall's W.
- [ ] Generate/review clips, recruit consenting listeners, collect real responses, and run the analysis. `research/listener_experiment_results.md` remains `[PENDING]`; synthetic software checks are not participant data.

## Priority 5 — Finish what is incomplete

- [x] Prepared live checks for Ask a Local, music-style JSON, and two non-English language estimates; status recorded in `research/live_feature_checks.md`.
- [ ] All three Gemini features still need actual key-backed checks. Current status is **blocked / not tested**, not pass or fail.
- [x] Added two sourced, visually reviewed photos for each of the remaining 69 places. All 75 places now have `photos[]` with two entries; sources are in `research/landmark_photo_sources.csv`.
- [x] Replaced the seven publisher-owned images with visually reviewed Wikimedia Commons
      images carrying CC or public-domain metadata. Where exact reusable photos of a private
      industrial site were unavailable, captions explicitly say the image is manufacturing or
      regional context and not the named campus/plant. All 138 additions are now reusable.
- [x] Prepared `research/accessibility_tester_brief.md`.
- [ ] **Future work, outside the current evaluation scope:** recruit blind/low-vision testers if participation becomes feasible. The user now expects this participation is unlikely. No outreach has been sent; completion of the current project does not depend on this recruitment.
- [x] Added full regional input/stat summaries to map `aria-label`s, east/west stereo panning
      to score-pitched navigation cues, and geographic N/S/E/W arrow-key movement based on
      projected region centroids. These are technically implemented but remain unvalidated
      with intended users; implementation does not establish usability for blind/low-vision people.

## Priority 6 — Writeup

- [x] `research/paper_draft.md` maps about §01 into Abstract/Introduction, §02/08 into Related Work, §03/05 into Method, and §06/07 into Limitations/Future Work.
- [ ] Results remain `[PENDING]` until Priority 1 produces real observations and analysis. The listener study is also pending.

Verification and reproducible commands: `research/IMPLEMENTATION_REPORT_2026-09-13.md`.

---

## Suno / Gemini code-side improvements (added 2026-09-20)

Found by reading `prompt.js`, `audio.js`, `ui.js` against the measured audio results
(`research/AUDIO_VERIFICATION_REPORT_EN.md`, `research/prompt_ablation_results.csv`). None need
anything from Suno or Google.

**Done, checked in the browser with a mocked `fetch` (no credits, no real keys):**
- [x] **Keys no longer pass through a public proxy.** Suno's Bearer key and Gemini's `?key=` URL
      used to go through `corsproxy.io`. Both APIs answer CORS preflights (localhost and the
      `null` origin of `file://`), so calls are direct. Gemini's key is now an `x-goog-api-key`
      header, never in the URL. A user-owned proxy is still possible via `cfg.proxy`.
- [x] **Live generation uses the prompt the panel shows** (`sunoGenerate(..., promptOverride)`), so
      the AI-predicted prompt is no longer silently replaced by the rule-based one.
- [x] **Only a finished track is returned.** `streamAudioUrl` (possibly a partial stream) is used
      only after status `SUCCESS` with no finished `audioUrl`.

**Still open (need a decision or a test):**
- [x] Made style words agree with the key at prompt construction time. Minor-mode styles drop
      explicitly bright/happy wording and receive a minor-color direction; major-mode styles
      receive a major-color direction. Whether Suno follows it remains a real-audio question.
- [x] Constrained the AI predictor: the model receives the app's fixed key and BPM, no longer
      invents a `tempo_feel` or mode, and predictions are cached per place/mapping version.
- [x] Decided not to offer both generated tracks. The player remains a single-track control and
      deliberately takes the provider's first finished result; exposing alternates would require
      selection, caching, download, and accessibility UI for a feature not central to the study.
- [ ] Slow requests (42-81 BPM) measured 122-161 BPM. Diagnose by ear before changing code.
- [x] Stated the measured 50% mode match and tempo caveats in `about.html` section 03.
- [x] Re-verified `gemini-3.5-flash-lite` on 2026-09-20 against Google's official model and
      deprecation pages: it is a stable multimodal model with no announced shutdown date.

---

## Housekeeping

- [x] **Repo-root file cleanup** — specific recommendation per file, not a vague "tidy up":
      - `korea_provinces.docx`, `korea_provinces2.docx` (12KB/11KB, dated Jul 12 — predate
        the CSV research pipeline) — not referenced anywhere in code or docs (checked). Move
        to `research/archive/` if they contain notes worth keeping, otherwise delete.
      - `NTQzNjhmOWUtYjk5MS00Yjc0LWI3N2UtZGRjYzcxNzEwZGJi.mp3` (5.1MB, UUID filename, dated
        Jul 26, same size as `Gyeongido samsung.mp3` at repo root — looks like a duplicate
        cached Suno download) — not referenced by filename anywhere in code. Delete, or if
        it's actually a wanted track, rename to the `<state-slug>__<place-slug>.mp3`
        convention in `audio/README.md` and move it into `audio/`.
      - `piano-anatomy/` — an unrelated project living inside this repo. Move it to its own
        repo/folder outside `sound-moodscape` entirely.
- [x] **Add `.claude/` to `.gitignore`** — currently untracked but not ignored, so it'll keep
      showing up in `git status` as noise.
- [x] **Add a `LICENSE` file.** Two reasonable options given Wikimedia CC-BY-SA/CC-BY photo
      credits are already carried per-image in the app: MIT for the code (keeps photo
      attribution as-is, most permissive for a KSEF project judges might want to try
      running), or CC-BY-NC-SA 4.0 if non-commercial use should be required. MIT was selected
      for the code; third-party image terms remain attached to each image.
