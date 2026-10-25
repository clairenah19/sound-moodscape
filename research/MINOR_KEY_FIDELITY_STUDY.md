# Prompt-to-Audio Mode Fidelity in Moodscape: An Iterative Investigation

**Project:** Moodscape (Suno-based geographic sonification)
**Scope:** Why Suno-generated audio frequently fails to honor the major/minor key
instruction in `buildSunoPrompt()`, and what, if anything, fixes it.
**Status:** Partially resolved. One repeatable fix found (institutional-category
style, Sejong major-key correction). One candidate fix found but does not
generalize (genre-word swapping). Root-note precision shown to be
uncontrollable; prompt language corrected to stop overclaiming it.

---

## Abstract

An initial real-audio verification of 10 Suno-generated tracks
(`AUDIO_VERIFICATION_REPORT_EN.md`) found a 50% major/minor key match rate,
with all three minor-key requests failing outright (0/3). This study traces
the subsequent investigation: reworded prompt language, a corrected request
shape (`customMode:true`), a landmark-specific categorization bug caught by
ear, a real-world factual correction supplied by the user, a full 10-clip
re-verification, and a targeted genre-word experiment. The mode match rate
rose from 5/10 to 7/10 under the corrected request shape, and a specific
genre-word substitution raised one previously-failing clip from 0/3 to 3/3 —
but the same substitution method failed to replicate on a second clip (0/3),
and exact root-note (pitch) accuracy was shown to be uncontrolled even when
mode succeeded. The practical conclusion is: mode fidelity is improvable but
not reliably solved, root-note precision should not be claimed, and no single
prompt-engineering rule generalizes across all landmarks yet.

---

## 1. Introduction

### 1.1 How the idea arose

The original chart (`research/plot_project_results.py` →
`moodscape_results_graph.png`) compares, for 10 real Suno tracks, the tempo
and key the prompt requested against what librosa measured in the actual
audio. Reading the per-clip CSV (`audio_analysis_results.csv`) rather than
only the aggregate "50%" headline revealed a pattern the aggregate hid: the
failures were not evenly distributed across major and minor requests. Every
one of the 3 clips that asked for a minor key came back major. Major
requests succeeded 5/7. This asymmetry — not "50% random" but "minor key
specifically and consistently lost" — was the actual finding worth
investigating, and became the idea: find out *why* minor key fails, and
whether it is fixable.

### 1.2 Why this matters for the project

`about.html` describes the mood→music mapping as the project's "sonification
formula." If the key/mode half of that formula is unreliable, that is a
direct, measurable gap between what the project claims to encode and what a
listener actually hears — relevant to the project's own accessibility and
legitimacy claims (`DEVELOPMENT_PLAN.md` Priority 2, ISO 12913
Pleasantness/Eventfulness axis work).

---

## 2. Methods

### 2.1 Wording iteration (Development Stage 1)

The original prompt buried the key as one word at the end of a long,
comma-separated adjective list, e.g. for Gangnam:

> "...mellow lo-fi hip-hop, relaxing city-pop synth pads, chill urban beat,
> warm, **minor key**, around 115 BPM..."

`getSunoStyle()` and `buildSunoPrompt()` (`prompt.js`) were rewritten to:

1. Strip pleasant-coded adjectives that could compete with a minor-key
   request (`bright|cheerful|happy|uplifting|celebratory|warm|chill|mellow|
   sleek|glossy|shimmer(?:ing)?|sunny|playful|breezy|cozy`).
