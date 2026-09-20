// Run: node research/export_landmarks.js > research/landmark_inventory.json
// Executes only the project's static data and pure prompt functions in an isolated context.
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const context = vm.createContext({window: {}});
vm.runInContext(fs.readFileSync(path.join(root, 'data.js'), 'utf8'), context);
vm.runInContext(fs.readFileSync(path.join(root, 'prompt.js'), 'utf8'), context);
const places = vm.runInContext(`Object.entries(MOOD_DATA.states).flatMap(([state, s]) =>
  s.places.map(p => ({state, place: p.name, score: p.score, region_score: s.score,
    type: p.type, photo: p.photo, photoPage: p.photoPage, photos: p.photos || [],
    key: getMusicalKey(p, state), bpm: getSunoBpm(p), prompt: buildSunoPrompt(p, state)})))`, context);
process.stdout.write(JSON.stringify(places, null, 2) + '\n');
