// ── MOOD SCAPE USER INTERFACE & NAVIGATION ─────────────────────────────────────

function showStateSide(stateName) {
  const s = MOOD_DATA.states[stateName];
  isPlaying = false;
  stopPlayback();
  currentPlace = null;
  currentPlaceState = null;
  const panel = document.getElementById("panel-content");
  panel.innerHTML = `
    <div class="panel-section">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
        <div style="font-size:28px;">${s.emoji}</div>
        <div>
          <div style="font-size:16px;font-weight:600;">${stateName}</div>
          <div style="font-size:12px;color:var(--text2);">${s.desc}</div>
        </div>
      </div>
      <div class="mood-bar-wrap" style="margin-bottom:4px;">
        <div style="font-size:11px;color:var(--text2);width:60px;">Mood</div>
        <div class="mood-bar"><div class="mood-fill" style="width:${s.score*100}%;background:${MOOD_COLOR(s.score)};"></div></div>
        <div class="mood-label">${MOOD_LABEL(s.score)}</div>
      </div>
    </div>
    <div class="panel-section">
      <div class="panel-title">Places to explore</div>
      ${s.places.map((p, i) => `
        <div class="region-card" onclick="showPlace('${stateName}', ${i})">
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
      </div>
    </div>

    <div class="panel-section">
      <div class="panel-title">Generated soundscape</div>
      <div class="player">
        <div class="player-top">
          <button class="play-btn" id="play-btn" onclick="togglePlay()" aria-label="Play/pause">
            <svg id="play-icon" viewBox="0 0 16 16"><polygon points="5,3 13,8 5,13" fill="white"/></svg>
          </button>
          <div class="player-info">
            <div class="track-name">${p.name} — ${MOOD_LABEL(p.score)} Mix</div>
            <div class="track-sub">${Math.round(40 + p.score * 80)} BPM · ${getMusicalKey(p) === "major key" ? "Major" : "Minor"} key · ${getSunoStyle(p).split(",")[0]}</div>
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
  document.getElementById("panel-content").innerHTML = `<div class="empty"><div class="big">🗺️</div><p>Hover over a province to preview its vibe.<br>Click to dive into places.</p></div>`;
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
