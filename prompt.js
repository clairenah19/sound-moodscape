// ── MOOD SCAPE SUNO PROMPTS & CONFIG ─────────────────────────────────────────

window.SUNO_TRACKS = window.SUNO_TRACKS || {};

function slugify(s) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

function placeKey(stateName, place) {
  return slugify(stateName) + "__" + slugify(place.name);
}

const PLACE_TERMS = {
  keySolemn: { name: ["cemetery", "memorial", "5.18", "observatory", "dmz", "cave", "tomb", "dolmen", "taejongdae"], type: ["cemetery", "memorial", "observatory", "cave"], character: ["dmz"] },
  keyMajor: { name: ["hanok", "temple", "palace", "village"], type: ["hanok", "traditional", "folk", "temple", "palace", "ruins", "park", "beach", "lake", "island", "nature", "valley", "garden", "arboretum", "springs"] },
  styleSolemn: { name: ["cemetery", "memorial", "5.18", "observatory", "dmz"], type: ["cemetery", "memorial", "observatory"] },
  traditional: { name: ["hanok", "temple", "palace", "village"], type: ["hanok", "traditional", "folk", "temple", "palace", "ruins"] },
  nature: { name: ["mountain", "beach", "lake", "cave"], type: ["park", "beach", "lake", "island", "nature", "valley", "garden", "arboretum", "cape", "cliff", "cave"] },
  industrial: { name: ["hynix", "posco", "hyundai", "kia"], type: ["plant", "factory", "shipyard", "tech", "science", "complex", "research", "fabrication", "industrial"] },
  urban: { name: ["hongdae", "gangnam", "biff", "plaza", "market"], type: ["district", "youth", "hub", "center", "cinema", "plaza", "amusement", "pier", "market", "shopping", "design", "quarter"] }
};

function matchesPlace(place, termsByField) {
  return Object.entries(termsByField).some(([field, terms]) =>
    terms.some(term => String(place[field] || "").toLowerCase().includes(term)));
}

function getSunoConfig() {
  try { return JSON.parse(localStorage.getItem("moodscape_suno") || "{}"); }
  catch (e) { return {}; }
}

function saveSunoConfig(cfg) {
  localStorage.setItem("moodscape_suno", JSON.stringify(cfg));
}

function getTrackCache() {
  try { return JSON.parse(localStorage.getItem("moodscape_tracks") || "{}"); }
  catch (e) { return {}; }
}

function cacheTrackUrl(key, url) {
  const c = getTrackCache(); c[key] = url;
  try { localStorage.setItem("moodscape_tracks", JSON.stringify(c)); } catch (e) {}
}

// Determine the musical key (major vs minor) with better contextual judgment.
// Hanok villages, traditional folk sites, temples, scenic parks, lakes, and beaches should be major/happy/serene.
// Minor keys are reserved for solemn, dramatic, or cave/underground places.
// The default case (no category override) is driven by the place's region's
// Visitor Pleasantness score, not its own activity-derived score — this is
// what gives ISO 12913's Pleasantness axis an actual path into the audio
// (DEVELOPMENT_PLAN.md Priority 2). Pass stateName when it's available;
// without it this falls back to the old score-threshold behavior.
function getMusicalKey(place, stateName) {
  // Solemn, memorial, war, observatory, DMZ, or cave locations use minor key
  if (matchesPlace(place, PLACE_TERMS.keySolemn)) {
    return "minor key";
  }
  
  // Hanok, traditional, folk, temples, palaces, ruins, parks, beaches, lakes, nature are always major
  if (matchesPlace(place, PLACE_TERMS.keyMajor)) {
    return "major key";
  }
  
  // Default: the region's Visitor Pleasantness relative to the national median
  // across all 17 regions (see PLEASANTNESS_MEDIAN in data.js) — a fixed
  // threshold doesn't work here since every region's pleasantness sits in a
  // narrow band. Falls back to the old score-threshold rule if stateName
  // wasn't passed or the region model isn't available.
  const model = stateName && typeof REGION_MODEL !== "undefined" && REGION_MODEL[stateName];
  if (model) {
    return model.pleasantness >= PLEASANTNESS_MEDIAN ? "major key" : "minor key";
  }
  return place.score > 0.45 ? "major key" : "minor key";
}

