# Landmark Wikipedia readership proxy

Status: implemented separately from the soundscape score. The first snapshot covers **2025-09-01 through 2026-08-31**, the last 12 complete calendar months as of 2026-09-13.

## Reproduce

```sh
node research/export_landmarks.js > research/landmark_inventory.json
python3 research/fetch_landmark_pageviews.py --start 2025-09-01 --end 2026-08-31
```

Python uses only the standard library. Set `WIKIMEDIA_USER_AGENT` to a descriptive contactable user agent for your deployment. The default identifies this project's public repository. Cached API responses retain their original retrieval timestamps; use `--refresh` to fetch again. The CSV and JSON are produced in the same run. The app reads the JSON over HTTP and offers the CSV for download.

## Source and denominator

[Wikimedia Analytics API pageview documentation](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/reference/page-views.html) defines the endpoint:

`https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/user/{article}/monthly/{start}/{end}`

The cohort uses English Wikipedia only, all access devices, and the `user` agent category to exclude the API's automated-agent categories. Views are not unique visitors, physical footfall, noise, or perceived Eventfulness. Monthly counts are summed; average monthly views use the available month count. Only a complete common observation window receives a normalized offset. Do not compare windows or languages without recalculating the full cohort.

## Mapping

For every complete article record, let `v = average monthly views`. Then:

`popularity_offset_0_100 = 100 × (log1p(v) − min(log1p(v))) / (max(log1p(v)) − min(log1p(v)))`.

Min/max are calculated over complete records in this snapshot. A constant cohort receives the neutral value 50 because it contains no ranking information. A measured zero is valid; missing, partial, and request-error records have a blank offset. A score of 100 means the highest readership **in this cohort**, not universal maximum popularity. “Offset” is the requested display name for this 0–100 comparison index; it is not a signed adjustment or an addition to the mood score.

## Article scope and missingness

The initial mapping extracts existing English Wikipedia `photoPage` titles. Some titles describe broader cities, districts, or companies (for example Samsung for Samsung Digital City). Those rows are explicitly described as linked-article proxies, not landmark-specific counts. A Commons photo page is not a Wikipedia article and cannot supply Wikipedia readership. All 75 places receive a CSV row, even when no article can be used. Redirects/title changes can cause partial coverage; the script does not invent zero counts for absent months or silently combine distinct articles.

If mappings are later reviewed, add an explicit `landmark_wikipedia_overrides.json` keyed by `state__place`, with `title` and `scope`, and preserve the change in source control. Shared article titles can produce identical proxy scores for different landmarks and must not be treated as independent popularity observations.

## UI and fieldwork

The landmark panel shows the existing illustrative score and its effective difference from the region baseline beside the popularity offset, article, period, and coverage. Neither the mood score nor its musical parameters are changed. `measured: false` remains on every landmark. During Priority 1, collect actual observations for 3–5 exact featured landmarks; only then attach source observation IDs, dates, questionnaire/acoustic details and uncertainty, and mark those supported records `measured: true`. A readership record never qualifies for that flag.

No real landmark field measurements were produced by this script.
