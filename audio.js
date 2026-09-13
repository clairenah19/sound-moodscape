// ── MOOD SCAPE AUDIO PLAYBACK & VISUALIZER ─────────────────────────────────────

let audioCtx = null;
let analyserNode = null;
let animFrameId = null;
let syntheticInterval = null;
let currentAudioEl = null;
let currentMediaSource = null;

function getAudioCtx() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    analyserNode = audioCtx.createAnalyser();
    analyserNode.fftSize = 64;
  }
  return audioCtx;
}

function stopPlayback() {
  if (animFrameId) { cancelAnimationFrame(animFrameId); animFrameId = null; }
  if (syntheticInterval) { clearInterval(syntheticInterval); syntheticInterval = null; }
  if (currentAudioEl) {
    try { currentAudioEl.pause(); } catch (e) {}
    if (currentMediaSource) { try { currentMediaSource.disconnect(); } catch (e) {} currentMediaSource = null; }
    currentAudioEl = null;
  }
}

function setPlayButtonUI(playing) {
  const bars = document.querySelectorAll(".wave-bar");
  const icon = document.getElementById("play-icon");
  if (!icon) return;
  if (playing) {
    bars.forEach(b => b.classList.add("playing"));
    icon.innerHTML = '<rect x="4" y="3" width="3" height="10" fill="white"/><rect x="9" y="3" width="3" height="10" fill="white"/>';
  } else {
    bars.forEach(b => { b.classList.remove("playing"); });
    icon.innerHTML = '<polygon points="5,3 13,8 5,13" fill="white"/>';
  }
}

function animateWaveform() {
  const bars = document.querySelectorAll(".wave-bar");
  const data = new Uint8Array(analyserNode.frequencyBinCount);
  function tick() {
    if (!isPlaying) return;
    analyserNode.getByteFrequencyData(data);
    bars.forEach((b, i) => {
      const v = data[i % data.length] / 255;
      b.style.height = Math.max(4, Math.round(v * 28)) + "px";
    });
    animFrameId = requestAnimationFrame(tick);
  }
  tick();
}

function animateWaveformSynthetic() {
  const bars = document.querySelectorAll(".wave-bar");
  syntheticInterval = setInterval(() => {
    if (!isPlaying) { clearInterval(syntheticInterval); return; }
    bars.forEach(b => { b.style.height = Math.round(4 + Math.random() * 26) + "px"; });
  }, 140);
}

function isSameOrigin(url) {
  try { return new URL(url, location.href).origin === location.origin; }
  catch (e) { return false; }
}

function playAudioUrl(url) {
  return new Promise((resolve, reject) => {
    const ctx = getAudioCtx();
    if (ctx.state === "suspended") ctx.resume();
    const audio = new Audio();
    audio.src = url;
    audio.preload = "auto";
    currentAudioEl = audio;
    let usedAnalyser = false;

    audio.addEventListener("playing", () => {
      if (isSameOrigin(url) && !currentMediaSource) {
        try {
          currentMediaSource = ctx.createMediaElementSource(audio);
          currentMediaSource.connect(analyserNode);
          analyserNode.connect(ctx.destination);
          usedAnalyser = true;
          animateWaveform();
        } catch (e) {
          animateWaveformSynthetic();
        }
      } else if (!usedAnalyser) {
        animateWaveformSynthetic();
      }
      resolve("file");
    }, { once: true });

    audio.addEventListener("ended", () => {
      isPlaying = false;
      setPlayButtonUI(false);
    });
    audio.addEventListener("error", () => reject(new Error("audio load failed: " + url)));
    audio.play().catch(reject);
  });
}

function setPlayStatus(msg, downloadUrl) {
  const el = document.getElementById("play-status");
  if (!el) return;
  if (downloadUrl && downloadUrl.startsWith("http")) {
    const filename = `${placeKey(currentPlaceState, currentPlace)}.mp3`;
    el.innerHTML = `${msg} <a href="${downloadUrl}" target="_blank" download="${filename}" style="color:var(--accent);text-decoration:underline;margin-left:8px;font-weight:500;">Download MP3 ↗</a>`;
  } else {
    el.textContent = msg || "";
  }
}

