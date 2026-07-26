# Moodscape audio tracks

Drop Suno-generated (or any) MP3s here to have Moodscape play them as a place's
soundscape instead of the built-in synth fallback.

## Naming

Each file must be named `<state-slug>__<place-slug>.mp3`, e.g.:

- `seoul__hongdae.mp3`
- `jeju-do__hallasan.mp3`
- `gyeongsang__busan-haeundae.mp3`

The exact filename for any place is shown in that place's "Generate real music
with Suno" panel in the app. Slugs are lowercase, with every run of
non-alphanumeric characters replaced by a single hyphen.

## Workflow

1. Open a place in the app, expand "Generate real music with Suno".
2. Copy the tailored prompt, generate an **instrumental** in Suno.
3. Download the MP3, rename it to the filename shown in the panel, and save it here.
4. Reload — the app detects the file and plays it automatically (the waveform
   reacts to the real audio).

Alternatively, paste a hosted MP3 URL into `window.SUNO_TRACKS` in index.html,
keyed by the same `<state-slug>__<place-slug>` string.
