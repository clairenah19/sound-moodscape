# Moodscape — 소리로 느끼는 한국

Moodscape is a data-sonification project asking one question: **can geographic and
demographic data be turned into music that lets a listener understand the character of a
place, without seeing a map?** It's an interactive map of all 17 South Korean
provinces/metros where every region and landmark has a computed "mood," and that mood
drives a real generated soundscape, a plain-language explanation of *why* it sounds that
way, and a keyboard-and-speech accessible way to explore the map without sight.

This README covers what's here and how to run it. For the research question, the scoring
formula, its sourcing, and an honest list of what's validated vs. proposed, see
**[`about.html`](about.html)** — that page is the actual methodology writeup and is kept
more current than this file for anything scientific. For what's built vs. what's next, see
**[`DEVELOPMENT_PLAN2.md`](DEVELOPMENT_PLAN2.md)**.

## Running it locally

No build step, no dependencies to install — it's a static site.

```bash
./start.command
```

or manually:

```bash
python3 -m http.server 8000
open http://localhost:8000/index.html
```

Two features are optional and need your own API key, entered in the app itself (never
committed to this repo): the "Ask a Local" chat and AI-generated music both use your own
Gemini/Suno key, stored only in your browser's `localStorage`. Everything else — the map,
region scores, real photos, and a synth soundscape — works with no setup.

## What's actually here

| Area | What it does | Where |
|---|---|---|
| **Region scoring** | A reproducible "Activity Proxy" computed from real official statistics (2025 population density, 2024 tourism trips, 2023 noise complaints/facilities, visitor crowding) for all 17 regions — weights are stated hypotheses, not fitted coefficients. A separate Visitor Pleasantness score is computed from satisfaction/recommend/revisit data. | `data.js` (`REGION_MODEL`), documented in `about.html` §03 |
| **Sonification** | Score → pitch (12-TET), tempo (BPM), timbre band, and — as of this plan cycle — musical key/mode, which now reads the region's Visitor Pleasantness relative to the national median instead of the place's own score. | `narrative.js`, `prompt.js` (`getMusicalKey`, `getSunoBpm`, `getSunoStyle`) |
| **Real audio** | Three-layer fallback: a pre-generated track (hosted URL or a local MP3 you drop in `audio/`), live generation via a paid third-party Suno API if you supply a key, or a Web Audio synth so the player is never silent. | `audio.js` |
| **Plain-language narrative** | A deterministic (no API key needed) explanation of exactly why each place/region sounds the way it does, read from the same functions that drive the audio. | `narrative.js` (`buildPlaceNarrative`, `buildProvinceNarrative`) |
| **"The music, without hearing it"** | A text-and-geometry panel for deaf/hard-of-hearing users, showing the same pitch/tempo/key/timbre/density parameters the synth reads. | `narrative.js` (`buildMusicSpecPanel`) |
| **Sound navigation (accessibility mode)** | All 17 provinces are real keyboard tab stops with `aria-label`s carrying region name, score, and mood label. One `aria-live="polite"` region announces changes without fighting a screen reader. A focused province plays its own score as a pitch. `prefers-reduced-motion` is honored throughout. | `map.js`, `audio.js`, `index.html` |
| **Hidden gem per province** | One place per region surfaced from an independent local/travel blog — not curated by the app — with the blog's own quote and a link back to the source. | `data.js` (`hiddenGem`), `ui.js` (`renderHiddenGem`) |
| **AI features (bring your own key)** | "Ask a Local" chat with a region-flavored persona; an AI music-style predictor that looks at a place's real photo plus its research data; a per-language accessibility estimate. All via Gemini. | `prompt.js` |
| **Multi-language interface** | 13 interface languages, plus a separately-estimated language-accessibility score per province per language. | `i18n.js` |

## Data & sources

Everything the live scoring formula reads is real, cited, official data — not scraped
reviews or invented numbers:

- `research/moodscape_15_regions_official_proxies.csv` — density, noise complaints/facilities (KOSIS, Ministry of Environment)
- `research/moodscape_2024_national_tourism_province_perception.csv` — satisfaction/recommend/revisit/crowding (National Tourism Survey)
- `research/moodscape_2024_jeju_visitor_survey_summary.csv` — supporting Jeju-specific context
- `research/moodscape_external_sources.csv` — every academic and government citation, with DOIs where they exist
- `research/2024_National_Tourism_Survey_*.pdf` — the underlying government reports

What's *not* yet real data: individual landmark scores are illustrative offsets from their
region's real score (flagged as such in the UI), and no primary soundscape field data has
been collected yet — see the next section.

## Validation status (read this before citing a score as "measured")

The region-level formula is **reproducible**, not **validated** — it hasn't been tested
against how people actually perceive these soundscapes. That's the single most important
caveat in this whole project, and it's stated plainly rather than glossed over:

- `research/soundscape_relationship_validation_protocol.md` — the actual ISO 12913 field
  study design (8-item questionnaire, site-time sampling, mixed-effects analysis plan) for
  testing whether the official-data proxy predicts real perceived Eventfulness.
- `research/soundwalk_observation_template.csv` — the data-entry structure for that study.
  **Currently empty** — no fieldwork has been done yet.
- `research/soundwalk_questionnaire_ko.md` — a Korean translation of the participant
  questionnaire, ready for a pilot (itself needs a proper back-translation pass before real
  use, per the protocol).
- `research/iso_pe_calculator.js` — a dependency-free implementation of ISO 12913's actual
  Pleasantness/Eventfulness formula, plus site-time aggregation and scatter-plot data
  shaping. Run `node research/iso_pe_calculator.js` for a worked example against clearly
  labeled example data — it has nothing to compute against yet, because no field data
  exists.

If you're evaluating this project (KSEF or otherwise): the honest one-line summary is
*"the inputs are measured, the weights are reasoned starting hypotheses, and the listening
study that would actually validate them hasn't been run."* `about.html` says this in more
detail; `DEVELOPMENT_PLAN2.md` Priority 1 is what closes that gap.

## Project structure

```
index.html          Map view (D3 + TopoJSON choropleth of the 17 regions)
about.html           Research writeup — question, method, sources, roadmap, limitations
data.js              All region/place data, REGION_MODEL scoring, hiddenGem entries
map.js               D3 map rendering + keyboard/screen-reader navigation
ui.js                Side-panel rendering for regions and places
audio.js             Playback (real tracks + Suno generation) and Web Audio tactile cues
narrative.js         Deterministic text explanations + the accessible music-spec panel
prompt.js            Suno prompt construction, Gemini calls (chat/prediction/language)
i18n.js              Interface translations
geojson.js           South Korea province boundary data
research/            Source CSVs/PDFs, validation protocol, ISO calculator, questionnaire
out/Log.md           Dated development log entries
DEVELOPMENT_PLAN2.md Consolidated, prioritized view of done vs. next
```

## What this is not (yet)

- Not a validated scientific instrument — see "Validation status" above.
- Not a trained or fitted model — every weight in the scoring formula is a stated design
  judgment, not a learned coefficient.
- Not a hidden-gem *discovery* engine — the one hidden gem per province is a fixed, sourced
  pick, not an algorithm that finds new ones.
- The AI features (chat, music-style prediction, language estimate) require your own API
  key and have not been exhaustively tested against a live key in every region.

## License / attribution

No license file is currently included — treat this as all-rights-reserved by default until
one is added. Real photos are Wikimedia Commons images with per-photo artist/license
credit shown in the app. Hidden-gem entries link back to and credit their original blog
source; that content is quoted under fair-use-scale excerpt, not reproduced in full.
