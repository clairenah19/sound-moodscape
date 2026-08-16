// ── MOOD SCAPE SUNO PROMPTS & CONFIG ─────────────────────────────────────────

window.SUNO_TRACKS = window.SUNO_TRACKS || {};

function slugify(s) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

function placeKey(stateName, place) {
  return slugify(stateName) + "__" + slugify(place.name);
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
function getMusicalKey(place) {
  const name = (place.name || "").toLowerCase();
  const type = (place.type || "").toLowerCase();
  const char = (place.character || "").toLowerCase();
  
  // Solemn, memorial, war, observatory, DMZ, or cave locations use minor key
  if (
    name.includes("cemetery") || type.includes("cemetery") ||
    name.includes("memorial") || type.includes("memorial") ||
    name.includes("5.18") ||
    name.includes("observatory") || type.includes("observatory") ||
    name.includes("dmz") || char.includes("dmz") ||
    name.includes("cave") || type.includes("cave") ||
    name.includes("tomb") || type.includes("tomb") ||
    name.includes("dolmen") || type.includes("dolmen") ||
    name.includes("taejongdae")
  ) {
    return "minor key";
  }
  
  // Hanok, traditional, folk, temples, palaces, ruins, parks, beaches, lakes, nature are always major
  if (
    type.includes("hanok") || type.includes("traditional") || type.includes("folk") ||
    type.includes("temple") || type.includes("palace") || type.includes("ruins") ||
    type.includes("park") || type.includes("beach") || type.includes("lake") ||
    type.includes("island") || type.includes("nature") || type.includes("valley") ||
    type.includes("garden") || type.includes("arboretum") || type.includes("springs") ||
    name.includes("hanok") || name.includes("temple") || name.includes("palace") ||
    name.includes("village")
  ) {
    return "major key";
  }
  
  // Default to major key for a happier, less minor-heavy distribution
  return place.score > 0.45 ? "major key" : "minor key";
}

// Tailor the style words based on score and place type to avoid repetitive EDM/electro house
function getSunoStyle(place) {
  const name = (place.name || "").toLowerCase();
  const type = (place.type || "").toLowerCase();
  const score = place.score;

  // 1. Solemn / Memorial / DMZ
  if (
    name.includes("cemetery") || type.includes("cemetery") ||
    name.includes("memorial") || type.includes("memorial") ||
    name.includes("5.18") ||
    name.includes("observatory") || type.includes("observatory") ||
    name.includes("dmz")
  ) {
    return "solemn cinematic ambient, deep emotional orchestral drone, moving cello, respectful, quiet";
  }

  // 2. Traditional / Hanok / Palace / Temple / Folk
  if (
    type.includes("hanok") || type.includes("traditional") || type.includes("folk") ||
    type.includes("temple") || type.includes("palace") || type.includes("ruins") ||
    name.includes("hanok") || name.includes("temple") || name.includes("palace") ||
    name.includes("village")
  ) {
    if (score > 0.6) {
      return "upbeat traditional Korean K-fusion, modern groove with ancient instruments, energetic, warm";
    } else if (score > 0.3) {
      return "warm acoustic folk, beautiful traditional Korean court-fusion, serene and happy, gentle rhythm";
    } else {
      return "serene traditional Korean meditation music, peaceful daegeum flute and gayageum pluck, warm, quiet, contemplative";
    }
  }

  // 3. Nature / Scenic / Park / Beach / Lake / Mountain / Valley
  if (
    type.includes("park") || type.includes("beach") || type.includes("lake") ||
    type.includes("island") || type.includes("nature") || type.includes("valley") ||
    type.includes("garden") || type.includes("arboretum") || type.includes("cape") ||
    type.includes("cliff") || type.includes("cave") || name.includes("mountain") ||
    name.includes("beach") || name.includes("lake") || name.includes("cave")
  ) {
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
  if (
    type.includes("plant") || type.includes("factory") || type.includes("shipyard") ||
    type.includes("tech") || type.includes("science") || type.includes("complex") ||
    type.includes("research") || type.includes("fabrication") || type.includes("industrial") ||
    name.includes("hynix") || name.includes("posco") || name.includes("hyundai") || name.includes("kia")
  ) {
    if (score > 0.6) {
      return "futuristic progressive electronic, clean high-tech synth layers, driving modular rhythm, sleek";
    } else {
      return "ambient IDM, glitchy minimalist electronic, warm synthesizer pads, cleanroom atmosphere, precise";
    }
  }

  // 5. Modern / Urban / Youth / Art / Entertainment
  if (
    type.includes("district") || type.includes("youth") || type.includes("hub") ||
    type.includes("center") || type.includes("cinema") || type.includes("plaza") ||
    type.includes("amusement") || type.includes("pier") || type.includes("market") ||
    type.includes("shopping") || type.includes("design") || type.includes("quarter") ||
    name.includes("hongdae") || name.includes("gangnam") || name.includes("biff") ||
    name.includes("plaza") || name.includes("market")
  ) {
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

function buildSunoPrompt(place, stateName) {
  const bpm = Math.round(40 + place.score * 80);
  const key = getMusicalKey(place);
  const style = getSunoStyle(place);
  return `Instrumental music for ${place.character || (place.name + ", " + stateName + ", South Korea")}. `
    + `${style}, ${key}, around ${bpm} BPM. Instrumentation: ${place.instrumentation}. `
    + `Cinematic, atmospheric, no vocals, no lyrics.`;
}

// Helper to proxy requests through corsproxy.io if running on file:// protocol or default sunoapi.org host
function getProxiedUrl(url) {
  const isDefaultHost = url.includes("sunoapi.org");
  if (window.location.protocol === "file:" || isDefaultHost) {
    return "https://corsproxy.io/?url=" + encodeURIComponent(url);
  }
  return url;
}

// Live generation against sunoapi.org
async function sunoGenerate(place, stateName, cfg) {
  const base = (cfg.base || "https://api.sunoapi.org").replace(/\/+$/, "");
  const genPath = cfg.generatePath || "/api/v1/generate";
  const pollPath = cfg.pollPath || "/api/v1/generate/record-info";
  const model = cfg.model || "V4_5";
  const prompt = buildSunoPrompt(place, stateName);

  const genUrl = getProxiedUrl(base + genPath);
  const genRes = await fetch(genUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Authorization": "Bearer " + cfg.key },
    body: JSON.stringify({
      prompt, customMode: false, instrumental: true, model,
      callBackUrl: "https://httpbin.org/post"
    })
  });
  if (!genRes.ok) throw new Error("generate HTTP " + genRes.status + ": " + (await genRes.text()).slice(0, 200));
  const genJson = await genRes.json();
  const taskId = genJson.taskId || genJson.task_id || (genJson.data && (genJson.data.taskId || genJson.data.task_id));
  if (!taskId) throw new Error("no taskId in response: " + JSON.stringify(genJson).slice(0, 200));

  // poll up to ~2.5 min (generation typically takes 30-90s)
  for (let i = 0; i < 50; i++) {
    await new Promise(r => setTimeout(r, 3000));
    const pollUrl = getProxiedUrl(base + pollPath + "?taskId=" + encodeURIComponent(taskId));
    const pr = await fetch(pollUrl, {
      headers: { "Authorization": "Bearer " + cfg.key }
    });
    if (!pr.ok) continue;
    const pj = await pr.json();
    const status = pj.data && pj.data.status;
    if (status && /FAIL|ERROR/i.test(status)) throw new Error("generation failed: " + status);
    const sunoData = pj.data && pj.data.response && pj.data.response.sunoData;
    if (Array.isArray(sunoData)) {
      for (const it of sunoData) {
        const audioUrl = it.audioUrl || it.streamAudioUrl;
        if (audioUrl) return audioUrl;
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

  // Use a CORS proxy if running from file:// protocol to avoid preflight issues
  let url = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${apiKey}`;
  if (window.location.protocol === "file:") {
    url = "https://corsproxy.io/?url=" + encodeURIComponent(url);
  }

  const response = await fetch(url, {
    method: "POST",
    headers: { 
      "Content-Type": "application/json"
    },
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
  let url = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${apiKey}`;
  if (window.location.protocol === "file:") {
    url = "https://corsproxy.io/?url=" + encodeURIComponent(url);
  }

  const parts = [{
    text: `You are predicting the best instrumental music style for a place in a sound-mapping app.

Place: ${place.name}, ${stateName}, South Korea
Type: ${place.type}
Real description: ${place.character}
Existing instrumentation tags: ${place.instrumentation}
Current mood score (0=very calm, 1=very energetic): ${place.score}

A real photo of this place is attached — use what you can actually see in it (crowd density, architecture, nature vs. urban, color/light, activity level) together with the text description above to predict what music would genuinely fit best, not just a generic mapping from the score. Respond ONLY with the requested JSON.`
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
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{ parts }],
      generationConfig: {
        temperature: 0.6,
        responseMimeType: "application/json",
        responseSchema: {
          type: "OBJECT",
          properties: {
            genre: { type: "STRING", description: "Specific music genre/style, e.g. 'lo-fi city pop' or 'traditional Korean court music'" },
            instrumentation: { type: "STRING", description: "Comma-separated instruments/sound elements" },
            tempo_feel: { type: "STRING", description: "e.g. 'slow and spacious' or 'driving and fast'" },
            key: { type: "STRING", enum: ["major key", "minor key"] },
            mood_descriptors: { type: "STRING", description: "3-5 adjectives" },
            reasoning: { type: "STRING", description: "1-2 sentences on why this fits, referencing what's visible in the photo if used" }
          },
          required: ["genre", "instrumentation", "tempo_feel", "key", "mood_descriptors", "reasoning"]
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

function buildSunoPromptFromAIPrediction(place, stateName, prediction) {
  const bpm = Math.round(40 + place.score * 80);
  return `Instrumental music for ${place.character || (place.name + ", " + stateName + ", South Korea")}. `
    + `${prediction.genre}, ${prediction.mood_descriptors}, ${prediction.tempo_feel}, ${prediction.key}, around ${bpm} BPM. `
    + `Instrumentation: ${prediction.instrumentation}. `
    + `Cinematic, atmospheric, no vocals, no lyrics.`;
}