// Tailor the style words based on score and place type to avoid repetitive EDM/electro house
function getSunoStyleBase(place) {
  const name = (place.name || "").toLowerCase();
  const score = place.score;

  // 1. Solemn / Memorial / DMZ
  if (matchesPlace(place, PLACE_TERMS.styleSolemn)) {
    return "solemn cinematic ambient, deep emotional orchestral drone, moving cello, respectful, quiet";
  }

  // 2. Traditional / Hanok / Palace / Temple / Folk
  if (matchesPlace(place, PLACE_TERMS.traditional)) {
    if (score > 0.6) {
      return "upbeat traditional Korean K-fusion, modern groove with ancient instruments, energetic, warm";
    } else if (score > 0.3) {
      return "warm acoustic folk, beautiful traditional Korean court-fusion, serene and happy, gentle rhythm";
    } else {
      return "serene traditional Korean meditation music, peaceful daegeum flute and gayageum pluck, warm, quiet, contemplative";
    }
  }

  // 3. Nature / Scenic / Park / Beach / Lake / Mountain / Valley
  if (matchesPlace(place, PLACE_TERMS.nature)) {
    if (score > 0.75) {
      if (name.includes("haeundae")) {
        return "tropical house, sun-drenched coastal synth groove, warm summer beach vibe, uplifting";
      }
      return "breeze-filled acoustic indie rock, bright coastal groove, happy, celebratory";
    } else if (score > 0.3) {
      return "dreamy organic downtempo, gentle acoustic guitar and warm ambient pads, relaxing, peaceful";
    } else {
      return "peaceful cinematic ambient, quiet nature soundscape, gentle acoustic strings, serene, warm";
    }
  }

  // 4. Industrial / Tech / Science
  if (matchesPlace(place, PLACE_TERMS.industrial)) {
    if (score > 0.6) {
      return "futuristic progressive electronic, clean high-tech synth layers, driving modular rhythm, sleek";
    } else {
      return "ambient IDM, glitchy minimalist electronic, warm synthesizer pads, cleanroom atmosphere, precise";
    }
  }

  // 5. Modern / Urban / Youth / Art / Entertainment
  if (matchesPlace(place, PLACE_TERMS.urban)) {
    if (score > 0.75) {
      if (name.includes("hongdae")) {
        return "energetic K-indie rock, electric guitar riffs, lively drums, youthful band vibe, upbeat";
      }
      if (name.includes("gangnam")) {
        return "sleek modern K-pop style synth-pop, high-fashion dance groove, polished, luxurious";
      }
      if (name.includes("biff")) {
        return "cinematic jazz-funk, upbeat brass section, lively street festival rhythm, groovy";
      }
      return "lively synth-pop, cheerful arpeggios, upbeat electronic groove, catchy";
    } else if (score > 0.3) {
      return "mellow lo-fi hip-hop, relaxing city-pop synth pads, chill urban beat, warm";
    } else {
      return "calm urban ambient, soft minimalist keys, relaxing, peaceful";
    }
  }

  // Fallback to general score-based bands (but simplified and less repetitive)
  if (score < 0.25) return "slow ambient drone, sparse, meditative, deep reverb, almost silent";
  if (score < 0.5) return "calm lo-fi, soft mellow keys, gentle warmth, relaxed";
  if (score < 0.75) return "downtempo, balanced groove, mellow beat, atmospheric pads";
  return "lively electronic synth-pop, bright arpeggios, energetic groove, upbeat";
}

// Keep descriptive style words from contradicting the independently computed
// mode. This improves the request; it does not imply that Suno will obey it.
function getSunoStyle(place, stateName) {
  const key = getMusicalKey(place, stateName);
  let style = getSunoStyleBase(place);
  if (key === "minor key") {
    style = style
      .replace(/\b(bright|cheerful|happy|uplifting|celebratory)\b,?\s*/gi, "")
      .replace(/\s+,/g, ",")
      .replace(/,\s*,/g, ",");
    return `${style.replace(/[\s,]+$/, "")}, shadowed minor-key color`;
  }
  return `${style.replace(/[\s,]+$/, "")}, open major-key color`;
}

// BPM range widened from the original 40–120 to 42–152. The original ceiling meant even
// Hongdae — the single highest-scoring place across all 85 — only reached ~115 BPM, well
// below real K-indie/dance-pop energy (120–150+), so the "most energetic" place in the app
// could never actually sound fast. This keeps the calm end (~42 BPM) about the same while
// letting high-score places reach a genuinely energetic tempo.
function getSunoBpm(place) {
  return Math.round(42 + place.score * 110);
}

