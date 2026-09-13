// ── MOOD SCAPE USER INTERFACE & NAVIGATION ─────────────────────────────────────

// Sends one concise line to the polite live region in index.html, so a screen
// reader announces what was selected in the visitor's own voice and speed. The
// blank-then-set is what makes repeat announcements of identical text register.
function announce(message) {
  const live = document.getElementById("a11y-live");
  if (!live) return;
  live.textContent = "";
  window.setTimeout(() => { live.textContent = message; }, 60);
}

// The live score is a reproducible proxy from official comparable statistics.
// It is deliberately not labelled as measured ISO Eventfulness.
function renderRegionResearchBadge(stateName) {
  const model = REGION_MODEL[stateName];
  if (!model) return "";
  const reference = model.reference ? " · direct soundscape reference available" : " · no direct regional soundscape measurement";
  return `<div class="pe-badge modelled" title="Official inputs; hypothesis weights; not a measured ISO score${reference}" style="margin-bottom:10px;">Modelled proxy</div>`;
}

function renderRegionModelDetails(stateName) {
  const m = REGION_MODEL[stateName];
  if (!m) return "";
  const x = m.input;
  const reference = m.reference
    ? `<div class="model-reference"><b>Direct study reference:</b> Eventfulness ${m.reference.eventfulness}/100. This is shown for comparison, not mixed into the model.</div>`
    : `<div class="model-reference muted">No direct regional soundscape survey is available; this score requires listener validation.</div>`;
  return `<details class="model-details">
    <summary>See data and calculation</summary>
    <div class="model-summary"><b>${m.activity.toFixed(1)}</b> activity proxy · <b>${m.pleasantness.toFixed(1)}</b> visitor pleasantness context</div>
    <div class="model-grid">
      <span>Density (35%)</span><b>${x.density.toLocaleString()}/km²</b>
      <span>Tourism intensity (30%)</span><b>${m.raw.tourism.toFixed(1)} trips/resident</b>
      <span>Noise complaints (15%)</span><b>${m.raw.complaints.toFixed(1)}/100k</b>
      <span>Noise facilities (10%)</span><b>${m.raw.facilities.toFixed(1)}/100k</b>
      <span>Crowding pressure (10%)</span><b>${m.raw.crowdingPressure.toFixed(1)}/100</b>
    </div>
    <p>Inputs are log min–max scaled across all 17 regions, then weighted. Pleasantness is kept separate: 40% overall satisfaction + 25% recommendation + 20% revisit + 15% crowding satisfaction.</p>
    ${reference}
  </details>`;
}

// A single, real, sourced "hidden gem" per province — a place surfaced from an
// independent travel blog rather than picked by us, since a curated app naming
// its own hidden gems would just be another opinion. Every quote/URL here was
// pulled from the blog post itself, not paraphrased from a search summary.
function renderHiddenGem(stateName) {
  const g = MOOD_DATA.states[stateName].hiddenGem;
  if (!g) return "";
  return `
    <div class="panel-section">
      <div class="panel-title">Hidden gem</div>
      <div class="hidden-gem-card">
        <div class="hidden-gem-name">💎 ${g.name}</div>
        <div class="hidden-gem-note">${g.note}</div>
        <blockquote class="hidden-gem-quote">“${g.quote}”</blockquote>
        <div class="hidden-gem-source">— <a href="${g.sourceUrl}" target="_blank" rel="noopener">${g.source}</a></div>
      </div>
    </div>`;
}