async function playCurrentSoundscape() {
  const place = currentPlace, stateName = currentPlaceState;
  if (!place) return;
  const key = placeKey(stateName, place);

  // 1a. cached resolved URL
  const cached = getTrackCache()[key];
  // 1b. hosted URL manifest
  const hosted = window.SUNO_TRACKS[key];
  // 1c. local convention
  const local = "audio/" + key + ".mp3";

  let url = cached || hosted || local;

  const isHosted = url.startsWith("http");
  setPlayStatus("Playing real track…", isHosted ? url : null);
  try {
    await playAudioUrl(url);
    cacheTrackUrl(key, url);
    return;
  } catch (e) {
    setPlayStatus("Track failed to load — trying other sources…");
  }

  // 2. live API
  const cfg = getSunoConfig();
  if (cfg.key) {
    setPlayStatus("Generating with Suno… this can take a minute.");
    try {
      const genUrl = await sunoGenerate(place, stateName, cfg);
      cacheTrackUrl(key, genUrl);
      setPlayStatus("Playing generated track…", genUrl);
      await playAudioUrl(genUrl);
      return;
    } catch (e) {
      setPlayStatus("Suno generation failed (" + e.message + ").");
    }
  } else {
    setPlayStatus("No real track found. Please generate music or upload an MP3 file to audio/ folder.");
  }

  isPlaying = false;
  setPlayButtonUI(false);
}

function togglePlay() {
  if (!currentPlace) return;
  isPlaying = !isPlaying;
  if (isPlaying) {
    setPlayButtonUI(true);
    playCurrentSoundscape();
  } else {
    stopPlayback();
    setPlayButtonUI(false);
    setPlayStatus("");
  }
}

// ── WEBAUDIO TACTILE CUES ────────────────────────────────────────────────────
let tactileAudioCtx = null;

// Semitone offsets of a two-octave pentatonic scale. Successive scores land on
// scale degrees rather than arbitrary chromatic steps, so moving across the map
// reads as a melodic contour instead of a random sweep — the point is that the
// listener can hear which region is more active, not just that focus moved.
const TICK_SCALE = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24];
const TICK_ROOT_HZ = 220; // A3

// The reformed activity proxy deliberately combines several variables, so real
// regional scores span roughly 0.33–0.61 rather than the full 0–1. Mapping the
// theoretical range would collapse all 17 regions onto four pitches — nine of
// them identical — and the contour would be unhearable. Stretching across the
// observed spread instead keeps every region distinguishable. Recomputed lazily
// so it still holds if the underlying scores change.
let _scoreDomain = null;
function regionScoreDomain() {
  if (_scoreDomain) return _scoreDomain;
  const scores = Object.values(MOOD_DATA.states).map(s => s.score).filter(isFinite);
  if (!scores.length) return (_scoreDomain = { lo: 0, hi: 1 });
  const lo = Math.min(...scores), hi = Math.max(...scores);
  return (_scoreDomain = (hi - lo < 0.05) ? { lo: 0, hi: 1 } : { lo, hi });
}

function pitchForScore(score, domain) {
  const d = domain || regionScoreDomain();
  const span = d.hi - d.lo || 1;
  const s = Math.max(0, Math.min(1, (Number(score) - d.lo) / span));
  const degree = TICK_SCALE[Math.round(s * (TICK_SCALE.length - 1))];
  return TICK_ROOT_HZ * Math.pow(2, degree / 12);
}

// `score` (0–1) makes the cue carry the region's modelled activity. Passing null
// keeps the original fixed-pitch cue for contexts with no score behind them.
function playTactileTick(isNode = false, score = null) {
  try {
    if (!tactileAudioCtx) {
      tactileAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (tactileAudioCtx.state === 'suspended') {
      tactileAudioCtx.resume();
    }
    const osc = tactileAudioCtx.createOscillator();
    const gainNode = tactileAudioCtx.createGain();
    osc.connect(gainNode);
    gainNode.connect(tactileAudioCtx.destination);

    const hasScore = typeof score === "number" && isFinite(score);
    const now = tactileAudioCtx.currentTime;

    if (isNode) {
      // Landing on a region: sustained sine, an octave up so selection reads as
      // distinct from browsing while still being the same note of the same data.
      osc.type = "sine";
      osc.frequency.setValueAtTime(hasScore ? pitchForScore(score) * 2 : 880, now);
      gainNode.gain.setValueAtTime(0.08, now);
      gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
      osc.start();
      osc.stop(now + 0.12);
    } else {
      // Browsing: short triangle click at the region's own pitch.
      osc.type = "triangle";
      osc.frequency.setValueAtTime(hasScore ? pitchForScore(score) : 320, now);
      gainNode.gain.setValueAtTime(0.15, now);
      gainNode.gain.exponentialRampToValueAtTime(0.001, now + (hasScore ? 0.09 : 0.04));
      osc.start();
      osc.stop(now + (hasScore ? 0.09 : 0.04));
    }
  } catch (e) {
    console.error("Tactile audio cue error:", e);
  }
}
