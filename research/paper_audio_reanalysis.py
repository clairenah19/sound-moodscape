#!/usr/bin/env python3
"""Re-measure every generated clip used in the paper with one detector, so no figure is copied from a report.

For each MP3 it records: Krumhansl-Schmuckler key/mode and confidence (analyze_generated_audio.detect_key),
beat_track tempo (the value the earlier reports used), and a prior-free tempogram view
(librosa.feature.tempo with default prior, with a uniform prior, and the three strongest autocorrelation peaks).

Output: research/paper_audio_reanalysis.json.  Needs librosa==1.0.0 (see requirements-audio-analysis.txt).
Run from the repo root:  python3 research/paper_audio_reanalysis.py
"""
import json
import sys
from pathlib import Path

import librosa
import numpy as np
import scipy.stats as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from analyze_generated_audio import detect_bpm, detect_key  # noqa: E402

CLIPS = ROOT / 'listener_clips'
# file -> (group, clip_id, requested mode, requested BPM, short description)
FILES = {}
req_bpm = {'clip01': 42, 'clip02': 62, 'clip03': 68, 'clip04': 75, 'clip05': 81, 'clip06': 88, 'clip07': 95, 'clip08': 107, 'clip09': 115, 'clip10': 138}
for i in range(1, 11):
    c = f'clip{i:02d}'
    FILES[f'{c}.mp3'] = ('round1', c, None, req_bpm[c], 'Round 1: original prompt, customMode=false')
    FILES[f'v2_{c}.mp3'] = ('round2', c, None, req_bpm[c], 'Round 2: revised prompt, customMode=true')
FOLLOW = {
    'clip09_retest_minor_fix.mp3': ('followup', 'clip09', 'minor', 115, 'Gangnam: reworded prompt, customMode=false'),
    'clip09_genre_swap_test.mp3': ('genre_swap', 'clip09', 'minor', 115, 'Gangnam: genre words swapped, run 1'),
    'clip09_genre_swap_test_run2.mp3': ('genre_swap', 'clip09', 'minor', 115, 'Gangnam: genre words swapped, run 2'),
    'clip09_genre_swap_test_run3.mp3': ('genre_swap', 'clip09', 'minor', 115, 'Gangnam: genre words swapped, run 3'),
    'clip10_asan_retest_custommode.mp3': ('followup', 'clip10', 'minor', 138, 'Asan: reworded prompt, customMode=true'),
    'clip10_genre_swap_test_run1.mp3': ('genre_swap', 'clip10', 'minor', 138, 'Asan: genre words swapped, run 1'),
    'clip10_genre_swap_test_run2.mp3': ('genre_swap', 'clip10', 'minor', 138, 'Asan: genre words swapped, run 2'),
    'clip10_genre_swap_test_run3.mp3': ('genre_swap', 'clip10', 'minor', 138, 'Asan: genre words swapped, run 3'),
    'clip07_sejong_retest_custommode.mp3': ('followup', 'clip07', 'minor', 95, 'Sejong: reworded prompt, customMode=true'),
    'clip07_sejong_institutional_fix.mp3': ('followup', 'clip07', 'minor', 95, 'Sejong: institutional-category style fix, minor requested'),
    'clip07_sejong_major_fix.mp3': ('followup', 'clip07', 'major', 95, 'Sejong: institutional style + major requested'),
}
FILES.update(FOLLOW)


def tempo_views(y, sr):
    oenv = librosa.onset.onset_strength(y=y, sr=sr)
    default = float(np.atleast_1d(librosa.feature.tempo(onset_envelope=oenv, sr=sr))[0])
    flat = float(np.atleast_1d(librosa.feature.tempo(onset_envelope=oenv, sr=sr, prior=st.uniform(30, 270)))[0])
    tg = librosa.feature.tempogram(onset_envelope=oenv, sr=sr)
    ac = tg.mean(axis=1)
    bpms = librosa.tempo_frequencies(tg.shape[0], sr=sr)
    idx = np.where((bpms >= 30) & (bpms <= 300))[0]
    peaks = [i for i in idx[1:-1] if ac[i] > ac[i - 1] and ac[i] > ac[i + 1]]
    top = sorted(peaks, key=lambda i: -ac[i])[:3]
    return default, flat, [round(float(bpms[i]), 1) for i in top]


out = []
for fn, (group, clip, mode, bpm, desc) in FILES.items():
    path = CLIPS / fn
    if not path.exists():
        print('missing', fn)
        continue
    y, sr = librosa.load(path, sr=None, mono=True)
    root, det_mode, conf = detect_key(y, sr)
    d, f, top3 = tempo_views(y, sr)
    out.append(dict(file=fn, group=group, clip=clip, requested_mode=mode, requested_bpm=bpm, description=desc,
                    key=f'{root} {det_mode}', mode=det_mode, confidence=round(float(conf), 3),
                    beat_track_bpm=round(detect_bpm(y, sr), 1), tempo_default_prior=round(d, 1), tempo_flat_prior=round(f, 1),
                    top3=top3, duration_s=round(len(y) / sr, 1)))
    print(out[-1]['file'], out[-1]['key'], out[-1]['confidence'], out[-1]['beat_track_bpm'], flush=True)
(ROOT / 'paper_audio_reanalysis.json').write_text(json.dumps(out, indent=1))
print('Wrote', ROOT / 'paper_audio_reanalysis.json', len(out), 'clips')
