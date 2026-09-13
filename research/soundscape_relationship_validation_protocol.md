# Moodscape proxy-to-Eventfulness validation protocol

## Research question

Do measured contextual indicators (population density, crowd density, traffic and human activity, acoustic level, land use, noise complaints, and visitor crowding perception) predict ISO 12913 Pleasantness and Eventfulness at South Korean locations?

The outcome is the ISO score reported by participants at a site and time. Province-level administrative data is contextual evidence and must not be treated as the outcome.

## Published basis for testing the relationship

- Hong and Jeon (2020), Seoul: on eight urban streets, traffic noise increased Eventfulness and decreased Pleasantness; human activity sounds increased both; crowd density was a critical predictor in commercial streets. DOI: 10.1016/j.buildenv.2020.107327.
- De Coensel et al. (2026), Flanders: 3,757 in-situ evaluations showed road density and anthropogenic activity were associated with higher Eventfulness, but geospatial variables explained only 9.6% of Eventfulness variance. Perceived sound sources predicted substantially better. DOI: 10.1016/j.buildenv.2026.114445.
- International Soundscape Database v1.0: an open reference dataset combining ISO questionnaires, acoustics, and contextual information. https://zenodo.org/records/10672568.
- ISO/TS 12913-2 defines in-situ data collection; ISO/TS 12913-3 defines analysis. The current analysis edition is ISO/TS 12913-3:2025.

These findings justify a hypothesis; they do not prove that province-level density or complaints predict Korean regional Eventfulness.

## Required observations

Collect at least 30 distinct sites across 6-10 provinces for a pilot, including:

- commercial street
- central business street
- residential street
- park or natural area
- transport area
- market, heritage, or tourism area
- industrial edge where safe and publicly accessible

Collect at least two time windows per site (for example weekday daytime and evening/weekend). Aim for at least 10 independent participant ratings per site-time observation. Record the same acoustic and contextual predictors during the exact rating period.

## Participant questionnaire

Ask: "To what extent do you agree or disagree that the present surrounding sound environment is ..."

Use the same five-point response scale for all eight attributes:

1. pleasant
2. chaotic
3. vibrant
4. uneventful
5. calm
6. annoying
7. eventful
8. monotonous

Also record perceived dominance of traffic, other mechanical, human, and natural sounds; overall appropriateness; age band; hearing difficulty; resident/visitor status; and familiarity with the place. Do not collect names in the analysis file.

Use a validated Korean translation or run translation/back-translation and a pilot before field deployment. Attribute order should be fixed to the selected standardized instrument and documented.

## Outcome calculation

Let p = pleasant, a = annoying, ca = calm, ch = chaotic, v = vibrant, m = monotonous, e = eventful, and u = uneventful.

```text
ISO Pleasantness = [(p-a) + cos(45 degrees)*(ca-ch) + cos(45 degrees)*(v-m)] / (4+sqrt(32))
ISO Eventfulness = [(e-u) + cos(45 degrees)*(ch-ca) + cos(45 degrees)*(v-m)] / (4+sqrt(32))
```

The normalized coordinates range approximately from -1 to +1. Preserve the original eight ratings as well as the calculated coordinates.

## Predictors collected at the same site and time

Required:

- LAeq over the rating interval using a calibrated or documented measurement device
- counted pedestrians per minute
- counted vehicles per minute
- perceived dominance of traffic, human, mechanical, and natural sounds
- land-use category
- latitude and longitude
- date, start time, duration, temperature, rain, and wind condition
- weekday/weekend and ordinary-day/festival status

Recommended:

- LCequivalent, loudness, roughness, sharpness, and fluctuation strength
- percentage vegetation within a declared buffer
- road length/density within the same buffer
- points of interest by type
- number and diversity of discrete sound events

Province-level predictors already collected by Moodscape (density, complaints, facilities, tourism and crowding satisfaction) may be joined afterward. They must not replace the site-time measurements.

## Analysis

1. Calculate participant-level ISO Pleasantness and Eventfulness.
2. Estimate site-time means and 95% confidence intervals.
3. Plot every predictor against Eventfulness before fitting a model.
4. Fit a mixed-effects model with participant and site as grouping effects. Keep Pleasantness and Eventfulness separate.
5. Compare a site-time model against a model that also includes province-level proxies.
6. Hold out complete sites or provinces for testing; never randomly split individual ratings from the same site across training and test sets.
7. Report coefficients, confidence intervals, cross-validated RMSE, R-squared, residual diagnostics, and multicollinearity checks.
8. Run sensitivity analysis with and without density, complaints, and each sound-source group.
9. Treat a relationship as supported only if its direction is stable, its confidence interval excludes zero, and it improves out-of-site prediction.

With two labelled provinces, province-level regression is invalid. The unit of analysis for the pilot should be the site-time observation, not the province.

## Decision rule for Moodscape

- If contextual proxies do not improve held-out prediction, do not use them to generate Eventfulness.
- If site-time acoustic and perceived-source variables predict Eventfulness, use those variables at places where they are available.
- Province scores should be reported as a distribution or weighted site summary with uncertainty, not as an unsupported single truth.
- A separate listener experiment is required to test whether Moodscape's generated music communicates the validated scores.

