# Moodscape — Development Plan

Last updated: 2026-09-06

Single ordered view of what is done and what is next, at the repo root on purpose — not
scattered across `about.html`, not duplicated into a second file. Every task below has a
concrete deliverable (a file, a function, a specific number of items) and a way to check it's
actually finished, not just a direction. Detailed sourcing remains in `about.html` §06–§07,
`out/Log.md`, and `research/soundscape_relationship_validation_protocol.md`.

---

## Do this first

- [ ] **Merge [PR #1](https://github.com/clairenah19/sound-moodscape/pull/1)** (hidden gems)
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
- [ ] **(Faster) Fix the documentation instead.** Change the §03 sentence and
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

**Fieldwork (cannot be automated) — do this after the script above exists:**
- [ ] Pick 1–2 physically reachable provinces and 6–10 sites covering: a commercial street, a
      residential street, a park/natural area, a transit area, and a market/heritage area.
- [ ] For each site, 2 time windows (weekday daytime + evening/weekend), ~5 independent
      participant ratings per site-time, using the printed Korean questionnaire.
- [ ] Record simultaneously: LAeq (any calibrated/documented phone SPL meter app is fine per
      the protocol), pedestrians/min, vehicles/min, lat/long, date/time, weather, land use.
- [ ] Enter every row into `research/soundwalk_observation_template.csv`.
- [ ] Run `node research/analyze_soundwalk.js` and paste the output table into a new
      `research/pilot_results.md`, with the protocol's decision rule applied explicitly:
      state in writing whether the official-data proxy actually predicted Eventfulness better
      than chance, even if the honest answer is no.

## Priority 2 — Pleasantness → audio

- [x] Gangnam's current prompt requests a minor key using regional Pleasantness.
- [x] Added `research/live_feature_checks.html` for actual API calls and a separate human listening record.
- [ ] Generate a real Gangnam Suno track and confirm it audibly resolves in minor. **Blocked:** no usable key was accessible in the inspected environment; browser-stored keys need the original origin/profile. A minor-key prompt is not proof of minor-key audio.

## Priority 3 — Landmark-level data

- [x] `research/fetch_landmark_pageviews.py` retrieves Wikimedia REST pageviews and writes CSV/JSON for all 75 places, including explicit missing-data rows.
- [x] Actual 2025-09 through 2026-08 pull: 58 complete, one partial, 16 with no linked Wikipedia article.
- [x] Documented log1p min–max 0–100 popularity offset in `research/landmark_pageviews_method.md`; it is not a soundscape measurement.
- [x] Detail panel shows popularity evidence alongside the existing illustrative score and offset; scoring and audio mappings are unchanged.
- [ ] Measure 3–5 real landmarks during Priority 1 fieldwork. Defaults are `measured: false`; set true only with linked actual observations.

## Priority 4 — Listener experiment

- [x] `research/listener_experiment_protocol.md`: ten places across the observed score range, blinded randomized clips, eight adjective ratings, consent/recruitment, target 24 adults (minimum 15 complete sessions for exploratory analysis).
- [x] Static `research/listener_rating_form.html`: resume, playback-coverage checks, validated ratings, CSV export and delete. Collection stays disabled until ten genuine clips are prepared and hashed.
- [x] `research/prepare_listener_clips.py` prepares reviewed real tracks; `research/analyze_listener_experiment.py` implements clip-level Spearman with permutation test and participant bootstrap intervals.
- [ ] Generate/review clips, recruit consenting listeners, collect real responses, and run the analysis. `research/listener_experiment_results.md` remains `[PENDING]`; synthetic software checks are not participant data.

## Priority 5 — Finish what is incomplete

- [x] Prepared live checks for Ask a Local, music-style JSON, and two non-English language estimates; status recorded in `research/live_feature_checks.md`.
- [ ] All three Gemini features still need actual key-backed checks. Current status is **blocked / not tested**, not pass or fail.
- [x] Added two sourced, visually reviewed photos for each of the remaining 69 places. All 75 places now have `photos[]` with two entries; sources are in `research/landmark_photo_sources.csv`.
- [ ] Original all-free-licensed-photo target is not fully met: seven of the 138 additions are explicitly credited publisher images with rights reserved. Replace those or obtain reuse permission before treating the gallery as wholly free-licensed. The other 131 additions have open-license source metadata.
- [x] Prepared `research/accessibility_tester_brief.md`.
- [ ] **Future work, outside the current evaluation scope:** recruit blind/low-vision testers if participation becomes feasible. The user now expects this participation is unlikely. No outreach has been sent; completion of the current project does not depend on this recruitment.
- [ ] Full stat aria-labels, longitude stereo panning, and N/S/E/W navigation remain deferred as future work. Existing accessibility features are unvalidated with intended users. Technical checks can document keyboard and screen-reader behavior but cannot establish usability for blind/low-vision people. The general listener experiment remains separate and can proceed.

## Priority 6 — Writeup

- [x] `research/paper_draft.md` maps about §01 into Abstract/Introduction, §02/08 into Related Work, §03/05 into Method, and §06/07 into Limitations/Future Work.
- [ ] Results remain `[PENDING]` until Priority 1 produces real observations and analysis. The listener study is also pending.

Verification and reproducible commands: `research/IMPLEMENTATION_REPORT_2026-09-13.md`.

---

## Housekeeping

- [ ] **Repo-root file cleanup** — specific recommendation per file, not a vague "tidy up":
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
- [ ] **Add `.claude/` to `.gitignore`** — currently untracked but not ignored, so it'll keep
      showing up in `git status` as noise.
- [ ] **Add a `LICENSE` file.** Two reasonable options given Wikimedia CC-BY-SA/CC-BY photo
      credits are already carried per-image in the app: MIT for the code (keeps photo
      attribution as-is, most permissive for a KSEF project judges might want to try
      running), or CC-BY-NC-SA 4.0 if non-commercial use should be required. Pick one and add
      the file — "no license" currently defaults to all-rights-reserved, which blocks even
      judges from legally running a local copy.
