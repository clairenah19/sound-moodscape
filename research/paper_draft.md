# Moodscape: Exploring Regional Character Through Geographic Sonification

Draft dated 2026-09-13. Author(s), affiliation, corresponding author: [PENDING].

## Abstract

Moodscape is an interactive prototype that translates a composite of regional statistics and authored landmark characteristics into musical specifications for South Korean places. It combines a map of 17 provincial-level regions and 75 featured places with explanations of the scoring model, music-generation prompts, optional generated-track playback, and alternative textual and auditory navigation. An Activity Proxy combines density, tourism intensity, noise complaints, noise-emitting facilities, and crowding pressure. A separate visitor-satisfaction composite informs musical mode, subject to contextual overrides. Landmark Wikipedia readership is displayed independently as a popularity proxy. The proposed evaluation separates two questions: whether regional/contextual indicators correspond to in-situ soundscape perception, and whether listeners perceive the ordering encoded in generated music. **Results: [PENDING].** The current contribution is an inspectable prototype and a prepared evaluation workflow; perceptual validity and accessibility effectiveness have not been established.

## 1. Introduction

Geographic interfaces usually communicate differences between places through maps, labels and visual scales. Moodscape asks whether a musical representation can communicate aspects of regional activity and place character, including when the map is not visible. The project combines data representation with cultural interpretation: a heritage site and a contemporary entertainment district may warrant different musical styles even when they share a region.

The central question is: can geographic and demographic/contextual data be converted into music that helps a listener interpret a place's character? We operationalize a narrower initial claim—perceived activity ordering—rather than assuming that safety, language accessibility or climatic conditions can all be inferred from one composite sound.

This draft distinguishes (a) measured administrative/survey inputs, (b) a model built with hypothesized weights, (c) illustrative landmark offsets, (d) musical representations, and (e) participant observations that have not yet been collected. These are separate evidence levels.

## 2. Background and related work

The project situates itself in geographic sonification and accessible data exploration. The existing About page discusses iSonic as a precedent for coordinated geographic sound and speech, and NASA's sonification work as an example of translating otherwise inaccessible data patterns into sound. These precedents motivate a design direction; they do not establish Moodscape's effectiveness.

Soundscape research separates Pleasantness and Eventfulness rather than treating all atmosphere as a single good-to-bad scale. Moodscape's field protocol adopts that distinction. Its present Activity Proxy and visitor-satisfaction composite are not measured ISO coordinates, and applying soundscape adjectives to generated music is an adaptation requiring its own validation.

The repository contains a related-work survey and source catalogue. Before submission, verify each bibliographic entry against its primary publication, including author list, title, year, DOI and the precise claim it supports. Do not carry over an unverified claim of research novelty from the website.

## 3. System and data

The browser-based system uses static HTML/CSS/JavaScript, local geographic boundaries and D3 for map interaction. Region and landmark panels expose scores, narratives, photos and musical specifications. Optional Gemini requests support conversational personas, music-style suggestions and language-accessibility estimates. Optional Suno-compatible generation produces music from place-specific prompts. These integrations are tools in the prototype, not trained Moodscape models.

The regional model uses bundled statistics described by the project as 2025 population density, 2024 domestic-tourism volume and visitor survey measures, and 2023 noise complaints/facilities. Values are recomputed from the bundled inputs on load, not refreshed from government APIs in real time. Source CSVs and the in-code 17-region table require a final provenance reconciliation before submission; some earlier source files contain only 15 regions.

The current landmark dataset has 75 entries. Its authored differences from regional baseline are preserved when regional scores are recalculated and clipped to [0,1]. These are labelled illustrative. Every landmark remains `measured: false` until linked field observations justify changing that status.

Wikipedia pageviews add a separate, reproducible readership measure. The script queries English Wikipedia over a fixed common period, retains missing and partial records, and creates a log-scaled popularity index only for complete records. The interface displays this beside the existing score. Related city/company articles are not represented as direct landmark readership, and popularity does not silently alter the music.

## 4. Computational method

### 4.1 Regional Activity Proxy

Each input is transformed with `log1p` and min–max scaled across the 17 regions. The activity score is:

`100 × (0.35 density + 0.30 tourism intensity + 0.15 complaints + 0.10 facilities + 0.10 crowding pressure)`.

Tourism intensity is trips per resident; complaints and facilities are per 100,000 residents; crowding pressure is 100 minus crowding satisfaction. The weights are explicit design hypotheses, not fitted coefficients. The rationale is documented, but must not be described as an empirically optimized model.

### 4.2 Visitor Pleasantness context

`0.40 overall satisfaction + 0.25 recommendation + 0.20 revisit intention + 0.15 crowding satisfaction`.

This visitor-survey composite remains distinct from acoustic Pleasantness. For places without category overrides, values at or above the regional median select major mode; below-median values select minor. Solemn sites and heritage/nature categories have separate rules. Gangnam is a pending real-track check of the below-median case; a minor-key prompt is not proof of a minor-key recording.

### 4.3 Musical representation

The specification maps activity to a chromatic pitch range of 440–880 Hz and a tempo of `round(42 + 110 × score)` BPM. Genre, instrumentation and major/minor rules incorporate place context. Written narratives expose these intended mappings. Generated models can depart from a prompt, so actual clip tempo and mode require checking. The current code does not provide a full automatic synth fallback when no music file or API result exists; navigation tones are a separate Web Audio feature.

### 4.4 Wikipedia popularity