// Most places should stay purely instrumental so the track reads as an ambient soundscape
// of the place, not a song about it. A few places contradict a blanket "no vocals" with
// their own instrumentation/character text (pansori is inherently sung, monk chant is
// vocal, Hongdae's character is literally "buskers") — those get wordless vocals instead,
// keeping the human voice as texture without introducing unrelated lyrics.
function getVocalDirective(place) {
  const name = (place.name || "").toLowerCase();
  const instr = (place.instrumentation || "").toLowerCase();
  const char = (place.character || "").toLowerCase();

  if (instr.includes("pansori")) return "wordless pansori-style vocal cries, no full lyrics";
  if (instr.includes("chant") || instr.includes("monk")) return "wordless Buddhist chant vocals, no full lyrics";
  if (name.includes("hongdae") || char.includes("busker")) return "wordless vocal ad-libs and shouted crowd energy, no full lyrics";
  return "no vocals, no lyrics";
}

function buildSunoPrompt(place, stateName) {
  const bpm = getSunoBpm(place);
  const key = getMusicalKey(place, stateName);
  const style = getSunoStyle(place, stateName);
  const vocals = getVocalDirective(place);
  return `Music for ${place.character || (place.name + ", " + stateName + ", South Korea")}. `
    + `${style}, ${key}, around ${bpm} BPM. Instrumentation: ${place.instrumentation}. `
    + `Cinematic, atmospheric, ${vocals}.`;
}

// Keep the generated style inside Suno's documented V4.5 custom-mode limit.
// Normalising whitespace also prevents copied line breaks from consuming useful
// style space or changing how the provider tokenises an otherwise identical prompt.
function normalizeSunoStyle(style) {
  return String(style || "").replace(/\s+/g, " ").trim().slice(0, 1000);
}

function sunoPhrase(value) {
  return String(value || "").replace(/\s+/g, " ").trim().replace(/[\s,;.!?]+$/, "");
}

function getSunoRootNote(place) {
  const notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"];
  const score = Math.max(0, Math.min(1, Number(place.score) || 0));
  return notes[Math.round(score * 12) % 12];
}

function buildSunoGenerationRequest(place, stateName, model, promptOverride) {
  const style = normalizeSunoStyle(promptOverride || buildSunoPrompt(place, stateName));
  if (!style) throw new Error("Suno style is empty");
  const vocalDirective = getVocalDirective(place);
  const isFullyInstrumental = vocalDirective === "no vocals, no lyrics";
  const request = {
    customMode: true,
    instrumental: isFullyInstrumental,
    model,
    // In custom mode Suno documents style + title as explicit controls. Sending
    // scene prose as a non-custom prompt made it reinterpret
    // Gemini's decisions instead of treating them as explicit music settings.
    style,
    title: `${place.name} — Moodscape`.slice(0, 80),
    callBackUrl: "https://httpbin.org/post"
  };
  // Custom vocal mode also requires a lyrics prompt. Section tags request voice
  // as timbre without supplying words for the model to sing.
  if (!isFullyInstrumental) {
    request.prompt = "[Instrumental Intro]\n[Wordless Vocalise]\n[Instrumental Outro]";
  }
  return request;
}

// sunoapi.org answers browser CORS preflights (checked 2026-09-20 for both localhost and the "null"
// origin of a file:// page), so requests go straight there. The Bearer key used to be sent through the
// public corsproxy.io on every call; a proxy is now used only if the user sets one they control
// (cfg.proxy, e.g. "https://my-worker.example.workers.dev/?url=").
function getProxiedUrl(url, cfg) {
  return cfg && cfg.proxy ? cfg.proxy + encodeURIComponent(url) : url;
}

