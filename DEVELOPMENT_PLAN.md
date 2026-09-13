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

**New concrete gap found while speccing this out:** the calculator has no code path that
reads an actual CSV — only the hand-written example in `runExample()`. Before real field data
exists, this will silently not work.

- [ ] **Write `research/analyze_soundwalk.js`** — a small Node script that:
      1. reads `research/soundwalk_observation_template.csv` with a plain CSV parser (no
         dependency needed — split on commas, or add `csv-parse` if quoting gets hairy),
      2. groups rows by `site_name` + `date` + `start_time` into site-time observations,
      3. calls `aggregateSiteTime()` per group and `eventfulnessScatterData()` across all
         groups (using `laeq_db` as the initial predictor),
      4. prints a table of site, n, Pleasantness mean ± CI, Eventfulness mean ± CI,
      5. exits cleanly with a clear message ("0 rows found — no field data collected yet") if
         the CSV is still just the header row, so running it early doesn't look like a crash.
      - **Done when:** running `node research/analyze_soundwalk.js` against the still-empty
        template prints that clear "no data yet" message instead of an error, and the same
        script works unmodified once real rows are added.

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

## Priority 2 — Pleasantness has no live path

**Done.** Nothing further required unless testing surfaces a bug. For reference:
`getMusicalKey(place, stateName)` in `prompt.js` now compares
`REGION_MODEL[stateName].pleasantness` against `PLEASANTNESS_MEDIAN` (`data.js`) for its
default case. Verified: Gangnam (Seoul) → minor key, because Seoul's Pleasantness (75.8) sits
below the 17-region median (77.7).

- [ ] **One remaining check, not yet done:** generate one real Suno track for a place that
      flipped key under this change (Gangnam is the clearest case) and confirm the returned
      MP3 is audibly in a minor key. This needs a Suno key to test — flag as blocked if none
      is available, don't skip silently.

## Priority 3 — Landmark level is still illustrative

**Cheap fix done** — every place shows "Illustrative offset, not measured."

**Concrete, automatable improvement found this pass** (doesn't need fieldwork): Wikipedia
page-view counts are a real, free, per-landmark popularity signal, available with no API key
via `https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/<Article_Title>/monthly/<start>/<end>`. Most places already have a
Wikipedia URL in `photoPage`.

- [ ] Write `research/fetch_landmark_pageviews.js` (or do it as a one-off script) that:
      1. loops over every place in `data.js` whose `photoPage` is an `en.wikipedia.org` URL,
      2. extracts the article title and calls the pageviews API for the last 12 months,
      3. writes the result to `research/moodscape_landmark_pageviews.csv` (columns: state,
         place, wikipedia_title, avg_monthly_views, months_covered).
      - **Done when:** the CSV has a row for every place with a Wikipedia `photoPage` (expect
        most of the 75; note which ones lack one).
- [ ] Decide and document a log-scaled 0–100 mapping from pageviews to a landmark-level
      Eventfulness offset (same log-then-min-max approach as `data.js`'s `logScale()`, for
      consistency), and note in `about.html` that this is a *popularity* proxy, explicitly
      not a *soundscape* measurement — don't let it get cited as more than it is.
- [ ] Wire it in as an *optional* override: if a place has pageview data, show both the
      current illustrative offset and the pageview-derived one side by side in the UI, rather
      than silently replacing one unvalidated number with another.
- [ ] **Better fix, still fieldwork-gated:** during Priority 1's site visits, measure 3–5 of
      the actual landmarks (not just generic street sites) so at least a handful of places
      get a real, non-proxy score. Add those as a `measured: true` flag on the place object.

## Priority 4 — Listener experiment

No protocol currently exists for this at all (unlike Priority 1). Unlike Priority 1, **this
one does not require in-person fieldwork** — participants can rate audio clips remotely.

- [ ] **Write `research/listener_experiment_protocol.md`**, covering:
      - **Stimulus set:** 8–10 places spanning the full score range (pick 2 each from
        very-peaceful/calm/balanced/lively/very-exciting bands using `MOOD_LABEL()`'s
        buckets), each rendered as a real Suno track — not synth fallback, since the claim
        being tested is about the generated music.
      - **Task:** listener hears one clip, rates it on the same 8-item ISO scale used in
        `soundwalk_questionnaire_ko.md` (English version), blind to the place name/score.
      - **Sample size:** ~15 listeners × 8–10 clips = enough for a paired comparison against
        the generating score; state the actual test up front (Spearman correlation between
        rated Eventfulness and the place's activity score; a paired t-test or Wilcoxon if
        comparing two specific conditions).
      - **Recruitment:** who, how many, how contacted, consent language, anonymity.
- [ ] **Build the collection tool.** A single static HTML page (`research/listener_rating_form.html`, no framework needed — same stack as the rest of the app) that: plays each of the
      8–10 clips in a random order per respondent, shows the 8-item scale as radio buttons,
      and appends responses to a downloadable CSV or a `localStorage`-backed table the
      respondent can export. This is buildable now, independent of recruiting anyone.
- [ ] Run it with whatever real listeners are reachable (classmates, family, online), analyze
      with the correlation test named above, and write results into
      `research/listener_experiment_results.md` — again, report a null result plainly if
      that's what happens.

## Priority 5 — Finish what is live but incomplete

- [ ] **Confirm the Gemini features actually complete.** Get a real (even free-tier) Gemini
      API key, open the app, and manually check three things complete without error: (1) Ask
      a Local returns a persona-flavored reply, (2) the AI music-style predictor returns valid
      JSON with `genre`/`instrumentation`/`key`, (3) the language-accessibility estimate
      returns a 0–100 score for at least 2 non-English languages. Note the exact error if any
      of the three fail — "never tested" and "tested and broken" need different fixes.
- [ ] **Photo gallery — 69 places remaining** (6 of 75 done, Seoul only). Concrete scope:
      2 additional real, free-licensed Wikimedia Commons photos per place, matching the
      pattern already in `data.js`'s `photos[]` array for Seoul (url/artist/license/page).
      At ~2 photos × 69 places = 138 images to source and verify — worth splitting across
      multiple sessions/passes by region rather than attempting in one sitting.
- [ ] **Accessibility gaps**, in priority order:
      1. No testing with blind or low-vision users — everything else is informed guesswork
         until this happens. Recruit even 1–2 testers before adding more accessibility code.
      2. Full stat readout in announcements (the raw density/tourism/complaints numbers, not
         just the final score) — add to the `aria-label` string built in `map.js`.
      3. Stereo/spatial panning by longitude — set `StereoPannerNode.pan` from each region's
         relative east-west position when the accessibility tick sound plays.
      4. Directional (N/S/E/W) navigation instead of the fixed 17-item tab order.

## Priority 6 — Writeup

- [ ] Draft `research/paper_draft.md` with this section mapping, copying stable prose from
      `about.html` and adapting tone (paper voice, not app-copy voice):
      - Abstract + Introduction ← §01 (research question)
      - Related Work ← §02 + §08
      - Method ← §03 + §05
      - Results ← **leave as `[PENDING — see Priority 1 pilot_results.md]`**, don't fabricate
        placeholder numbers
      - Limitations / Future Work ← §06 + §07
- [ ] Once Priority 1 produces `research/pilot_results.md`, fill in the Results section for
      real and remove the pending marker.

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