function showStateSide(stateName) {
  const s = MOOD_DATA.states[stateName];
  isPlaying = false;
  stopPlayback();
  currentPlace = null;
  currentPlaceState = null;
  const panel = document.getElementById("panel-content");
  panel.innerHTML = `
    <div class="panel-section">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
        <div style="font-size:28px;">${s.emoji}</div>
        <div>
          <div style="font-size:16px;font-weight:600;">${stateName}</div>
          <div style="font-size:12px;color:var(--text2);">${s.desc}</div>
        </div>
      </div>
      ${renderRegionResearchBadge(stateName)}
      <div class="mood-bar-wrap" style="margin-bottom:4px;">
        <div style="font-size:11px;color:var(--text2);width:60px;">Activity</div>
        <div class="mood-bar"><div class="mood-fill" style="width:${s.score*100}%;background:${MOOD_COLOR(s.score)};"></div></div>
        <div class="mood-label">${MOOD_LABEL(s.score)}</div>
      </div>
      ${renderRegionModelDetails(stateName)}
    </div>
    <div class="panel-section">
      <div class="panel-title">Language accessibility</div>
      <select id="lang-select" class="suno-input" style="width:100%;margin-bottom:8px;" onchange="onLanguageChange('${stateName}')">
        ${LANGUAGE_OPTIONS.map(l => `<option value="${l}" ${l === getSelectedLanguage() ? "selected" : ""}>${l}</option>`).join("")}
      </select>
      <div id="lang-score-result">${renderLanguageScoreArea(stateName)}</div>
    </div>
    <div class="panel-section">
      <div class="narrative-card">
        <div class="narrative-label">The vibe, in words</div>
        ${buildProvinceNarrative(stateName)}
      </div>
    </div>
    ${renderHiddenGem(stateName)}
    <div class="panel-section">
      <div class="panel-title">Places to explore</div>
      ${s.places.map((p, i) => `
        <div class="region-card" role="button" tabindex="0"
             aria-label="${p.name}. ${p.type}. Mood ${Math.round(p.score*100)} out of 100, ${MOOD_LABEL(p.score).toLowerCase()}."
             onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();showPlace('${stateName}', ${i});}"
             onclick="showPlace('${stateName}', ${i})">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
            <span style="font-size:16px;">${p.emoji}</span>
            <span class="region-name">${p.name}</span>
          </div>
          <div style="font-size:11px;color:var(--text2);margin-bottom:6px;">${p.type}</div>
          <div class="mood-bar-wrap">
            <div class="mood-bar"><div class="mood-fill" style="width:${p.score*100}%;background:${MOOD_COLOR(p.score)};"></div></div>
            <div class="mood-label">${MOOD_LABEL(p.score)}</div>
          </div>
        </div>
      `).join("")}
    </div>
  `;
  announce(`${stateName} opened. Modelled activity ${Math.round(s.score * 100)} out of 100, `
    + `${MOOD_LABEL(s.score).toLowerCase()}. ${s.places.length} places listed.`);
}