// Live generation against sunoapi.org
async function sunoGenerate(place, stateName, cfg, promptOverride) {
  const base = (cfg.base || "https://api.sunoapi.org").replace(/\/+$/, "");
  const genPath = cfg.generatePath || "/api/v1/generate";
  const pollPath = cfg.pollPath || "/api/v1/generate/record-info";
  const model = cfg.model || "V4_5";
  // Use the prompt the panel is showing (it may be the AI-predicted one), not a silently rebuilt copy.
  const prompt = (promptOverride && promptOverride.trim()) || buildSunoPrompt(place, stateName);

  const genUrl = getProxiedUrl(base + genPath, cfg);
  const genRes = await fetch(genUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Authorization": "Bearer " + cfg.key },
    body: JSON.stringify(buildSunoGenerationRequest(place, stateName, model, prompt))
  });
  if (!genRes.ok) throw new Error("generate HTTP " + genRes.status + ": " + (await genRes.text()).slice(0, 200));
  const genJson = await genRes.json();
  const taskId = genJson.taskId || genJson.task_id || (genJson.data && (genJson.data.taskId || genJson.data.task_id));
  if (!taskId) throw new Error("no taskId in response: " + JSON.stringify(genJson).slice(0, 200));

  // poll up to ~2.5 min (generation typically takes 30-90s)
  for (let i = 0; i < 50; i++) {
    await new Promise(r => setTimeout(r, 3000));
    const pollUrl = getProxiedUrl(base + pollPath + "?taskId=" + encodeURIComponent(taskId), cfg);
    const pr = await fetch(pollUrl, {
      headers: { "Authorization": "Bearer " + cfg.key }
    });
    if (!pr.ok) continue;
    const pj = await pr.json();
    const status = pj.data && pj.data.status;
    if (status && /FAIL|ERROR/i.test(status)) throw new Error("generation failed: " + status);
    const sunoData = pj.data && pj.data.response && pj.data.response.sunoData;
    if (Array.isArray(sunoData)) {
      // audioUrl is the finished file. streamAudioUrl can be a partial stream while the task is still
      // running, so it is only accepted once the task reports SUCCESS and no finished file is listed.
      for (const it of sunoData) {
        if (it.audioUrl) return it.audioUrl;
      }
      if (status && /^SUCCESS$/i.test(status)) {
        for (const it of sunoData) {
          if (it.streamAudioUrl) return it.streamAudioUrl;
        }
      }
    }
  }
  throw new Error("generation timed out");
}

function copySunoPrompt() {
  const ta = document.getElementById("suno-prompt");
  if (!ta) return;
  ta.select();
  navigator.clipboard.writeText(ta.value).then(() => {
    const btn = document.getElementById("copy-prompt-btn");
    if (btn) { const t = btn.textContent; btn.textContent = "Copied ✓"; setTimeout(() => btn.textContent = t, 1500); }
  }).catch(() => {});
}

function toggleSunoPanel() {
  const p = document.getElementById("suno-panel");
  if (p) p.style.display = p.style.display === "none" ? "block" : "none";
}

function saveSunoKey() {
  const cfg = getSunoConfig();
  cfg.base = (document.getElementById("suno-base").value || "").trim();
  cfg.key = (document.getElementById("suno-key").value || "").trim();
  saveSunoConfig(cfg);
  const s = document.getElementById("suno-save-status");
  if (s) { s.textContent = "Saved to this browser."; setTimeout(() => s.textContent = "", 2000); }
}

// ── GEMINI AI CONFIG & CHAT INTEGRATION ──────────────────────────────────────

function getGeminiConfig() {
  try { return JSON.parse(localStorage.getItem("moodscape_gemini") || "{}"); }
  catch (e) { return {}; }
}

function saveGeminiConfig(cfg) {
  localStorage.setItem("moodscape_gemini", JSON.stringify(cfg));
}