2. Move the key out of the adjective list into its own short, early
   sentence, paired with a specific root note (`getSunoRootNote()`, already
   computed but previously unused) and explicit mood words instead of the
   bare theory term "minor key" (e.g. "melancholic, somber, shadowed
   tonality").

### 2.2 Request-shape discovery (Development Stage 2)

While building the first real-audio retest, inspection of `prompt.js`'s
`buildSunoGenerationRequest()` showed the live app sends
`{customMode: true, style, title}` — not the `{customMode: false, prompt}`
shape used by both the original 10-clip test
(`research/generate_listener_clips.py`) and the first retest. Git history
confirmed `customMode: true` was introduced in commit `52b0d62`
(2026-09-20), after the original real-audio test ran. This meant the
original "50%" figure was measured against a request shape the live app no
longer uses — a second, independent variable had been conflated with the
wording change.

### 2.3 Verification protocol

All real-audio tests in this study follow the same procedure:
1. Build the exact prompt text / style+title via the live app's own
   functions (`buildSunoPrompt()`, `getMusicalKey()`, `getSunoRootNote()`),
   read directly from a running instance of the app, not reconstructed by
   hand.
2. POST to `sunoapi.org`'s `/api/v1/generate`, polling
   `/api/v1/generate/record-info` until an audio URL appears (mirroring
   `sunoGenerate()` in `prompt.js`).
3. Download the resulting MP3.
4. Analyze it with `research/analyze_generated_audio.py`'s `analyze_clip()`
   — librosa tempo detection + Krumhansl-Schmuckler key estimation — the
   same published, non-project-specific algorithm used in the original
   verification report.
5. Compare detected key/tempo against what was requested.

No step in this pipeline modifies audio after generation; "octave
correction," discussed in the original report, is a separate post-hoc
re-labeling of the detected tempo number only, not used in the mode analysis.

---

## 3. Results

### 3.1 Wording alone, old request shape — failed

Gangnam retested with the Stage-1 reworded prompt but the old
`customMode:false` shape: detected D# major at 0.938 confidence — a *more*
confident wrong answer than the original failure (0.921). Wording change
alone was insufficient.

### 3.2 Wording + corrected request shape — succeeded (n=2)

Sejong and Asan, retested with the same reworded text but
`customMode:true`:

| Clip | Requested | Detected | Match |
|---|---|---|---|
| Sejong | D# minor | D# minor (0.763) | ✅ |
| Asan | G minor | G minor (0.666) | ✅ |

### 3.3 Landmark categorization bug (feedback-driven)

The user, listening to the Sejong result, asked what Sejong actually
contains and said the music didn't match. Investigation found
`PLACE_TERMS.industrial` matched on the bare substring `"complex"`, and
Sejong's `type` field is `"National government complex"` — an accidental
keyword collision with factory/semiconductor-plant terms (`data.js:79`,
`prompt.js:19`), giving a government building with a rooftop garden a
"glitchy minimalist electronic, cleanroom atmosphere" style. A new
`institutional` category was added, checked before `industrial`
(`prompt.js:19-24, 119-131`), excluding `"assembly"` so real car-assembly
plants stay industrial. Re-verified: D# minor (0.827 confidence), 95.3 BPM
vs. 95 requested (0.3% error).

### 3.4 Real-world factual correction (feedback-driven)

The user supplied information absent from the data: Sejong is a planned
administrative city with a large kindergarten and young-family population,
not a solemn place, and should not be minor key. `"government"` was added
to `PLACE_TERMS.keyMajor.type`, and `data.js`'s `character` field for this
place was updated to mention the kindergartens/families. Re-verified: D#
major, 0.942 confidence — the highest confidence recorded in this entire
study — 95.3 BPM vs. 95 (0.3% error).

### 3.5 Full 10-landmark re-verification

All 10 original clips were regenerated with the current, fixed
`buildSunoPrompt()` output and `customMode:true`
(`research/reverify_all_landmarks.py`, `research/audio_analysis_results_v2.csv`):

| Metric | Original (customMode:false) | v2 (customMode:true, fixed prompts) |
|---|---|---|
| Mode match | 5/10 (50%) | 7/10 (70%) |
| Minor-key requests matched | 0/3 | 0/2 (Sejong no longer minor) |
| Median octave-aware tempo error (detected may be 1/3, 1/2, 1, 2 or 3x the request) | 1.1% | 1.4% |
| Mean octave-aware tempo error (same rule) | 7.7% | 7.7% |
| Clips not within 5% of any such multiple | 2 (clip07, clip08) | 2 (clip06, clip08) |

Critically, Asan — which had matched exactly in the isolated n=2 test
(§3.2) — failed in this larger batch using the *identical* prompt (D major
detected instead of G minor). This demonstrates Suno's generation is
stochastic: identical input does not guarantee identical output, and single
successful trials cannot be treated as fixes.

### 3.6 Genre-word substitution experiment

Hypothesis: genre nouns (e.g. "lo-fi hip-hop", "city-pop"), not just mood
adjectives, carry a statistical major-key bias from training data, and
compete with the explicit minor-key instruction independently of the
Stage-1 adjective fix.

**Gangnam** (genre swapped: "lo-fi hip-hop, city-pop synth pads, urban beat"
→ "dark synth-pop, moody downtempo electronic, atmospheric minor-key
synths"), 3 runs, mode clause/BPM/instrumentation held constant:

| Run | Detected | Match |
|---|---|---|
| 1 | F minor (0.643) | ✅ |
| 2 | G minor (0.684) | ✅ |
| 3 | D# minor (0.805) | ✅ |

3/3, versus 0/3 for this clip across every prior test with the original
genre words.

**Asan** (genre swapped: "futuristic progressive electronic, clean
high-tech synth layers, driving modular rhythm" → "dark industrial techno,
brooding synth bassline, tense mechanical atmosphere"), same protocol:

| Run | Detected | Match |
|---|---|---|
| 1 | D major (0.812) | ❌ |
| 2 | D major (0.592) | ❌ |
| 3 | G major (0.594) | ❌ |

0/3. The method did not generalize. Tempo was identical (137.2 BPM) across
all 3 runs, suggesting some generation parameters are stable for this prompt
while mode is not.

### 3.7 Root-note (pitch) instability

Across Gangnam's 4 successful minor-key generations (§3.2, §3.6), the exact
root note requested ("F minor" every time) was honored only once: F, then G,
D#, F. Mode succeeded consistently; pitch center did not.

---

## 4. Discussion

### 4.1 What is actually confirmed

- Request shape (`customMode:true` vs. `false`) correlates with better mode
  fidelity in the aggregate (70% vs. 50%), though this is one comparison, not
  a controlled large-sample experiment.
- A landmark-specific style-categorization bug was a real, confirmed defect,
  independent of any Suno behavior — fixed and verified.
- A real-world factual gap (kindergartens) produced a wrong mood assignment
  independent of any Suno behavior — fixed and verified.
- Genre-word choice can flip mode reliability for at least one place, 3/3
  vs. 0/3 — a real, repeatable effect for that specific case.
- Root note (pitch) is not reliably controlled via text prompting, even when
  mode succeeds.

### 4.2 What is not confirmed

- The genre-word hypothesis does not generalize (Asan: 0/3 with the same
  method). Mode fidelity appears to depend on an interaction between genre,
  place, and possibly other unidentified factors, not a single fixable rule.
- Suno's generation is stochastic — the same exact prompt produced different
  outcomes for Asan across different runs (§3.2 vs. §3.5). Any single
  success or failure, including several results in this study, could be
  partly chance rather than a verified causal effect. Sample sizes here
  (n=2 to n=10) are small relative to the variance observed.
- No human has listened through these clips to confirm the automated
  key/tempo detection reflects what a listener would actually perceive.

### 4.3 Feedback that shaped this investigation

This study was driven substantially by user feedback, not solely by planned
experimentation:

1. The user asked for a direct, honest (non-report-style) explanation of
   why minor key failed, which led to examining per-clip data rather than
   the aggregate figure.
2. The user caught the Sejong style mismatch by ear ("what is there a lot of
   in Sejong — doesn't match the music") before any code was known to be
   wrong — this is what surfaced the `industrial`/`"complex"` keyword
   collision.
3. The user supplied the kindergarten/young-families fact from outside the
   project's data entirely, overriding a default the regional-pleasantness
   model had gotten defensibly but incorrectly.
4. The user explicitly stated that catching this class of mismatch is also
   the implementer's responsibility ("these things are also your part"),
   not something that should wait on being caught by ear each time.
5. The user pushed back on an unverified claim ("I thought we tried
   changing the adjectives") that correctly distinguished two different
   variables (adjectives vs. genre nouns) that had been conflated, which is
   what prompted the genre-swap experiment in §3.6.

---

## 5. Recommendations for Use

1. **Do not claim exact root/pitch accuracy anywhere user-facing.** The
   `buildSunoPrompt()` phrasing was changed from "In {root} minor key" to
   "In a minor key (around {root})" to stop asserting a precision §3.7
   shows is false. This is implemented (`prompt.js`, this commit).
2. **Do not claim a fixed "mode fidelity %" without citing the request
   shape and sample size it was measured under.** The original "50%" and
   this study's "70%" are not directly comparable to a hypothetical future
   number without also stating `customMode` setting, n, and whether a
   single run or repeated runs were used.
3. **Do not generalize the genre-word fix without per-place testing.** It
   is not a global prompt-engineering rule; apply it only where verified,
   and treat each application as its own small experiment, not a known fix.
4. **Treat any single successful generation as inconclusive.** Given
   demonstrated stochasticity (§3.5), a claim of "fixed" should require at
   least 3 repeated real generations, not 1.
5. **Prioritize institutional-category-style fixes and factual corrections
   over further Suno-side prompt tuning**, since those two interventions
   (§3.3, §3.4) are the two unambiguous, fully-repeatable wins in this
   study — they fix defects in Moodscape's own code/data, not attempts to
   control a third-party model's internals.
6. **A human listening pass remains the single biggest open gap** across
   both the original report and this study. All conclusions here rest on
   automated detection (librosa + Krumhansl-Schmuckler), not confirmed
   human perception.

---

## 6. Conclusion

Mode fidelity in Moodscape's Suno pipeline is partially, not fully,
improvable through prompt engineering. Two defects fully within the
project's own control — a keyword-collision style bug and a missing
real-world fact — were found and fixed with full real-audio confirmation.
One prompt-engineering intervention (genre-word substitution) produced a
clean, repeatable win for one landmark and a clean, repeatable failure for
another, meaning it is a real but non-general effect rather than a solved
problem. Root-note precision was shown to be uncontrolled and the prompt
language was corrected to stop claiming it. No further Suno-side change is
recommended without first running a larger, repeated-trial experiment design
than this study had time or budget for.
