# Moodscape — mid-session report (2026-09-20)

Covers this session so far. Every number below was re-checked by running the code or reading the
file, not recalled. Status labels: **done** = built and tested, **prepared** = built but not run on
real people, **pending** = needs something only you can supply.

---

## 1. Where the project is on your five-stage pipeline

| Stage | Status | Evidence in the repo |
|---|---|---|
| 1. Perceive the problem | drafted | `research/paper_draft.md` §1–2 |
| 2. Idea | done | Activity score → pitch 440–880 Hz, tempo `42 + 110 × score` BPM, major/minor from visitor satisfaction (paper §4) |
| 3. Develop the idea | done | 17 regions, 75 places, accessible navigation, Suno prompts, generated tracks checked against prompts (`research/AUDIO_VERIFICATION_REPORT_EN.md`) |
| 4. Verify with real methods | **prepared, not run** | Listener protocol, rating form, analysis script, fieldwork questionnaire and analysis script — no participant or field data exists |
| 5. Results, feedback, development points | **pending** | `listener_experiment_results.md` and paper §7 both read `[PENDING]` |

The honest one-line summary: the project can now be tested; it has not been tested.

---

## 2. What changed this session

### 2.1 Agreement metrics added to the listener analysis (your request)

You asked whether a "matching number" like WAPE exists. Answer and what was built:

- **WAPE alone is a poor fit.** It needs both series on one scale; generating scores are 0–100
  and Eventfulness is a −1 to 1 index. It is included, but only on min–max-scaled series and
  labelled descriptive.
- **Added to `research/analyze_listener_experiment.py`:**
  - **Pairwise ordering accuracy** (the plain "matching %"): share of the 45 clip pairs whose
    rated order matches the score order; chance = 0.50. Bootstrap CI and clip-label permutation p.
    Prespecified **secondary**.
  - **Lin's CCC, WAPE, MAE** on min–max-scaled series. Descriptive, no threshold.
  - **ICC(2,1), ICC(2,k), Kendall's W** for rater consistency (do listeners agree with each
    other?).
- **Primary test unchanged:** Spearman ρ between the ten generating scores and ten clip-mean
  Eventfulness values, permutation p, participant bootstrap. Its decision rule is untouched. The
  secondary metrics use a separate random stream (seed + 1) so the primary numbers do not move.
- **Protocol amended** (`research/listener_experiment_protocol.md`, new "Agreement metrics"
  section) and dated 2026-09-20, before any recruitment or data, with the collection
  `protocol_version` left at `2026-09-13-v1`. Paper §6.2 and `DEVELOPMENT_PLAN.md` line 128
  updated to match.

### 2.2 Verification

- `research/test_research.py`: **19 tests pass** (14 before, 5 new).
- The ICC implementation is checked against the published Shrout & Fleiss (1979) Table 2 example
  (ICC(2,1) = .29, ICC(2,k) = .62). Kendall's W and the ordering/error metrics are checked
  against hand-worked values.
- An end-to-end run on **synthetic** fixtures produced the full report with the new section. It
  was written to a scratch file; the real `listener_experiment_results.md` still says `[PENDING]`.
- Tests run in a scratch virtualenv because system Python has no SciPy. To run them yourself you
  need `pip install numpy scipy`.

---

## 3. What is still blocking real results

1. **Clips not cleared for use.** `research/listener_stimuli.json` has `"ready": false`, and the
   `key_review` column is `PENDING` for all ten clips, including the Gangnam minor-key check. The
   `.mp3` files exist in `research/listener_clips/`, but I have not confirmed they are the reviewed,
   hash-frozen genuine Suno outputs the protocol requires.
   `research/listener_clips/README.md` still says "No audio is supplied yet", which is stale.
2. **No participants.** The target is 24 complete adults (minimum 15 for an exploratory pilot).
   Recruitment, supervisor review and consent have not started. I cannot do this, and I will not
   produce synthetic responses to fill the results file.
3. **No fieldwork data.** `research/analyze_soundwalk.py` exists and is tested, but
   `soundwalk_observation_template.csv` has no observations.

### Correction to something I told you earlier

I said the soundwalk analysis script was still unwritten. That was wrong. The plan names
`analyze_soundwalk.js`, but the script exists as **`research/analyze_soundwalk.py`**, has tests,
and handles the empty-CSV case. `DEVELOPMENT_PLAN.md` Priority 1 still lists the `.js` file as an
open task and should be updated.

---

## 4. Open problems that do not depend on data

| Item | Why it matters |
|---|---|
| "Built-in synth fallback" claim in `about.html` §03 and `audio/README.md` | The code has no such fallback (`DEVELOPMENT_PLAN.md` Priority 0). A reviewer can find this in minutes. |
| Paper reference list unverified | Paper says verification is pending; nothing may be cited as established until each entry is checked against its primary source. |
| Source CSVs vs. the 17-region table | Some source files contain only 15 regions; provenance needs reconciling before submission. |
| Uncommitted work | Many modified and untracked files (git status at session start), on branch `feature/accessibility-and-scoring-reform`. Nothing from this session is committed. |
| Stale docs | `listener_clips/README.md` (above) and the `.js` reference in `DEVELOPMENT_PLAN.md`. |

---

## 5. Development points (what to do next, in order)

1. **Review the ten clips** (mode, tempo, Gangnam), record notes in `key_review`, run
   `python3 research/prepare_listener_clips.py` so the manifest sets `ready` and freezes hashes.
   Do not hand-edit the flag.
2. **Freeze the protocol and record a recruitment deadline** before the first invitation, then get
   supervisor approval and begin recruiting.
3. **Resolve the synth-fallback mismatch**: build the fallback or correct the wording.
4. **Once ≥15 complete sessions exist**, run
   `python3 research/analyze_listener_experiment.py path/to/*.csv`. Report the result whichever way
   it comes out, including non-support.
5. **Fieldwork in parallel**: at least a small soundwalk, since the listener study tests only
   whether the music encodes the model, not whether the model describes real places.
6. **Verify references**, reconcile the region tables, then commit and open the PR.

---

## 6. What this report does not claim

No perceptual validity, no accessibility effectiveness, and no agreement between listeners and the
model have been shown. The only test results are unit tests on synthetic fixtures.