The popularity offset is the min–max scaled `log1p` of average monthly readership over complete records, on a 0–100 scale. Its observation period, article title/scope, coverage and source URL are exported to CSV. The index measures relative online attention in a particular language and cohort. It is not a soundscape measurement or signed addition to the activity score.

## 5. Research and implementation process

The existing project describes six stages: literature search, framework selection, regional data compilation, evidence fusion, narrative synthesis and interface integration. This describes a development process, not a validation result. Earlier estimated/sourced regional labels are retained as history; they do not replace the current official-input composite.

The present implementation pass adds a reproducible landmark readership collector, a separate evidence panel, a blinded static listening form, stimulus preparation and correlation-analysis scripts, and study preparation documents. Recruitment, fieldwork, live-key verification and real musical judgments must be reported separately from software completion.

## 6. Evaluation design

### 6.1 Field validation

Follow `soundscape_relationship_validation_protocol.md`: sample locations and time windows, collect eight perceptual attributes with contemporaneous acoustic/contextual measures, aggregate by site-time, and compare predictors with appropriately grouped/held-out analyses. Include 3–5 actual featured landmarks so measured evidence can be attached to those exact places. The broad protocol and smaller feasibility plan currently describe different sample targets; reconcile and freeze the chosen pilot design before data collection.

### 6.2 Listener experiment

The prepared protocol uses ten real generated clips spanning the observed score range, with identical 25-second extraction and loudness treatment. The participant interface conceals names and scores, randomizes order, requires complete playback and eight ratings, and exports pseudonymous CSV rows. Target 24 complete adults; a cohort of at least 15 may be reported as exploratory, without a claim of sufficient power.

The prespecified primary analysis correlates ten clip-mean rated Eventfulness values with generating scores using Spearman rho and a two-sided clip-label permutation test. Participants are repeated raters; participant-by-clip rows are not independent stimuli. Participant-bootstrap intervals condition on the fixed stimulus set. A positive result would support this encoding on these clips, not geographic truth or causality.

### 6.3 Accessibility evaluation

Participation by blind or low-vision users is unlikely to be available for the current study. Intended-user accessibility evaluation is therefore outside the current evaluation scope and retained as future work. The prepared brief concerns task performance, assistive-technology conflicts and verbosity preferences if later recruitment becomes feasible. Full-stat readouts, stereo longitude mapping and cardinal navigation remain deferred. Development-team keyboard or screen-reader checks can document technical behavior, but do not establish accessibility effectiveness or usability for intended users.

## 7. Results

**[PENDING]**

Priority 1 has not produced real field observations. No measured landmark results, listener correlations, accessibility findings or audibly verified Gangnam mode result are reported here. Software fixture tests are not participant data. Populate this section only after real observations exist, retaining negative findings and exclusions.

## 8. Discussion and limitations

The design makes an interpretation inspectable, but administrative density, tourist attention, noise complaints and perceived activity are not interchangeable. Regional averages conceal local and temporal variation. Authored landmark offsets, narrow satisfaction ranges, hand-set weights, language-dependent Wikipedia readership, broad linked articles and category-based musical stereotypes can bias representations. Score clipping can compress calm landmarks toward zero.

Generated music introduces another layer of uncertainty: instrumentation or mode may not follow instructions, and pre-existing tracks may no longer correspond to updated scores. The current documentation contains older scoring and fallback descriptions that require reconciliation. Some browser controls remain less accessible than the map itself. AI personas are not real residents, language-accessibility scores are estimates, and live external-service reliability has not been established in this pass.

Without blind/low-vision participants, this study cannot establish that Moodscape supports independent exploration or meets the needs of those users. General-listener ratings concern perception of musical encoding, not accessibility validation. Testing sighted people with their eyes closed or blindfolded would not resolve this limitation.

The planned evaluation can separate failure of the geographic model from failure of the musical encoding. Both should be reported even if results contradict the intended design.

## 9. Future work

Complete field observations and listener recruitment, verify generated stimuli, and evaluate accessibility with intended users. Only after those results should the project consider revised weights, measured landmark replacements, new audio navigation, weather-driven parameters or model-generated narrative wording. Preserve versioned datasets and prompt/clip provenance so changes remain reproducible.

## References — verification pending before submission

- Zhao, Plaisant, Shneiderman & Lazar (2008), *Data Sonification for Users with Visual Impairment*, ACM TOCHI. DOI as recorded in the project: 10.1145/1352782.1352786.
- ISO 12913 series; edition and adapted-instrument claims must be checked against the field protocol and original standard.
- Hong & Jeon (2020), soundwalk research; DOI recorded in the project: 10.1016/j.buildenv.2020.107327.
- NASA Chandra (2022), Perseus sonification, as discussed in `about.html` §08.
- Wikimedia, [Analytics API: page views](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/reference/page-views.html), documentation consulted for the implemented collector.
- Official Korean statistical/survey sources and additional literature: `moodscape_external_sources.csv`; reconcile each used value to source table before publication.

## Appendix: website-to-paper mapping

| Website section | Draft sections |
|---|---|
| §01 Research question | Abstract; 1 Introduction |
| §02 Why sonification | 1 Introduction; 2 Background |
| §08 Related work | 2 Background; References |
| §03 Algorithm | 3 System/data; 4 Computational method |
| §05 Pipeline | 5 Research process |
| §06 Roadmap | 6 Evaluation design; 9 Future work |
| §07 Improvements | 6.3 Accessibility; 8 Limitations |

Results are deliberately not inferred from any website section.
