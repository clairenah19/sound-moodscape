// ── ISO 12913 PLEASANTNESS / EVENTFULNESS CALCULATOR ─────────────────────────
//
// Implements the exact projection formula from
// research/soundscape_relationship_validation_protocol.md (§ "Outcome
// calculation"), which is itself ISO/TS 12913-3's standard method for turning
// the 8-item perceptual questionnaire into two circumplex coordinates.
//
// This is a "preparable now" item from DEVELOPMENT_PLAN.md Priority 1: the
// math, aggregation, and scatter-plot data shaping can all be built and
// tested before a single real soundwalk observation exists. It is deliberately
// dependency-free (no build step, no framework) so it can run in Node for
// analysis or be <script>-included in a browser page.
//
// IMPORTANT: nothing in this file is wired into the live Moodscape app or its
// scores. It exists to process real field data collected against
// soundwalk_observation_template.csv — until that data exists, calling this
// with real rows is not possible, only with the clearly-labeled example rows
// in runExample() below.

const COS45 = Math.SQRT1_2; // cos(45°) = √2/2 ≈ 0.7071
const NORM = 4 + Math.sqrt(32); // the protocol's fixed denominator

/**
 * Compute ISO Pleasantness and Eventfulness for one participant's 8 ratings.
 * Each rating is a 1–5 Likert value, matching the *_1_5 columns in
 * soundwalk_observation_template.csv.
 *
 * @param {{pleasant:number, annoying:number, calm:number, chaotic:number,
 *          vibrant:number, monotonous:number, eventful:number, uneventful:number}} r
 * @returns {{pleasantness:number, eventfulness:number}} each in roughly [-1, 1]
 */
function isoCoordinates(r) {
  const required = ["pleasant", "annoying", "calm", "chaotic", "vibrant", "monotonous", "eventful", "uneventful"];
  for (const key of required) {
    if (typeof r[key] !== "number" || r[key] < 1 || r[key] > 5) {
      throw new Error(`isoCoordinates: "${key}" must be a 1–5 rating, got ${r[key]}`);
    }
  }
  const pleasantness = ((r.pleasant - r.annoying) + COS45 * (r.calm - r.chaotic) + COS45 * (r.vibrant - r.monotonous)) / NORM;
  const eventfulness = ((r.eventful - r.uneventful) + COS45 * (r.chaotic - r.calm) + COS45 * (r.vibrant - r.monotonous)) / NORM;
  return { pleasantness, eventfulness };
}

/**
 * Aggregate participant-level ISO coordinates into one site-time observation:
 * mean and a 95% CI (normal approximation — fine for the ≥10-rating pilot
 * size the protocol calls for; swap for a t-interval if n per cell is small).
 *
 * @param {Array<{pleasant:number, annoying:number, calm:number, chaotic:number,
 *                 vibrant:number, monotonous:number, eventful:number, uneventful:number}>} ratings
 *        one entry per participant, same site + time window
 * @returns {{n:number, pleasantness:{mean:number, ci95:[number,number]},
 *            eventfulness:{mean:number, ci95:[number,number]}}}
 */
function aggregateSiteTime(ratings) {
  if (!ratings.length) throw new Error("aggregateSiteTime: no ratings given");
  const coords = ratings.map(isoCoordinates);
  const summarize = (values) => {
    const n = values.length;
    const mean = values.reduce((a, b) => a + b, 0) / n;
    const variance = n > 1 ? values.reduce((a, b) => a + (b - mean) ** 2, 0) / (n - 1) : 0;
    const se = Math.sqrt(variance / n);
    const margin = 1.96 * se; // normal approximation
    return { mean, ci95: [mean - margin, mean + margin] };
  };
  return {
    n: ratings.length,
    pleasantness: summarize(coords.map((c) => c.pleasantness)),
    eventfulness: summarize(coords.map((c) => c.eventfulness)),
  };
}

/**
 * Shape a set of site-time observations into {x, y, label} points ready for
 * a scatter plot — x = a chosen predictor (e.g. LAeq, pedestrians/min, or
 * Moodscape's own province-level Activity Proxy joined in afterward per the
 * protocol's "may be joined afterward" rule), y = Eventfulness mean.
 * Deliberately just data shaping, not a charting library — plug into
 * whatever renders scatter points (SVG, Canvas, D3) at analysis time.
 *
 * @param {Array<{siteLabel:string, predictorValue:number, ratings:Array}>} observations
 * @returns {Array<{x:number, y:number, yLow:number, yHigh:number, label:string, n:number}>}
 */
function eventfulnessScatterData(observations) {
  return observations.map((obs) => {
    const agg = aggregateSiteTime(obs.ratings);
    return {
      x: obs.predictorValue,
      y: agg.eventfulness.mean,
      yLow: agg.eventfulness.ci95[0],
      yHigh: agg.eventfulness.ci95[1],
      label: obs.siteLabel,
      n: agg.n,
    };
  });
}

// ── Self-test with clearly labeled EXAMPLE data (not real observations) ─────
// Demonstrates the functions work end-to-end. Run with: node iso_pe_calculator.js
function runExample() {
  console.log("EXAMPLE ONLY — not real soundwalk data. For structure-testing purposes.\n");

  const exampleParticipant = {
    pleasant: 4, annoying: 2, calm: 3, chaotic: 3,
    vibrant: 4, monotonous: 2, eventful: 4, uneventful: 2,
  };
  console.log("Single participant:", isoCoordinates(exampleParticipant));

  const exampleSiteRatings = [
    { pleasant: 4, annoying: 2, calm: 3, chaotic: 3, vibrant: 4, monotonous: 2, eventful: 4, uneventful: 2 },
    { pleasant: 3, annoying: 2, calm: 3, chaotic: 3, vibrant: 3, monotonous: 3, eventful: 3, uneventful: 3 },
    { pleasant: 4, annoying: 1, calm: 4, chaotic: 2, vibrant: 3, monotonous: 2, eventful: 3, uneventful: 2 },
  ];
  console.log("\nExample site-time aggregate (n=3, below the protocol's ~10-rating target):", aggregateSiteTime(exampleSiteRatings));

  const exampleObservations = [
    { siteLabel: "Example commercial street, weekday", predictorValue: 68.4, ratings: exampleSiteRatings },
    { siteLabel: "Example residential street, weekend", predictorValue: 52.1, ratings: exampleSiteRatings },
  ];
  console.log("\nExample scatter data (predictorValue would be real LAeq/pedestrian counts):", eventfulnessScatterData(exampleObservations));
}

if (typeof require !== "undefined" && require.main === module) {
  runExample();
}

if (typeof module !== "undefined") {
  module.exports = { isoCoordinates, aggregateSiteTime, eventfulnessScatterData };
}
