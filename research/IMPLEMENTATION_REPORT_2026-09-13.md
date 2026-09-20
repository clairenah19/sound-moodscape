# Moodscape implementation report — 2026-09-13

This pass implements the research infrastructure and UI evidence display for priorities 2–6. It does not supply field observations, participant responses, or successful live API calls.

## Delivered

- Reproducible Wikimedia REST pull, all-place CSV/JSON, raw response cache, missingness and log-normalization documentation. Window: September 2025–August 2026; 58 complete, one partial, 16 missing article links.
- Separate popularity evidence and original illustrative offset in place details. No score or music-mapping replacement. Unmeasured places remain `measured: false`.
- Ten-stimulus listener protocol, gated static form, genuine-track preparation, CSV validation and clip-level correlation analysis. Results remain `[PENDING]`.
- Live three-feature Gemini harness and Gangnam Suno/human-listening harness. No key values are embedded or recorded in reports.
- 138 sourced and visually reviewed images added to 69 galleries; all 75 places have two photos[] entries. Metadata/source audit retained. 131 additions carry open-license metadata; seven carry explicit publisher rights-reserved labels. This completes photo coverage but not the older all-free-licensed target. Asan exhibit imagery is explicitly captioned as a scale model. KTO preview watermark is retained. External hotlinks can expire.
- Tester brief and paper draft with pending Results. No tester outreach; no changes to map.js/audio.js accessibility behavior.
- Fixed the existing malformed music-prediction inline click handler by registering the click listener after rendering.

## Verification

Seven research unit tests passed: date windows, missing vs zero coverage, log scaling, rating conversion, duplicate/hash/session validation, insufficient-sample gate, and clip-level correlation. Synthetic data were used solely for software checks outside the project; they are not research results.

An isolated Chrome browser test passed: current place panel and Gangnam minor prompt, pending collection gate, ten randomized synthetic audio trials, seek-to-end prevention, radio validation, resume, CSV export, and response deletion. No browser JavaScript exceptions were observed. This does not establish live Gemini/Suno functionality or audible key correctness.

Final JavaScript/Python syntax checks passed. All 75 detail panels rendered without JavaScript errors, missing-key controls reported blocked correctly, and all 75 galleries contain two entries. Every effective place score, tempo and intended key matched the original; map.js, audio.js and prompt.js are byte-for-byte unchanged.

All 138 selected photo previews were downloaded and visually reviewed against source metadata. Original scores and the six existing galleries are preserved.

## Reproduce

Serve the project root with `python3 -m http.server 8000`.

```sh
node research/export_landmarks.js > research/landmark_inventory.json
python3 research/fetch_landmark_pageviews.py --start 2025-09-01 --end 2026-08-31
python3 -m pip install numpy scipy
python3 -m unittest discover -s research -p test_research.py
python3 research/analyze_listener_experiment.py
```

The analyzer without participant files reports pending and does not manufacture results. See its `--help` for real response-file analysis. Clip preparation additionally requires ffmpeg/ffprobe. Browser collection uses localStorage and Web Crypto; use localhost or HTTPS.

Photo sourcing script and reviewed selection are retained for provenance. `install_reviewed_photos.py` is a one-time installer and intentionally refuses to overwrite an existing gallery. Raw photo search caches and synthetic test outputs are not project deliverables.

## Outstanding dependencies

- Original browser/origin containing usable keys, or user-entered keys, for the live Gemini and Suno checks.
- Human listening review of an actual Gangnam output; prompt text alone is insufficient.
- Ten genuine reviewed tracks, consenting listeners, and real response CSVs before listener results.
- Priority 1 field observations before marking landmarks measured or writing paper Results.
- Scope update: blind/low-vision participation is unlikely for the current study. Intended-user evaluation and the deferred accessibility implementation are future work, not a blocker for the general listener study or current project. No accessibility-validation claim is supported.
