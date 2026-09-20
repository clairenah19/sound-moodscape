# Moodscape listener experiment — preregistration draft

Version: 2026-09-13-v1. Status: prepared, not run. Freeze this document and the clip hashes before recruitment.

## Question and scope

Does the activity ordering encoded in Moodscape's real generated music correspond to listeners' rated Eventfulness? This tests the encoding of the **modelled** score, not whether the score describes the actual landmark. Priority 1 fieldwork is the separate validity test. Eight soundscape adjectives are adapted to music; this is not an ISO-compliant in-situ soundwalk.

## Stimulus set

Ten places were selected deterministically across the current 75-place score distribution (rank quantiles, endpoints included). Gangnam replaces the nearby upper-quantile selection to include the Pleasantness-driven minor-key case. Do not alter selection after hearing participant responses.

The exact scores, prompts, target BPM, and intended modes are frozen in `listener_stimulus_metadata.csv`. The selection spans the **observed** range (0–87.23), not an invented full 0–100 distribution:

| Clip | Place (researcher only) | Approximate generating score |
|---|---|---:|
| clip01 | Gyeongbokgung Palace | 0.00 |
| clip02 | Hanbat Arboretum | 18.57 |
| clip03 | Naganeupseong Folk Village | 23.94 |
| clip04 | Korean Folk Village | 30.42 |
| clip05 | Oeam Folk Village | 35.23 |
| clip06 | Gunsan Modern History Street | 41.41 |
| clip07 | Government Complex Sejong | 48.40 |
| clip08 | Kia AutoLand Gwangju | 58.91 |
| clip09 | Gangnam | 66.27 |
| clip10 | Hyundai Motor Asan Plant | 87.23 |

Use real Suno output, one fixed generation per place, with the exact prompt archived. Document provider/model, generation date, task identifier, source URL, permissions, and any failed generation attempts. Use the first technically usable output; do not select tracks according to whether they produce the desired hypothesis. Have a musically knowledgeable reviewer check mode, record uncertainty, and record Gangnam's minor-key check explicitly. If a track does not follow its intended mode, report that mismatch; do not relabel it.

Extract 25 seconds from 5–30 seconds of each source. Apply the same two-pass loudness normalization target (-18 LUFS, -1 dBTP) and strip metadata; archive originals. Use `prepare_listener_clips.py` with FFmpeg installed. Freeze the resulting SHA-256 hashes in `listener_stimuli.json`. Keep `ready: false` until all ten files exist, are genuine Suno outputs, and have been reviewed. The collector verifies the hashes before accepting responses.

Neutral filenames and ordinal headings conceal names, scores, genre, and mode in the participant UI. This static site is not resistant to a participant inspecting its source files. Ask participants not to browse project files until finished; do not claim cryptographic blinding.

## Participants and recruitment

Target **24 complete adult participants**; minimum **15** for an explicitly exploratory pilot. This is a feasibility target, not a power calculation or proof of adequate power. Recruit up to 30 to allow withdrawal/incomplete sessions. Stop at 24 complete sessions or at the prespecified recruitment deadline (record the deadline before the first invitation), never based on the p-value. If fewer than 15 complete, keep inference pending and report feasibility only.

Recruit adult volunteers through the researcher's school/community contacts and music/general-interest groups. Avoid a cohort made exclusively of trained musicians. The researcher chooses contacts; no invitations have been sent. Participation is voluntary, with no grade or service consequence. Record aggregate recruitment route, hearing-access needs, and music-experience distribution separately without linking names to response files. Include blind/low-vision participants where accessible recruitment is feasible; never claim subgroup validation from 1–2 testers.

Suggested invitation: “Would you like to join a voluntary 12–18 minute study about how people interpret short musical clips? You will listen and rate eight atmosphere descriptors. No names are collected in the rating file, and you may stop without penalty. Please reply if interested; we can discuss access needs before you decide.”

Obtain the applicable school/research supervisor review before recruiting. Obtain consent using the form's plain-language statement. Adults only in this pilot; including minors would require a separately reviewed consent procedure. Agree on the researcher/contact and CSV-return channel before sending the form. No recruitment is automated.

## Task and collection

1. Give identical instructions; do not name places, explain score ordering, or reveal the hypothesis's expected direction.
2. Ask participants to choose a comfortable volume, preferably use headphones, and keep the setup constant.
3. Obtain consent. The form assigns a random UUID and a uniformly shuffled clip order, saved in the browser.
4. Present each 25-second clip without map, photo, score, or place name. Allow replay. Seeking does not count as full listening.
5. Ask: “To what extent do you agree that the atmosphere communicated by this music is …” pleasant, chaotic, vibrant, uneventful, calm, annoying, eventful, monotonous. Fixed adjective order; five radio options from strongly disagree (1) to strongly agree (5). No default answer.
6. Require all eight ratings before saving the trial. Save clip hash, presentation order, actual played coverage, response duration, consent timestamp, and protocol/stimulus version with each row.
7. Download one CSV per participant. Participants knowingly return it through the agreed channel. The page does not send responses automatically. Returning a partial CSV is allowed, but incomplete sessions are excluded from the primary analysis.

Responses are stored in localStorage only for resume/download. On shared devices, ask participants to download and then delete the saved session before another participant starts. The researcher stores returned data in an access-controlled location and records retention/deletion arrangements with the supervising institution. Do not commit participant-level response files to the public repository. Withdrawals can be identified using the random participant code; there is no name lookup in the form.

## Outcomes and prespecified analysis

For each participant/clip, compute adapted Eventfulness:

`[(eventful − uneventful) + cos(45°) × (chaotic − calm + vibrant − monotonous)] / (4 + √32)`.

Primary statistic: **Spearman correlation between the ten generating activity scores and the ten clip-mean Eventfulness ratings**. Participants are repeated raters; 24 × 10 ratings are not 240 independent stimuli. Use a two-sided Monte Carlo permutation test with 49,999 permutations of clip labels, +1 correction, seed 20260913. Report rho, p, participant count, and ten clip means. A positive rho with p < .05 meets the stated pilot criterion; otherwise explicitly report non-support.

Report a 95% percentile interval from 5,000 participant-bootstrap samples (resample entire participants and all their ratings together). This interval is conditional on the selected clips and does not support population-wide generalization over places or musical outputs. The small, purposive stimulus set remains a limitation. Pleasantness ratings and presentation-order patterns may be described as exploratory; no additional confirmatory tests or selective condition comparisons are planned.

Exclude incomplete sessions. Reject invalid Likert values, mismatched hashes/versions, missing consent, impossible timing, or conflicting duplicate trials. Deduplicate exact repeated downloads. Do not remove unfavorable ratings, “outliers,” or listeners with low correlations. Log all exclusions and any post-freeze amendments.

Run `python3 research/analyze_listener_experiment.py /path/to/returned/*.csv` with NumPy and SciPy installed. With no rows, the script reports pending and does not overwrite results. With fewer than 15 complete sessions, it also leaves inference pending. The empty results file is not a failed or null experiment.

## Source and instrument notes

- [Wikimedia pageview API](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/reference/page-views.html) documents the separate readership measure; it is not an outcome in this listening study.
- Soundscape projection and fieldwork procedures are recorded in `soundscape_relationship_validation_protocol.md` and `iso_pe_calculator.js`. This study deliberately labels its musical adaptation separately.
- No real participant observations or completed listening validation exist at protocol creation.
