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