// The API key goes in a header, never the URL, and requests go straight to Google: both APIs answer
// browser CORS preflights (checked 2026-09-20, including the "null" origin of a file:// page), so the
// public corsproxy.io hop that used to carry every key is not needed.
function geminiEndpoint(model) {
  return `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;
}

function geminiHeaders(apiKey) {
  return { "Content-Type": "application/json", "x-goog-api-key": apiKey };
}

function buildSystemPrompt(place, stateName) {
  const persona = getLocalPersona(stateName, place);
  return `You are a local resident of ${place.name} in ${stateName}, South Korea. 
Your persona is: ${persona.name}.
Your job or role matches the location's character: ${place.type}. 
Your personality and greeting style is: "${persona.greeting}".

Instructions:
1. Answer the user's questions in a friendly, conversational, and helpful tone.
2. Answer from your local resident persona's perspective. Avoid saying "I am an AI" or "I am a language model". Talk about street busking, history, local tea pairings, mountain hiking, or surfing depending on your role!
3. Keep your answers brief (maximum 2-3 sentences).
4. Feel free to occasionally use simple Korean words of excitement or friendliness (e.g. "Annyeong!", "Daebak!", "Jinja?") but write the main answer in English.`;
}

async function askGeminiLocal(question, place, stateName, apiKey) {
  const systemInstruction = buildSystemPrompt(place, stateName);

  // Model verified against the live Gemini API docs/pricing pages (ai.google.dev) on 2026-08-09.
  // gemini-1.5-flash is fully shut down (all 1.5/1.0 models return HTTP 404) — this call was
  // silently broken before this change. gemini-2.5-flash-lite is cheaper ($0.10/$0.40 per 1M
  // tokens vs gemini-3.5-flash-lite's $0.30/$2.50) but Google has already announced its
  // retirement for 2026-10-16, so gemini-3.5-flash-lite is used instead: it's the cheapest
  // model in the current, non-deprecated 3.5 generation with no shutdown date announced.
  const GEMINI_MODEL = "gemini-3.5-flash-lite";

  const url = geminiEndpoint(GEMINI_MODEL);

  const response = await fetch(url, {
    method: "POST",
    headers: geminiHeaders(apiKey),
    body: JSON.stringify({
      contents: [{ parts: [{ text: question }] }],
      systemInstruction: { parts: [{ text: systemInstruction }] },
      generationConfig: { maxOutputTokens: 150, temperature: 0.7 }
    })
  });

  if (!response.ok) {
    throw new Error(`Gemini API error (HTTP ${response.status})`);
  }

  const json = await response.json();
  if (json.candidates && json.candidates[0] && json.candidates[0].content && json.candidates[0].content.parts[0]) {
    return json.candidates[0].content.parts[0].text;
  }
  
  throw new Error("Invalid response format from Gemini API");
}

// ── AI MUSIC-STYLE PREDICTION (multimodal: research data + real photo) ──────────
// Instead of the hand-written keyword rules in getSunoStyle()/getMusicalKey(), this
// sends Gemini the place's actual research data (character, type, instrumentation
// tags, region) AND its real Wikimedia photo, and asks it to predict the genre/
// instrumentation/tempo/key that best fits — a genuine model-based prediction rather
// than a lookup table. Requires the same Gemini key already used by "Ask a Local".

const MUSIC_PREDICTION_CACHE_VERSION = "v1";

function musicPredictionCacheKey(place, stateName) {
  return [MUSIC_PREDICTION_CACHE_VERSION, stateName, place.name, getSunoBpm(place),
    getMusicalKey(place, stateName), getSunoRootNote(place)].join("|");
}

function getMusicPredictionCache() {
  try { return JSON.parse(localStorage.getItem("moodscape_music_predictions") || "{}"); }
  catch (e) { return {}; }
}

function getCachedMusicPrediction(place, stateName) {
  return getMusicPredictionCache()[musicPredictionCacheKey(place, stateName)] || null;
}

function cacheMusicPrediction(place, stateName, prediction) {
  const cache = getMusicPredictionCache();
  cache[musicPredictionCacheKey(place, stateName)] = prediction;
  try { localStorage.setItem("moodscape_music_predictions", JSON.stringify(cache)); } catch (e) {}
}

async function imageUrlToBase64(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error("image fetch HTTP " + res.status);
  const blob = await res.blob();
  const mimeType = blob.type || "image/jpeg";
  const data = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result.split(",")[1]);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
  return { data, mimeType };
}

async function predictMusicStyleWithAI(place, stateName, apiKey) {
  const GEMINI_MODEL = "gemini-3.5-flash-lite";
  const url = geminiEndpoint(GEMINI_MODEL);

  const targetBpm = getSunoBpm(place);
  const targetKey = getMusicalKey(place, stateName);
  const targetRoot = getSunoRootNote(place);
  const vocalDirective = getVocalDirective(place);
  const parts = [{
    text: `You are the music director for a place-based, instrumental sound-mapping app. Choose the aesthetic details that will make a Suno V4.5 generation evoke this specific place.

Place: ${place.name}, ${stateName}, South Korea
Type: ${place.type}
Real description: ${place.character}
Existing instrumentation tags: ${place.instrumentation}
Current mood score (0=very calm, 1=very energetic): ${place.score}
Locked tempo from the app's data mapping: exactly ${targetBpm} BPM
Locked tonal center and mode from the app's pitch/pleasantness mapping: ${targetRoot} ${targetKey.split(" ")[0]}
Locked vocal treatment: ${vocalDirective}

A real photo of this place is attached. Use visible architecture, landscape, materials, color, light, and activity to refine genre, timbre, mood, and arrangement. A single photo may show a quiet moment at a normally energetic place, so treat the real description as the stable identity and the photo as texture; do not let time of day or temporary crowd density contradict the locked tempo or mode.

Use concrete, audible production language that Suno can follow. Do not name artists. Do not repeat the place name, BPM, key, vocal instruction, or generic words such as "cinematic" and "atmospheric" in your fields. Keep genre under 8 words, instrumentation to 3-6 comma-separated sound sources, mood_descriptors to 3-5 adjectives, and arrangement to one concise sentence describing density, rhythm, and development. Respond ONLY with the requested JSON.`
  }];

  try {
    if (place.photo) {
      const img = await imageUrlToBase64(place.photo);
      parts.push({ inlineData: { mimeType: img.mimeType, data: img.data } });
    }
  } catch (e) {
    // Photo fetch failed (CORS, offline, etc.) — proceed text-only rather than fail the whole prediction.
  }

  const response = await fetch(url, {
    method: "POST",
    headers: geminiHeaders(apiKey),
    body: JSON.stringify({
      contents: [{ parts }],
      generationConfig: {
        temperature: 0.35,
        responseMimeType: "application/json",
        responseSchema: {
          type: "OBJECT",
          properties: {
            genre: { type: "STRING", description: "Specific music genre/style, e.g. 'lo-fi city pop' or 'traditional Korean court music'" },
            instrumentation: { type: "STRING", description: "Comma-separated instruments/sound elements" },
            mood_descriptors: { type: "STRING", description: "3-5 adjectives" },
            arrangement: { type: "STRING", description: "One concise sentence describing density, rhythm, and how the piece develops" },
            reasoning: { type: "STRING", description: "1-2 sentences on why this fits, referencing what's visible in the photo if used" }
          },
          required: ["genre", "instrumentation", "mood_descriptors", "arrangement", "reasoning"]
        }
      }
    })
  });

  if (!response.ok) {
    throw new Error(`Gemini API error (HTTP ${response.status}): ${(await response.text()).slice(0, 200)}`);
  }

  const json = await response.json();
  const text = json.candidates && json.candidates[0] && json.candidates[0].content &&
               json.candidates[0].content.parts[0] && json.candidates[0].content.parts[0].text;
  if (!text) throw new Error("Invalid response format from Gemini API");

  const prediction = JSON.parse(text);
  // These are app-controlled sonification parameters, not model guesses. Adding
  // them after parsing gives every downstream consumer one consistent object.
  prediction.bpm = targetBpm;
  prediction.key = targetKey;
  prediction.root_note = targetRoot;
  prediction.vocals = vocalDirective;
  return prediction;
}

function buildSunoPromptFromAIPrediction(place, stateName, prediction) {
  const bpm = getSunoBpm(place);
  const key = getMusicalKey(place, stateName);
  const root = getSunoRootNote(place);
  const vocals = getVocalDirective(place);
  return normalizeSunoStyle(
    `${sunoPhrase(prediction.genre)}; ${sunoPhrase(prediction.mood_descriptors)}. `
    + `Exactly ${bpm} BPM, in ${root} ${key.split(" ")[0]}. Instrumentation: ${sunoPhrase(prediction.instrumentation)}. `
    + `Arrangement: ${sunoPhrase(prediction.arrangement)}. ${vocals}. `
    + `Evokes ${place.character || (place.name + ", " + stateName + ", South Korea")}.`
  );
}

// ── LANGUAGE PROFICIENCY (selectable, AI-estimated) ──────────────────────────
// The mood formula's "English proficiency" term (about.html §03) hard-coded one
// language for every listener. This generalizes it: the listener picks their own
// language, and the province's accessibility score for that specific language is
// estimated live via the same Gemini key already used by "Ask a Local" and the AI
// music-style predictor — rather than only ever citing the English-specific EF EPI
// number. Results are cached per province+language pair since they don't change
// moment to moment and re-querying on every panel open would just burn quota.

const LANGUAGE_OPTIONS = [
  "English", "Korean", "Mandarin Chinese", "Japanese", "Spanish", "French",
  "German", "Vietnamese", "Russian", "Arabic", "Hindi", "Portuguese", "Thai"
];

function getLanguageConfig() {
  try { return JSON.parse(localStorage.getItem("moodscape_language") || "{}"); }
  catch (e) { return {}; }
}

function saveLanguageConfig(cfg) {
  localStorage.setItem("moodscape_language", JSON.stringify(cfg));
}

function getSelectedLanguage() {
  return getLanguageConfig().language || "English";
}

function getLanguageScoreCache() {
  try { return JSON.parse(localStorage.getItem("moodscape_lang_scores") || "{}"); }
  catch (e) { return {}; }
}

function cacheLanguageScore(key, data) {
  const c = getLanguageScoreCache();
  c[key] = data;
  try { localStorage.setItem("moodscape_lang_scores", JSON.stringify(c)); } catch (e) {}
}

function languageScoreKey(stateName, language) {
  return slugify(stateName) + "__" + slugify(language);
}

// Global language picker in the site header (both index.html and about.html).
// Keeps localStorage as the single source of truth; syncs the in-panel dropdown
// (rendered per province in ui.js) and refreshes an already-open panel so a
// language change takes effect immediately rather than only on next visit.
function onHeaderLanguageChange(value) {
  const cfg = getLanguageConfig();
  cfg.language = value;
  saveLanguageConfig(cfg);

  if (typeof setInterfaceLanguage === "function") {
    setInterfaceLanguage(value);
  }

  if (typeof currentState !== "undefined" && currentState && typeof showStateSide === "function") {
    showStateSide(currentState);
  }
  const panelSelect = document.getElementById("lang-select");
  if (panelSelect && panelSelect.value !== value) panelSelect.value = value;
}

function initHeaderLanguageSelect() {
  const sel = document.getElementById("header-lang-select");
  if (sel) sel.value = getSelectedLanguage();
  if (typeof setInterfaceLanguage === "function") {
    setInterfaceLanguage(getSelectedLanguage());
  }
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", initHeaderLanguageSelect);
}

async function predictLanguageProficiencyWithAI(stateName, language, apiKey) {
  const GEMINI_MODEL = "gemini-3.5-flash-lite";
  const url = geminiEndpoint(GEMINI_MODEL);

  const prompt = `You are estimating a "language accessibility" score for Moodscape, a data-sonification app that scores South Korean provinces on a mood formula. One input to that formula is how easy it is for a visitor who speaks ${language} (and no Korean) to navigate and communicate in ${stateName}, South Korea.

Base your estimate on real, general knowledge of ${stateName}: things like international airport/tourism volume, presence of ${language}-speaking expat or immigrant communities, international schools or universities, prevalence of translated signage and menus, and how it compares to other Korean provinces. If ${language} is English, you may anchor on South Korea's real EF English Proficiency Index (nationally "moderate", roughly 520-550 in major metro areas) but still reason about this specific province rather than just repeating the national number. For every other language there is no equivalent published index, so this is a reasoned estimate from proxy signals, not a citation — say so plainly in the reasoning.

Respond ONLY with the requested JSON: a 0-100 integer score (0 = essentially no ${language} accessibility, 100 = fully navigable in ${language} without any Korean), a short label, and 1-2 sentences of reasoning.`;

  const response = await fetch(url, {
    method: "POST",
    headers: geminiHeaders(apiKey),
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: {
        temperature: 0.4,
        responseMimeType: "application/json",
        responseSchema: {
          type: "OBJECT",
          properties: {
            score: { type: "INTEGER", description: "0-100 language accessibility estimate" },
            label: { type: "STRING", description: "e.g. 'High', 'Moderate', 'Low'" },
            reasoning: { type: "STRING", description: "1-2 sentences, framed as a reasoned estimate rather than a measured statistic" }
          },
          required: ["score", "label", "reasoning"]
        }
      }
    })
  });

  if (!response.ok) {
    throw new Error(`Gemini API error (HTTP ${response.status}): ${(await response.text()).slice(0, 200)}`);
  }

  const json = await response.json();
  const text = json.candidates && json.candidates[0] && json.candidates[0].content &&
               json.candidates[0].content.parts[0] && json.candidates[0].content.parts[0].text;
  if (!text) throw new Error("Invalid response format from Gemini API");

  return JSON.parse(text);
}
