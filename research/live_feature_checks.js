'use strict';
const byId = id => document.getElementById(id);
const gangnam = MOOD_DATA.states.Seoul.places.find(p => p.name === 'Gangnam');
const log = ['# Moodscape live checks', '', 'Started: ' + new Date().toISOString(), ''];
const append = text => { log.push(text); byId('report').textContent = log.join('\n'); };
const redact = error => {
  let message = String(error.message || error);
  [getGeminiConfig().key, getSunoConfig().key].filter(Boolean).forEach(key => { message = message.replaceAll(key, '[REDACTED]'); });
  return message.slice(0, 500);
};
byId('key-status').textContent = 'Gemini key: ' + (getGeminiConfig().key ? 'available' : 'not found') + '. Suno key: ' + (getSunoConfig().key ? 'available' : 'not found') + '.';
byId('gemini-check').addEventListener('click', async () => {
  const key = getGeminiConfig().key;
  if (!key) { append('Gemini features: BLOCKED — no saved key on this origin.'); return; }
  byId('gemini-check').disabled = true;
  const checks = [
    ['Ask a Local', () => askGeminiLocal('What kind of atmosphere should a visitor expect here?', gangnam, 'Seoul', key), r => typeof r === 'string' && r.trim().length > 0],
    ['Music-style prediction', () => predictMusicStyleWithAI(gangnam, 'Seoul', key), r => ['genre','instrumentation','key','root_note','mood_descriptors','arrangement','reasoning'].every(k => typeof r[k] === 'string' && r[k].trim()) && Number.isInteger(r.bpm) && r.bpm === getSunoBpm(gangnam) && r.key === getMusicalKey(gangnam, 'Seoul') && r.root_note === getSunoRootNote(gangnam)],
    ...['Japanese', 'Mandarin Chinese'].map(language => ['Language accessibility (' + language + ')', () => predictLanguageProficiencyWithAI('Seoul', language, key), r => Number.isInteger(r.score) && r.score >= 0 && r.score <= 100 && !!r.label && !!r.reasoning])
  ];
  for (const [name, call, valid] of checks) {
    byId('status').textContent = 'Testing ' + name + '…';
    try { const result = await call(); append(name + ': ' + (valid(result) ? 'PASS — live response has the required shape.' : 'FAIL — response shape invalid.')); }
    catch (error) { append(name + ': FAIL — ' + redact(error)); }
  }
  byId('status').textContent = 'Gemini checks finished. This checks live service responses; also exercise the main-page controls.';
  byId('gemini-check').disabled = false;
});
let generatedUrl = null;
byId('suno-check').addEventListener('click', async () => {
  const cfg = getSunoConfig();
  if (!cfg.key) { append('Gangnam generation: BLOCKED — no saved Suno key on this origin.'); return; }
  if (getMusicalKey(gangnam, 'Seoul') !== 'minor key') { append('Gangnam generation: FAIL — intended mode is no longer minor.'); return; }
  byId('suno-check').disabled = true; // One request per visit; no accidental repeated spending.
  append('Gangnam intended prompt: ' + buildSunoPrompt(gangnam, 'Seoul'));
  byId('status').textContent = 'Generating one real Gangnam track…';
  try {
    generatedUrl = await sunoGenerate(gangnam, 'Seoul', cfg);
    const parsed = new URL(generatedUrl);
    if (!['http:', 'https:'].includes(parsed.protocol)) throw new Error('Invalid audio URL');
    cacheTrackUrl(placeKey('Seoul', gangnam), generatedUrl);
    byId('track').src = generatedUrl; byId('track').hidden = false;
    byId('track-link').href = generatedUrl; byId('track-link').hidden = false;
    append('Gangnam generation: PASS — returned audio URL. Listening judgment remains PENDING.');
    byId('status').textContent = 'Play the actual track and record the mode check.';
  } catch (error) { append('Gangnam generation: FAIL — ' + redact(error)); byId('status').textContent = 'Generation did not complete.'; }
});
byId('track').addEventListener('timeupdate', () => {
  let seconds = 0; for (let i=0;i<byId('track').played.length;i++) seconds += byId('track').played.end(i)-byId('track').played.start(i);
  byId('save-review').disabled = seconds < 25;
});
byId('save-review').addEventListener('click', () => {
  const mode = document.querySelector('input[name="mode"]:checked');
  if (!generatedUrl || !mode || !byId('review-notes').value.trim()) { byId('status').textContent = 'Choose a judgment and add evidence from listening.'; return; }
  append('Human listening judgment: ' + mode.value + '. Notes: ' + byId('review-notes').value.trim());
});
byId('download').addEventListener('click', () => {
  const url = URL.createObjectURL(new Blob([log.join('\n')+'\n'],{type:'text/markdown'}));
  const a = document.createElement('a'); a.href=url; a.download='moodscape-live-checks.md'; a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
});
