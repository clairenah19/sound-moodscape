# Generated audio (Suno V4_5 via sunoapi.org)

These files are the audio measured in the research paper and the KSEF 2027 submissions (`ksef2027/`). They are
real generations, not synthetic fixtures. Generated audio remains subject to the provider's terms.

| Files | What they are |
|---|---|
| `clip01.mp3`–`clip10.mp3` | Round 1: original prompts, single free-text request, generated 2026-09-13 |
| `v2_clip01.mp3`–`v2_clip10.mp3` | Round 2: revised prompts, custom request shape (style + title) |
| `clip07_sejong_perceived95_candidate2.mp3` | Sejong regeneration that strictly required 95 BPM; one blind listener tapped it at 48 BPM |
| `clip07_sejong_retimed_hihat_fixed.flac` | The same audio after pitch-preserving time-axis correction (47 → 95 BPM) and hi-hat replacement; **post-processed, not a raw generation** |
| `clip07_hihat_fixed_blind_test.wav` | 25-second anonymous excerpt of the corrected file; the same listener tapped it at 96 BPM |
| `clip07_*.json` | Parameters, hashes and the human tap result for the Sejong correction |
| `clip09_genre_swap_test*.mp3` | Gangnam with genre words swapped to "dark synth-pop, moody downtempo" (3 runs, detected minor 3/3) |
| `clip10_genre_swap_test_run*.mp3` | Asan plant with genre words swapped to "dark industrial techno" (3 runs, detected minor 0/3) |

Measurements: `../audio_analysis_results_octave_aware.csv` (round 1), `../audio_analysis_results_v2_octave_aware.csv`
(round 2), `../paper/stats.json` (all follow-ups). Only the Sejong clip was checked by a person (one informal
listener); every other key and tempo is an automatic librosa detection.

## Listener experiment status

None of these files is cleared as a study stimulus yet. `../listener_stimuli.json` stays `"ready": false` until one
clip set is chosen, the key of every clip is reviewed by ear, and `python3 research/prepare_listener_clips.py`
(needs ffmpeg) freezes the 25-second clips and their hashes. Do not hand-edit readiness or hashes, and do not use
the post-processed Sejong file as a raw-generation stimulus without saying so.
