// ── VIBE NARRATIVE ───────────────────────────────────────────────────────────
// Plain-language "why does it sound like this?" text, generated instantly from
// data already on the page (no API key, unlike the Gemini-backed features).
// Purpose: make the data→music link legible — pitch/tempo/key/timbre aren't
// arbitrary, they're read straight off each place's mood score and character.

const CHROMATIC_NOTES = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"];

function noteForScore(score) {
  const semitones = Math.round(Math.max(0, Math.min(1, score)) * 12);
  const name = CHROMATIC_NOTES[semitones % 12];
  const octave = 4 + Math.floor(semitones / 12);
  const freq = Math.round(440 * Math.pow(2, semitones / 12));
  return { name: `${name}${octave}`, freq };
}

function timbreBand(score) {
  const pct = score * 100;
  if (pct <= 35) return { label: "traditional acoustic", detail: "gayageum, daegeum, haegeum — instruments with centuries of history behind them" };
  if (pct <= 65) return { label: "ambient-electronic hybrid", detail: "acoustic tones blended with soft synthesizer pads" };
  return { label: "synth-forward", detail: "electric bass and digital beats" };
}

// Same real-world category buckets prompt.js uses for style/key decisions —
// kept separate (small duplication, matches this file's existing pattern in
// getMusicalKey/getSunoStyle) so this module can't be broken by tweaks there.
function classifyPlaceCategory(place) {
  const name = (place.name || "").toLowerCase();
  const type = (place.type || "").toLowerCase();

  if (name.includes("cemetery") || type.includes("cemetery") || name.includes("memorial") ||
      type.includes("memorial") || name.includes("5.18") || name.includes("dmz") ||
      type.includes("observatory") || name.includes("observatory")) {
    return { key: "solemn", phrase: "a solemn, memorial-weighted site" };
  }
  if (type.includes("hanok") || type.includes("traditional") || type.includes("folk") ||
      type.includes("temple") || type.includes("palace") || name.includes("hanok") ||
      name.includes("temple") || name.includes("palace") || name.includes("village")) {
    return { key: "traditional", phrase: "a traditional, heritage-rooted place" };
  }
  if (type.includes("park") || type.includes("beach") || type.includes("lake") ||
      type.includes("island") || type.includes("nature") || type.includes("valley") ||
      type.includes("garden") || name.includes("mountain") || name.includes("beach")) {
    return { key: "nature", phrase: "a nature or scenic escape" };
  }
  if (type.includes("plant") || type.includes("factory") || type.includes("tech") ||
      type.includes("science") || type.includes("complex") || type.includes("industrial")) {
    return { key: "industrial", phrase: "an industrial or high-tech hub" };
  }
  return { key: "urban", phrase: "an everyday urban space" };
}

function keyReason(category, score) {
  if (category.key === "solemn") return "the site's solemn, memorial character pulls it into a minor key regardless of score";
  if (category.key === "traditional" || category.key === "nature") return "traditional and scenic places default to a major key here, since Moodscape treats heritage and nature as warm rather than tense";
  return score > 0.45 ? "at this score, the mapping defaults to a major key" : "at this score, the mapping defaults to a minor key";
}

// Deterministic pick from a string, so the same place always gets the same
// phrasing (no flicker on re-render) but different places read differently.
function pickVariant(seed, options) {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  return options[h % options.length];
}

function buildPlaceNarrative(place, stateName) {
  const pct = Math.round(place.score * 100);
  const label = MOOD_LABEL(place.score);
  const note = noteForScore(place.score);
  const bpm = getSunoBpm(place);
  const key = getMusicalKey(place);
  const timbre = timbreBand(place.score);
  const category = classifyPlaceCategory(place);

  const openers = [
    `${place.name} is ${category.phrase} — ${place.character}.`,
    `Start with what ${place.name} actually is: ${category.phrase}, ${place.character}.`,
  ];
  const opener = pickVariant(place.name, openers);

  const scoreLine = `That real-world character earns it a mood score of ${pct}/100 (${label.toLowerCase()}) on Moodscape's peaceful-to-exciting scale.`;

  const soundLine = `Fed through the sonification formula, that score becomes ${note.name} (${note.freq} Hz) at ${bpm} BPM in a ${key}, drawn from a ${timbre.label} palette — ${timbre.detail}.`;

  const whyLine = `The key lands on ${key.split(" ")[0]} because ${keyReason(category, place.score)}, and the instrumentation you'll hear — ${place.instrumentation} — reflects both that same score band and ${place.name}'s specific character rather than a generic template.`;

  return `${opener} ${scoreLine} ${soundLine} ${whyLine}`;
}

function buildProvinceNarrative(stateName) {
  const s = MOOD_DATA.states[stateName];
  if (!s || !s.places || !s.places.length) return "";
  const pct = Math.round(s.score * 100);
  const label = MOOD_LABEL(s.score);
  let min = s.places[0], max = s.places[0];
  s.places.forEach(p => {
    if (p.score < min.score) min = p;
    if (p.score > max.score) max = p;
  });
  const spread = max.score - min.score;
  const spreadLine = spread > 0.15
    ? `Its featured places range widely — from ${min.name} (${MOOD_LABEL(min.score).toLowerCase()}, ${Math.round(min.score * 100)}/100) up to ${max.name} (${MOOD_LABEL(max.score).toLowerCase()}, ${Math.round(max.score * 100)}/100) — so the soundscape shifts a lot depending which one you open.`
    : `Its featured places stay fairly close together in tone, from ${min.name} to ${max.name}, so the soundscape holds a fairly consistent character across the province.`;
  return `${stateName}'s overall mood score is ${pct}/100 — ${label.toLowerCase()}. ${s.desc}. ${spreadLine} Click into any place below to hear exactly how its own score reshapes the pitch, tempo, key, and instrumentation.`;
}
