'use strict';
const ATTRIBUTES = ['pleasant', 'chaotic', 'vibrant', 'uneventful', 'calm', 'annoying', 'eventful', 'monotonous'];
const FIELDS = ['protocol_version', 'stimulus_version', 'participant_id', 'consent_utc', 'clip_id', 'clip_sha256',
  'presentation_order', 'clip_duration_seconds', 'listened_seconds', 'response_seconds', ...ATTRIBUTES.map(a => a + '_1_5')];
let config, state, activeClip, listened = 0, trialStarted = 0, clipsVerified = false;
const $ = id => document.getElementById(id);
const status = text => { $('status').textContent = text; };
const storageKey = () => 'moodscape_listener_' + config.version;
const save = () => {
  try { localStorage.setItem(storageKey(), JSON.stringify(state)); }
  catch { status('Browser storage is unavailable. Keep this page open and download your responses before leaving.'); }
};
function shuffle(items) {
  const out = [...items];
  for (let i = out.length - 1; i > 0; i--) {
    // Rejection sampling avoids modulo bias and records the actual order in state.
    const limit = Math.floor(4294967296 / (i + 1)) * (i + 1);
    let n; do { n = crypto.getRandomValues(new Uint32Array(1))[0]; } while (n >= limit);
    const j = n % (i + 1); [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}
function csvCell(value) {
  let text = String(value ?? '');
  if (/^[=+@\-]/.test(text)) text = "'" + text;
  return '"' + text.replaceAll('"', '""') + '"';
}
function download() {
  if (!state?.rows.length) return;
  const text = [FIELDS, ...state.rows.map(r => FIELDS.map(f => r[f]))].map(row => row.map(csvCell).join(',')).join('\r\n') + '\r\n';
  const url = URL.createObjectURL(new Blob([text], {type: 'text/csv;charset=utf-8'}));
  const link = document.createElement('a'); link.href = url;
  link.download = `moodscape-listener-${state.participant_id}.csv`; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function showTrial() {
  $('consent-panel').hidden = true;
  $('download').disabled = !state.rows.length;
  if (state.rows.length === state.order.length) {
    $('trial').hidden = true; $('complete').hidden = false; $('clip').pause();
    status('All clips rated. Download your responses to share them.'); return;
  }
  $('trial').hidden = false;
  activeClip = config.clips.find(c => c.id === state.order[state.rows.length]);
  listened = 0; trialStarted = performance.now();
  $('ratings').reset(); $('next').disabled = true;
  $('trial-title').textContent = `Clip ${state.rows.length + 1} of ${state.order.length}`;
  $('clip').src = activeClip.src; $('clip').load();
  $('trial-title').focus(); status('Play the clip, then rate all eight attributes.');
}
function updateListening() {
  const audio = $('clip');
  listened = 0;
  for (let i = 0; i < audio.played.length; i++) listened += audio.played.end(i) - audio.played.start(i);
  // Seeking to the end alone does not qualify as listening.
  $('next').disabled = !activeClip || listened < activeClip.duration_seconds - 0.25;
}
$('attributes').innerHTML = ATTRIBUTES.map(attr => `<fieldset><legend>${attr[0].toUpperCase()+attr.slice(1)}</legend><div class="ratings">${[1,2,3,4,5].map(n => `<label><input type="radio" name="${attr}" value="${n}" required>${n}</label>`).join('')}</div></fieldset>`).join('');
$('consent').addEventListener('change', () => { $('start').disabled = !clipsVerified || !$('consent').checked; });
$('start').addEventListener('click', () => {
  if (!$('consent').checked || !clipsVerified) return;
  if (!state) state = {participant_id: crypto.randomUUID(), consent_utc: new Date().toISOString(), order: shuffle(config.clips.map(c => c.id)), rows: []};
  save(); showTrial();
});
$('ratings').addEventListener('submit', event => {
  event.preventDefault(); updateListening();
  if ($('next').disabled || !$('ratings').reportValidity()) return;
  const row = {protocol_version: config.protocol_version, stimulus_version: config.version,
    participant_id: state.participant_id, consent_utc: state.consent_utc,
    clip_id: activeClip.id, clip_sha256: activeClip.sha256, presentation_order: state.rows.length + 1,
    clip_duration_seconds: activeClip.duration_seconds, listened_seconds: listened.toFixed(3),
    response_seconds: ((performance.now() - trialStarted) / 1000).toFixed(3)};
  const answers = new FormData($('ratings'));
  ATTRIBUTES.forEach(a => { row[a + '_1_5'] = Number(answers.get(a)); });
  state.rows.push(row); save(); showTrial();
});
['timeupdate', 'ended', 'pause'].forEach(event => $('clip').addEventListener(event, updateListening));
$('clip').addEventListener('error', () => { $('next').disabled = true; status('This clip could not be loaded. Please tell the researcher; no rating for it has been saved.'); });
$('download').addEventListener('click', download);
$('erase').addEventListener('click', () => {
  if (!confirm('Delete this session’s saved responses? Download them first if you want a copy.')) return;
  if (config) localStorage.removeItem(storageKey());
  state = null; $('clip').pause(); $('trial').hidden = true; $('complete').hidden = true;
  $('consent-panel').hidden = false; $('consent').checked = false; $('start').disabled = true; $('download').disabled = true;
  status('Saved responses deleted.');
});
fetch('listener_stimuli.json').then(r => { if (!r.ok) throw new Error(); return r.json(); }).then(async data => {
  config = data;
  if (!data.ready) { status('Study preparation is pending: verified real music clips have not been installed. Responses cannot be collected yet.'); return; }
  if (data.clips.length < 8 || data.clips.length > 10 || new Set(data.clips.map(c => c.id)).size !== data.clips.length) throw new Error();
  // Verify every neutral clip before collecting consent/ratings. No silent replacement stimuli.
  for (const clip of data.clips) {
    if (!/^[a-f0-9]{64}$/.test(clip.sha256) || clip.duration_seconds !== 25) throw new Error();
    const response = await fetch(clip.src); if (!response.ok) throw new Error();
    const digest = await crypto.subtle.digest('SHA-256', await response.arrayBuffer());
    const hex = [...new Uint8Array(digest)].map(x => x.toString(16).padStart(2, '0')).join('');
    if (hex !== clip.sha256) throw new Error();
  }
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey()) || 'null');
    if (saved && saved.order?.length === data.clips.length && new Set(saved.order).size === data.clips.length &&
        saved.order.every(id => data.clips.some(c => c.id === id)) && Array.isArray(saved.rows) &&
        saved.rows.length <= data.clips.length && saved.rows.every((r,i) => r.clip_id === saved.order[i] &&
          r.clip_sha256 === data.clips.find(c => c.id === r.clip_id).sha256 && ATTRIBUTES.every(a => Number.isInteger(r[a+'_1_5']) && r[a+'_1_5'] >= 1 && r[a+'_1_5'] <= 5))) {
      state = saved; $('start').textContent = 'Resume listening'; $('download').disabled = !state.rows.length;
    }
  } catch { /* An unreadable saved session is not valid data. */ }
  clipsVerified = true;
  status('Clips checked. Read the consent information to begin.');
  $('start').disabled = !$('consent').checked;
}).catch(() => { if (config) config.ready = false; $('start').disabled = true; status('Study files are missing, changed, or invalid. Ask the researcher to check the stimulus files before starting.'); });
