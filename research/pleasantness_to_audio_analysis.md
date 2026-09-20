# Does Visitor Pleasantness actually reach the audio?

Written 2026-09-20 to close DEVELOPMENT_PLAN.md Priority 2, whose open item still read
"**Blocked:** no usable key was accessible." That is out of date — the 2026-09-13 run
(`6bc9ded`) generated ten real Suno tracks with a real key and analysed them, which answers
the question directly. This file records the answer and what it implies.

Every number below was recomputed from the live code and data while writing this.

## The claim under test

`about.html` §03 and `README.md` describe musical key/mode as being driven by the region's
Visitor Pleasantness relative to the national median. The Priority 2 item asked specifically:
does a Gangnam track, whose prompt requests a minor key, actually come back in minor?

## Answer: no — and the request is attenuated three separate times

### 1. Pleasantness decides the key for fewer than half of all places

`getMusicalKey()` in `prompt.js` checks two hard-coded category overrides before it ever
consults Pleasantness:

| Deciding branch | Places | Share |
|---|---:|---:|
| Solemn override (cemetery, memorial, DMZ, observatory, cave, tomb…) | 6 | 8.0% |
| Nature/traditional override (park, beach, temple, palace, hanok, village…) | 35 | 46.7% |
| **Visitor Pleasantness (the default branch)** | **34** | **45.3%** |
| | **75** | |

For 41 of 75 places, Pleasantness has no effect on the key whatsoever.

### 2. Where it does decide, it decides per region, not per place

The default branch reads `REGION_MODEL[stateName].pleasantness` — a regional value. Every
default-branch place in the same region therefore receives the same key. Seoul's Hongdae,
Gangnam, N Seoul Tower and Dongdaemun Design Plaza are all minor for one reason: Seoul's
regional Pleasantness. That is **17 distinct decisions, not 75**.

### 3. The median split is an artifact, not a measurement

`PLEASANTNESS_MEDIAN` is computed in `data.js` as the median of the 17 regions' own values:

```js
const PLEASANTNESS_VALUES = Object.values(REGION_MODEL).map(m => m.pleasantness).sort((a,b) => a-b);
const PLEASANTNESS_MEDIAN = PLEASANTNESS_VALUES[Math.floor(PLEASANTNESS_VALUES.length / 2)];
```

Two consequences follow, and neither is about Korea:

- **Roughly half the regions get a minor key by construction.** Currently 9 major / 8 minor.
  If every region in the country scored 95/100 — uniformly delightful — 8 would *still* be
  assigned minor keys. The key encodes rank among 17, not pleasantness in any absolute sense.
- **The threshold sits inside the noise.** All 17 values span 75.05–81.74, a range of 6.69
  points on a 0–100 scale. The median is 77.72, which is *exactly* Gyeongsangbuk-do's value —
  it is classified major only because the comparison is `>=`. Busan sits 0.16 above the line,
  Gangwon 0.39, Ulsan 0.55. A trivial revision to the underlying tourism-survey inputs would
  flip several regions from major to minor.

| Region | Pleasantness | Key | Distance from median |
|---|---:|---|---:|
| Daejeon | 75.05 | minor | 2.67 |
| Sejongsi | 75.15 | minor | 2.57 |
| Daegu | 75.34 | minor | 2.38 |
| Seoul | 75.81 | minor | 1.91 |
| Incheon | 76.15 | minor | 1.57 |
| Chungcheongnam-do | 76.53 | minor | 1.19 |
| Chungcheongbuk-do | 76.85 | minor | 0.87 |
| Gyeonggi-do | 77.01 | minor | 0.71 |
| **Gyeongsangbuk-do** | **77.72** | **major** | **0.00** ← on the line |
| Busan | 77.88 | major | 0.16 |
| Gangwon | 78.11 | major | 0.39 |
| Ulsan | 78.27 | major | 0.55 |
| Gyeongsangnam-do | 79.25 | major | 1.53 |
| Jeju-do | 79.70 | major | 1.98 |
| Jeollabuk-do | 80.91 | major | 3.19 |
| Gwangju | 80.94 | major | 3.22 |
| Jeollanam-do | 81.74 | major | 4.02 |

### 4. And the request only survives into the audio half the time

From `research/audio_analysis_results.csv` — ten real generated tracks, key estimated with
Krumhansl-Schmuckler against the published Krumhansl & Kessler (1982) profiles:

| | |
|---|---|
| Major/minor match rate | **5 / 10 (50%)** |
| Mean detection confidence, matches | 0.885 |
| Mean detection confidence, mismatches | 0.742 |

Gangnam specifically — the exact case Priority 2 named:

| | |
|---|---|
| Requested mode | **minor** |
| Detected key | **A# major** |
| Detection confidence | **0.921** |
| Requested BPM / detected | 115 / 114.8 (0.2% error) |

The high confidence matters. The detector was not undecided; the track reads as clearly
major. Tempo came back near-perfect in the same clip, so this is not a case of the prompt
being ignored wholesale — the tempo instruction survived and the mode instruction did not.

## What this means end to end

For any given place, Pleasantness reaches the listener's ear roughly:

> 45% (reaches the Pleasantness branch) × ~50% (mode survives generation) ≈ **23%**

So the honest statement is: **Pleasantness is wired to the prompt, not reliably to the
audio.** Describing it as controlling the music overstates what the evidence supports.

## Decision applied on 2026-09-20

Option 1 was selected: correct the wording without changing the scoring rule. `README.md`,
`about.html`, and `research/paper_draft.md` now describe mode and tempo as requested parameters
and state the measured 5/10 mode match. The remaining alternatives are retained below because
they would change scoring or need more paid generation evidence:

1. **Correct the wording only.** Say Pleasantness determines the key *requested* in the
   prompt, and that verification against real audio shows the request survives ~50% of the
   time. Cheapest, and immediately honest.
2. **Replace the median split with an absolute threshold or a spread-aware mapping.** The
   current rule cannot express "every region is fairly pleasant," which is what the data
   actually says. This changes keys for real places, so it needs a stated rationale in
   `about.html` §03 the way the weighting rationale already is.
3. **Widen what Pleasantness controls.** If mode is unreliable through Suno, Pleasantness
   could drive something the generator honours better — tempo survived at 0.2% error on the
   same clip. This is a design change, not a fix.
4. **Wait for the ablation experiment.** `research/prompt_ablation_experiment.py` is already
   testing why the mode request gets dropped, across three prompt conditions. If a phrasing
   reliably produces minor, option 1's "~50%" figure changes and options 2–3 may be moot.

Option 4 is in progress and independent of this analysis; this file deliberately does not
duplicate it. Nothing here touches any score, prompt, or audio mapping.
