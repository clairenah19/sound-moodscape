# Soundwalk pilot — results

**Status: [PENDING] — no field observations collected yet.**

This file is a scaffold, not a result. Nothing below is filled in, and none of it should
be treated as a finding until it is. The pipeline that produces these numbers is built
and tested; only the fieldwork is outstanding.

Fill this in by running:

```sh
python3 research/analyze_soundwalk.py
python3 research/analyze_soundwalk.py --predictor pedestrians_per_minute
python3 research/analyze_soundwalk.py --predictor vehicles_per_minute
```

---

## 1. What was collected

| | |
|---|---|
| Provinces | _[ ]_ |
| Sites | _[ ] of the protocol's 6–10 target_ |
| Site types covered | _[commercial / residential / park / transit / market-heritage / …]_ |
| Time windows per site | _[ ]_ |
| Participants per site-time | _[ ] (protocol target ~10; pilot minimum 5)_ |
| Total participant rows | _[ ]_ |
| Dates | _[ ]_ |
| LAeq instrument / app | _[name and version — the protocol requires this be documented]_ |

Rows rejected at analysis, and why: _[paste the script's "skipped" lines, or "none"]_

## 2. Site-time results

_Paste the table from `analyze_soundwalk.py` here._

```
[site    date    time    n    Pleasant   95% CI    Eventful   95% CI    laeq_db]
```

## 3. Predictor vs Eventfulness

The protocol requires plotting every predictor against Eventfulness **before** fitting any
model. Record what the scatter actually looks like, in words, before computing anything.

| Predictor | Direction | Looks like |
|---|---|---|
| `laeq_db` | _[rises / falls / flat / no pattern]_ | _[ ]_ |
| `pedestrians_per_minute` | _[ ]_ | _[ ]_ |
| `vehicles_per_minute` | _[ ]_ | _[ ]_ |

## 4. Comparison with Moodscape's own Activity Proxy

Per the protocol, province-level proxies may be joined **afterward** and must not replace
the site-time measurements. For each site, record the measured Eventfulness beside the
province's modelled Activity Proxy from `REGION_MODEL` in `data.js`.

| Site | Measured Eventfulness | Province Activity Proxy | Agrees? |
|---|---|---|---|
| _[ ]_ | _[ ]_ | _[ ]_ | _[ ]_ |

## 5. Decision rule — state the answer in writing

The protocol's rule, quoted so it cannot be quietly skipped:

> If contextual proxies do not improve held-out prediction, do not use them to generate
> Eventfulness.

**Did the official-data proxy predict measured Eventfulness better than chance?**

_[ YES / NO / NOT ENOUGH DATA — and the reasoning. A "no" is a legitimate result and must
be reported as one. It would mean the province-level Activity Proxy, however reproducible,
is not evidence about how a place actually sounds, and the app should keep labelling it a
proxy rather than a measurement. ]_

## 6. Limitations to carry into the paper

These apply regardless of what the numbers say, and are known in advance:

- **Sample size.** A pilot of this size cannot support the protocol's mixed-effects model
  with participant and site grouping, nor held-out validation by site. Treat every number
  here as descriptive, not inferential.
- **Unit of analysis.** The site-time observation, never the province. With one or two
  provinces, province-level regression is invalid.
- **The questionnaire is not a validated instrument.** `soundwalk_questionnaire_ko.md` is a
  working translation; the protocol requires back-translation and a pilot before it counts
  as validated. In particular, whether 단조롭다 (monotonous) and 지루하다 (uneventful) stay
  distinct for Korean speakers is untested.
- **Convenience sample.** Participants approached at the site are not representative of
  residents, visitors, or the population.
- **Single observer.** Pedestrian and vehicle counts were made by one person without a
  reliability check.
- _[add anything that actually went wrong in the field — weather, refusals, a broken meter,
  a site that turned out to be a construction zone. These belong in the record.]_

## 7. What this does and does not license

- It does **not** license setting `measured: true` on any landmark in `data.js` unless that
  specific landmark was itself observed.
- It does **not** license changing any live score. Scores stay as they are until a result
  supports changing them.
- It **does** license replacing `[PENDING]` in `research/paper_draft.md` §Results with the
  actual finding — including a null one.