function showPlace(stateName, placeIdx) {
  const s = MOOD_DATA.states[stateName];
  const p = s.places[placeIdx];
  isPlaying = false;
  stopPlayback();
  currentPlace = p;
  currentPlaceState = stateName;

  updateBreadcrumb(stateName, p.name);

  const panel = document.getElementById("panel-content");
  const barsHtml = waveHeights.map((h, i) => `<div class="wave-bar" style="height:${Math.round(h*28)}px;animation-delay:${(i*0.05).toFixed(2)}s;"></div>`).join("");

  panel.innerHTML = `
    <div class="back-btn" onclick="showStateSide('${stateName}');updateBreadcrumb('${stateName}',null);">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10 12L6 8l4-4"/></svg>
      Back to ${stateName}
    </div>
    <div class="place-header">
      <div class="place-icon" style="background:${MOOD_COLOR(p.score)}22;">${p.emoji}</div>
      <div>
        <div class="place-name">${p.name}</div>
        <div class="place-type">${p.type} · ${stateName}</div>
      </div>
    </div>

    <div class="mood-ring">
      <div class="mood-score" style="color:${MOOD_COLOR(p.score)};">${Math.round(p.score * 100)}</div>
      <div>
        <div style="font-size:13px;font-weight:500;">${MOOD_LABEL(p.score)}</div>
        <div class="mood-desc">${getMoodDesc(p.score, p.name)}</div>
        <div class="pe-badge modelled" style="margin-top:6px;" title="No landmark-level measurement exists for ${p.name}. This score is ${stateName}'s measured regional score, offset by an author judgment of how this specific place compares to others in the region — not an independent measurement of this place.">Illustrative offset, not measured</div>
      </div>
    </div>

    <div class="panel-section">
      <div class="narrative-card">
        <div class="narrative-label">How this became music</div>
        ${buildPlaceNarrative(p, stateName)}
      </div>
    </div>

    ${buildMusicSpecPanel(p, stateName)}

    <div class="panel-section">
      <div class="panel-title">Generated soundscape</div>
      <div class="player">
        <div class="player-top">
          <button class="play-btn" id="play-btn" onclick="togglePlay()" aria-label="Play/pause">
            <svg id="play-icon" viewBox="0 0 16 16"><polygon points="5,3 13,8 5,13" fill="white"/></svg>
          </button>
          <div class="player-info">
            <div class="track-name">${p.name} — ${MOOD_LABEL(p.score)} Mix</div>
            <div class="track-sub">${getSunoBpm(p)} BPM · ${getMusicalKey(p, stateName) === "major key" ? "Major" : "Minor"} key · ${getSunoStyle(p).split(",")[0]}</div>
          </div>
        </div>
        <div class="waveform" id="waveform">${barsHtml}</div>
        <div class="player-params">
          ${p.instrumentation.split(", ").map(t => `<span class="param-tag">${t}</span>`).join("")}
        </div>
        <div id="play-status" style="font-size:11px;color:var(--text2);margin-top:8px;min-height:14px;"></div>
        <button class="suno-toggle" onclick="toggleSunoPanel()">🎶 Generate real music with Suno</button>
        <div id="suno-panel" class="suno-panel" style="display:none;">
          <div class="suno-label">Prompt for this place — paste into Suno:</div>
          <textarea id="suno-prompt" class="suno-prompt" readonly rows="4">${buildSunoPrompt(p, stateName).replace(/</g, "&lt;")}</textarea>
          <div class="suno-btn-row">
            <button id="copy-prompt-btn" class="suno-btn" onclick="copySunoPrompt()">Copy prompt</button>
            <a class="suno-btn" href="https://suno.com/create" target="_blank" rel="noopener">Open Suno ↗</a>
          </div>
          <div class="suno-help">Generate an instrumental in Suno, download the MP3, and save it as <code>audio/${placeKey(stateName, p)}.mp3</code> next to this page — it'll then play automatically. Or set up automatic generation below.</div>

          <button class="suno-toggle" id="ai-predict-btn" onclick="runAIMusicPrediction(${JSON.stringify(stateName)}, ${JSON.stringify(p.name)})" style="margin-top:6px;">🤖 Let AI predict the best music style (uses photo + research data)</button>
          <div id="ai-predict-result" class="suno-help" style="margin-top:6px;"></div>

          <details class="suno-adv">
            <summary>⚡ Fully automatic generation (paste an API key)</summary>
            <div class="suno-adv-body">
              <div class="suno-help" style="margin-top:0;">1. Sign up at <a href="https://sunoapi.org" target="_blank" rel="noopener" style="color:var(--accent);">sunoapi.org</a> (a paid third-party Suno API — Suno itself has no official API) and buy credits.<br>2. Copy your API key from their dashboard and paste it below.<br>3. Leave "API base URL" empty unless you're using a different sunoapi.org-compatible provider.</div>
              <input id="suno-base" class="suno-input" placeholder="API base URL (default: https://api.sunoapi.org)" value="${(getSunoConfig().base || "").replace(/"/g, "&quot;")}">
              <input id="suno-key" class="suno-input" type="password" placeholder="Your sunoapi.org API key" value="${(getSunoConfig().key || "").replace(/"/g, "&quot;")}">
              <button class="suno-btn" onclick="saveSunoKey()">Save key</button>
              <span id="suno-save-status" class="suno-save-status"></span>
              <div class="suno-help">Stored only in your browser (localStorage) — never sent anywhere except sunoapi.org, and never included in this page's code. Once saved, just press ▶ on any place — it generates and plays automatically (~30-90s), no downloading or renaming needed. Each generation spends credits on your account. Streams from their URL rather than saving a local file, so it won't survive that URL expiring — use the download method above for a permanent copy.</div>
            </div>
          </details>
        </div>
      </div>
    </div>

    <div class="panel-section">
      <div class="panel-title">Photo</div>
      <div class="real-photo-card">
        ${p.photo
          ? `<a href="${p.photoPage || p.photo}" target="_blank" rel="noopener"><img src="${p.photo}" alt="${p.name}" class="real-photo" loading="lazy"></a>
             <div class="photo-credit">${p.photoArtist ? "Photo: " + p.photoArtist + (p.photoLicense ? " · " + p.photoLicense : "") : (p.photoLicense || "Wikimedia Commons")} · <a href="${p.photoPage}" target="_blank" rel="noopener">source ↗</a></div>`
          : `<div class="photo-placeholder-static">No free-licensed photo found for this place yet.</div>`
        }
      </div>
      ${p.photos && p.photos.length ? `
      <div class="real-photo-gallery">
        ${p.photos.map(ph => `
          <a href="${ph.page || ph.url}" target="_blank" rel="noopener" class="real-photo-gallery-cell">
            <img src="${ph.url}" alt="${p.name}" loading="lazy">
            <div class="photo-credit">${ph.artist ? "Photo: " + ph.artist : "Wikimedia Commons"}${ph.license ? " · " + ph.license : ""}</div>
          </a>
        `).join("")}
      </div>` : ""}
      <div class="panel-title" style="margin-top:16px;">Add your own photos</div>
      <div class="photo-grid" id="photo-grid">
        ${[0,1].map(i => {
          const key = `${stateName}__${p.name}__${i}`;
          const stored = window._photoStore && window._photoStore[key];
          return `<div class="photo-cell" id="photo-cell-${i}" data-state="${stateName}" data-place="${p.name}" data-slot="${i}" onclick="triggerUpload(this.dataset.state, this.dataset.place, parseInt(this.dataset.slot))">
            ${stored
              ? `<img src="${stored}" class="loaded" alt="Your photo ${i+1}"><div class="photo-edit-hint">📷 tap to change</div>`
              : `<div class="photo-placeholder"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="32" height="32"><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M8 5l1.5-2h5L16 5"/></svg><span>+ Add photo</span></div>`
            }
          </div>`;
        }).join("")}
      </div>
      <input type="file" id="photo-upload-input" accept="image/*" style="display:none" onchange="handlePhotoUpload(event)">
      <div style="font-size:11px;color:var(--text2);margin-top:6px;">Tap a slot to upload a photo you took yourself. Saved for this browser session only.</div>
    </div>

    <div class="panel-section">
      <div class="panel-title">Reviews</div>
      <a class="reviews-card" href="${p.mapsUrl}" target="_blank" rel="noopener">
        <div class="reviews-card-icon">★</div>
        <div>
          <div class="reviews-card-title">See real reviews on Google Maps ↗</div>
          <div class="reviews-card-sub">Opens ${p.name}'s actual Maps listing — reviews aren't reproduced here since they're other people's copyrighted text.</div>
        </div>
      </a>
    </div>
  `;

  announce(`${p.name}. ${p.type}. Mood ${Math.round(p.score * 100)} out of 100, `
    + `${MOOD_LABEL(p.score).toLowerCase()}. Soundscape: ${getSunoBpm(p)} BPM, ${getMusicalKey(p, stateName)}.`);

  // Render "Ask a Local" chat interface (Gemini Integration)
  const persona = getLocalPersona(stateName, p);
  const geminiConfig = getGeminiConfig();
  const hasKey = !!geminiConfig.key;
  const keyEscaped = (geminiConfig.key || "").replace(/"/g, "&quot;");

  const chatKey = `${stateName}__${p.name}`;
  if (!chatHistory[chatKey]) {
    chatHistory[chatKey] = [{ role: "local", text: persona.greeting }];
  }

  const historyHtml = chatHistory[chatKey].map(m => `
    <div class="chat-bubble ${m.role === 'user' ? 'user' : 'local'}">
      ${m.role === 'local' ? `<span>${persona.avatar}</span> ` : ''}${m.text.replace(/</g, "&lt;")}
    </div>
  `).join("");

  const chatHtml = `
    <div class="chat-section">
      <div class="chat-header">
        <div class="chat-header-avatar">${persona.avatar}</div>
        <div class="chat-header-info">
          <div class="chat-header-name">Ask a Local: ${persona.name}</div>
          <div class="chat-header-status">● Online</div>
        </div>
      </div>
      <div class="chat-box" id="chat-box">
        ${historyHtml}
      </div>
      
      <div id="chat-key-area" class="chat-key-prompt" style="display: ${hasKey ? 'none' : 'flex'}">
        <p>🔑 To chat, please paste your Gemini API key (from Google AI Studio):</p>
        <div class="chat-key-input-row">
          <input type="password" id="gemini-key-input" class="chat-key-input" placeholder="Paste your API key here..." value="${keyEscaped}">
          <button class="chat-key-save-btn" onclick="saveGeminiKey()">Save</button>
        </div>
        <span id="gemini-save-status" class="chat-key-save-status"></span>
      </div>

      <div class="chat-input-row" style="display: ${hasKey ? 'flex' : 'none'}" id="chat-input-area">
        <input type="text" id="chat-user-input" class="chat-input" placeholder="Ask something about this place..." onkeydown="handleChatKeyDown(event)">
        <button class="chat-send-btn" onclick="sendChatMessage()">Send</button>
      </div>

      <button class="chat-settings-toggle" onclick="toggleGeminiSettings()" id="chat-settings-link" style="display: ${hasKey ? 'inline-block' : 'none'}">⚙️ Edit API Key</button>
    </div>
  `;

  // Append chat HTML to side panel content
  panel.innerHTML += chatHtml;

  // Scroll chat box to bottom
  const chatBox = document.getElementById("chat-box");
  if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
}

// ── PHOTO UPLOAD ──────────────────────────────────────────────────────────────
window._photoStore = {};
let _uploadTarget = null;

function triggerUpload(stateName, placeName, slotIndex) {
  _uploadTarget = { stateName, placeName, slotIndex };
  document.getElementById("photo-upload-input").click();
}

function handlePhotoUpload(event) {
  const file = event.target.files[0];
  if (!file || !_uploadTarget) return;
  const { stateName, placeName, slotIndex } = _uploadTarget;
  const key = `${stateName}__${placeName}__${slotIndex}`;
  const reader = new FileReader();
  reader.onload = (e) => {
    window._photoStore[key] = e.target.result;
    const cell = document.getElementById(`photo-cell-${slotIndex}`);
    if (cell) {
      cell.innerHTML = `<img src="${e.target.result}" class="loaded" alt="Photo ${slotIndex+1}">`;
    }
  };
  reader.readAsDataURL(file);
  event.target.value = "";
}

function updateBreadcrumb(state, place) {
  const bc = document.getElementById("breadcrumb");
  let html = `<span onclick="goCountry()">South Korea</span>`;
  if (state) html += `<span class="sep">›</span><span onclick="showStateSide('${state}');updateBreadcrumb('${state}',null);">${state}</span>`;
  if (place) html += `<span class="sep">›</span><span>${place}</span>`;
  bc.innerHTML = html;
}

function goCountry() {
  currentState = null;
  currentPlace = null;
  currentPlaceState = null;
  isPlaying = false;
  stopPlayback();
  svg.selectAll(".region-path").classed("active", false);
  document.getElementById("panel-content").innerHTML = `<div class="empty"><div class="big">🗺️</div><p>Hover over a province to preview its vibe.<br>Click to dive into places.</p><div class="byok-notice"><b>Free to explore, no setup needed.</b> The map, modelled scores, real photos, and a synth soundscape all work instantly. Two optional AI features — the "Ask a Local" chat and AI-generated music — need your own free/paid API key (Gemini / Suno), entered when you try them.</div><div class="byok-notice"><b>Research status.</b> Province scores now run from a transparent composite of official density, tourism, noise and visitor-survey data. The weights are documented hypotheses, not learned coefficients or measured ISO Eventfulness. Open any province's calculation and see <a href="about.html" style="color:var(--accent);">About &amp; research</a> for limitations.</div></div>`;
  document.getElementById("breadcrumb").innerHTML = `<span onclick="goCountry()">South Korea</span>`;
  hint.style.display = "block";
}

// ── SEARCH ────────────────────────────────────────────────────────────────────
const searchIndex = [];
Object.entries(MOOD_DATA.states).forEach(([state, data]) => {
  searchIndex.push({ label: state, sub: data.desc, type: "state", state });
  data.places.forEach((p, i) => {
    searchIndex.push({ label: p.name, sub: `${p.type} · ${state}`, type: "place", state, idx: i });
  });
});

const searchInput = document.getElementById("search-input");
const searchResults = document.getElementById("search-results");

searchInput.addEventListener("input", () => {
  const q = searchInput.value.trim().toLowerCase();
  if (!q) { searchResults.classList.remove("open"); return; }
  const hits = searchIndex.filter(x => x.label.toLowerCase().includes(q) || x.sub.toLowerCase().includes(q)).slice(0, 6);
  if (!hits.length) { searchResults.classList.remove("open"); return; }
  searchResults.innerHTML = hits.map((h, i) => `
    <div class="search-item" data-i="${i}">
      ${h.label}
      <div class="sub">${h.sub}</div>
    </div>
  `).join("");
  searchResults.classList.add("open");
  searchResults.querySelectorAll(".search-item").forEach((el, i) => {
    el.addEventListener("click", () => {
      const h = hits[i];
      searchInput.value = "";
      searchResults.classList.remove("open");
      svg.selectAll(".region-path").classed("active", n => {
        return false;
      });
      if (h.type === "state") {
        svg.selectAll(".region-path").filter(d => d && d.properties && d.properties.name === h.state).classed("active", true);
        showStateSide(h.state);
        updateBreadcrumb(h.state, null);
        currentState = h.state;
      } else {
        showPlace(h.state, h.idx);
        currentState = h.state;
      }
      hint.style.display = "none";
    });
  });
});

document.addEventListener("click", e => {
  if (!e.target.closest(".search-wrap")) searchResults.classList.remove("open");
});

// ── CHAT FUNCTIONS ────────────────────────────────────────────────────────────

function saveGeminiKey() {
  const key = (document.getElementById("gemini-key-input").value || "").trim();
  const cfg = getGeminiConfig();
  cfg.key = key;
  saveGeminiConfig(cfg);
  
  const status = document.getElementById("gemini-save-status");
  if (status) {
    status.textContent = "Saved ✓";
    setTimeout(() => status.textContent = "", 2000);
  }
  
  if (key) {
    document.getElementById("chat-key-area").style.display = "none";
    document.getElementById("chat-input-area").style.display = "flex";
    document.getElementById("chat-settings-link").style.display = "inline-block";
  }
}

function toggleGeminiSettings() {
  const area = document.getElementById("chat-key-area");
  if (area.style.display === "none") {
    area.style.display = "flex";
  } else {
    area.style.display = "none";
  }
}

function handleChatKeyDown(event) {
  if (event.key === "Enter") {
    sendChatMessage();
  }
}

// ── LANGUAGE ACCESSIBILITY UI ──────────────────────────────────────────────────

function renderLanguageScoreArea(stateName) {
  const language = getSelectedLanguage();
  const cache = getLanguageScoreCache();
  const cached = cache[languageScoreKey(stateName, language)];
  const cfg = getGeminiConfig();

  if (cached) {
    return `
      <div class="lang-score-card">
        <div class="lang-score-num">${cached.score}<span>/100</span></div>
        <div class="lang-score-body">
          <div class="lang-score-label">${cached.label} — ${language}</div>
          <div class="lang-score-reason">${cached.reasoning.replace(/</g, "&lt;")}</div>
        </div>
      </div>
      <button class="suno-toggle" style="margin-top:8px;" onclick="runLanguageProficiencyEstimate('${stateName}')">🔁 Re-estimate</button>
    `;
  }

  if (cfg.key) {
    return `<button class="suno-toggle" onclick="runLanguageProficiencyEstimate('${stateName}')">🌐 Estimate ${language} accessibility via AI</button>`;
  }

  const keyEscaped = (cfg.key || "").replace(/"/g, "&quot;");
  return `
    <div class="suno-help" style="margin-top:0;margin-bottom:6px;">Computed live via the same Gemini key used by "Ask a Local" &amp; AI music prediction — free tier available at <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener" style="color:var(--accent);">Google AI Studio</a>.</div>
    <input id="lang-gemini-key-input" class="suno-input" type="password" placeholder="Paste your Gemini API key…" value="${keyEscaped}" style="width:100%;margin-bottom:6px;">
    <button class="suno-btn" onclick="saveLanguageGeminiKey('${stateName}')">Save &amp; estimate</button>
  `;
}

function onLanguageChange(stateName) {
  const sel = document.getElementById("lang-select");
  const cfg = getLanguageConfig();
  cfg.language = sel.value;
  saveLanguageConfig(cfg);
  const resultEl = document.getElementById("lang-score-result");
  if (resultEl) resultEl.innerHTML = renderLanguageScoreArea(stateName);
}

function saveLanguageGeminiKey(stateName) {
  const input = document.getElementById("lang-gemini-key-input");
  const key = (input && input.value || "").trim();
  if (!key) return;
  const cfg = getGeminiConfig();
  cfg.key = key;
  saveGeminiConfig(cfg);
  runLanguageProficiencyEstimate(stateName);
}

async function runLanguageProficiencyEstimate(stateName) {
  const language = getSelectedLanguage();
  const cfg = getGeminiConfig();
  const resultEl = document.getElementById("lang-score-result");
  if (!cfg.key) return;

  if (resultEl) resultEl.innerHTML = `<div class="suno-help" style="margin-top:0;">🤖 Estimating ${language} accessibility for ${stateName}…</div>`;
  try {
    const prediction = await predictLanguageProficiencyWithAI(stateName, language, cfg.key);
    cacheLanguageScore(languageScoreKey(stateName, language), prediction);
    if (resultEl) resultEl.innerHTML = renderLanguageScoreArea(stateName);
  } catch (e) {
    if (resultEl) resultEl.innerHTML = `<div class="suno-help" style="margin-top:0;color:#ff6c6c;">Estimate failed: ${e.message}</div>`;
  }
}

// ── AI MUSIC-STYLE PREDICTION UI ──────────────────────────────────────────────
async function runAIMusicPrediction(stateName, placeName) {
  const s = MOOD_DATA.states[stateName];
  const place = s && s.places.find(pl => pl.name === placeName);
  if (!place) return;

  const cfg = getGeminiConfig();
  const resultEl = document.getElementById("ai-predict-result");
  const btn = document.getElementById("ai-predict-btn");

  if (!cfg.key) {
    if (resultEl) resultEl.innerHTML = `⚠️ This needs a Gemini API key — the same one used for "Ask a Local" chat. Scroll up to that section, paste a key there, then try again.`;
    return;
  }

  btn.disabled = true;
  const originalText = btn.textContent;
  btn.textContent = "🤖 Analyzing photo + research data…";
  if (resultEl) resultEl.textContent = "";

  try {
    const prediction = await predictMusicStyleWithAI(place, stateName, cfg.key);
    const newPrompt = buildSunoPromptFromAIPrediction(place, stateName, prediction);
    const promptArea = document.getElementById("suno-prompt");
    if (promptArea) promptArea.value = newPrompt;

    if (resultEl) {
      resultEl.innerHTML = `<b>AI prediction:</b> ${prediction.genre} (${prediction.mood_descriptors}), ${prediction.tempo_feel}, ${prediction.key}.<br>`
        + `<b>Instrumentation:</b> ${prediction.instrumentation}<br>`
        + `<i>${prediction.reasoning}</i><br>`
        + `<span style="color:var(--accent);">Suno prompt above updated with this prediction.</span>`;
    }
  } catch (e) {
    if (resultEl) resultEl.textContent = "AI prediction failed: " + e.message;
  } finally {
    btn.disabled = false;
    btn.textContent = originalText;
  }
}

async function sendChatMessage() {
  const input = document.getElementById("chat-user-input");
  if (!input) return;
  const question = input.value.trim();
  if (!question) return;

  const place = currentPlace;
  const stateName = currentPlaceState;
  if (!place || !stateName) return;

  const chatKey = `${stateName}__${place.name}`;
  const persona = getLocalPersona(stateName, place);
  const cfg = getGeminiConfig();
  
  if (!cfg.key) {
    alert("Please enter a Gemini API Key first.");
    return;
  }

  // 1. Add user bubble to history & screen
  chatHistory[chatKey].push({ role: "user", text: question });
  input.value = "";
  
  const chatBox = document.getElementById("chat-box");
  if (!chatBox) return;

  const userBubble = document.createElement("div");
  userBubble.className = "chat-bubble user";
  userBubble.textContent = question;
  chatBox.appendChild(userBubble);
  chatBox.scrollTop = chatBox.scrollHeight;

  // 2. Add typing indicator bubble
  const typingIndicator = document.createElement("div");
  typingIndicator.className = "typing-indicator";
  typingIndicator.id = "chat-typing-indicator";
  typingIndicator.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
  chatBox.appendChild(typingIndicator);
  chatBox.scrollTop = chatBox.scrollHeight;

  // 3. Make the API Call to Gemini
  try {
    const answer = await askGeminiLocal(question, place, stateName, cfg.key);
    
    // Remove typing indicator
    const indicatorEl = document.getElementById("chat-typing-indicator");
    if (indicatorEl) indicatorEl.remove();

    // Add local response bubble to history & screen
    chatHistory[chatKey].push({ role: "local", text: answer });
    
    const localBubble = document.createElement("div");
    localBubble.className = "chat-bubble local";
    localBubble.innerHTML = `<span>${persona.avatar}</span> ${answer.replace(/</g, "&lt;")}`;
    chatBox.appendChild(localBubble);
    chatBox.scrollTop = chatBox.scrollHeight;
  } catch (e) {
    // Remove typing indicator
    const indicatorEl = document.getElementById("chat-typing-indicator");
    if (indicatorEl) indicatorEl.remove();

    // Display error bubble
    const errorBubble = document.createElement("div");
    errorBubble.className = "chat-bubble local";
    errorBubble.style.color = "#ff6c6c";
    errorBubble.innerHTML = `<span>⚠️</span> Sorry, I couldn't connect. Error: ${e.message}`;
    chatBox.appendChild(errorBubble);
    chatBox.scrollTop = chatBox.scrollHeight;
  }
}

// ── ACCESSIBILITY TEXT-TO-SPEECH (TTS) ───────────────────────────────────────

function vocalizeTactileState(stateKey) {
  if (!window.speechSynthesis) return;

  // Stop any current voice output
  window.speechSynthesis.cancel();

  const s = MOOD_DATA.states[stateKey];
  if (!s) return;

  // Compile high-quality descriptive text for the screen reader
  const text = `${stateKey}. Atmosphere is ${MOOD_LABEL(s.score)}. Score: ${Math.round(s.score * 100)}. Description: ${s.desc}. Press Enter or Space to explore places.`;

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  utterance.rate = 1.05; // Slightly faster for high responsiveness
  window.speechSynthesis.speak(utterance);
}
