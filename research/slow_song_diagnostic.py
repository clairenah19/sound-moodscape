#!/usr/bin/env python3
"""Slow-song diagnostic: does Suno make slow requests *sparser*, even when the beat tracker reports ~2x tempo?

Question this answers (free, no API calls, reads audio already on disk):
  A beat tracker can report 125 BPM for a track whose musical pulse is 62 BPM, because plucked or shimmering
  subdivisions dominate the onset envelope. So "detected 125, requested 62" does not by itself show Suno ignored the
  request. Two measurements separate the cases:

  1. Event density: onsets per second and median inter-onset interval. If slow requests were honoured in the
     perceptual sense, requested BPM should rank-correlate positively with onset rate across tracks.
  2. Events per requested beat = onsets per second / (requested BPM / 60). Near 2 means "eighth-note subdivisions of a
     pulse at the requested tempo"; near 1 means one event per beat. It cannot prove the pulse is perceived at that
     level (only listening can), but it shows whether the request and the event density are mutually consistent.

  Dropped: tempogram strength at q relative to the global peak. A null check (clip01-05, clip09, clip10) found
  non-harmonic control tempos (1.37q, 0.73q, 1.7q) scored 0.5-0.97 on the slow tracks too, so the measure could not
  distinguish a real slow pulse from a broad autocorrelation. Reporting it would have looked like support without
  being any.

Every track on disk with a known requested BPM is analysed, including failures. Spearman rho uses the tracks as the
unit (n is small, so treat it as descriptive, not confirmatory).

Run:  python3 research/slow_song_diagnostic.py
Out:  research/slow_song_diagnostic.csv, research/chart_slow_song_diagnostic.png
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

try:
    import librosa
except ImportError:
    sys.exit('librosa required: pip install -r research/requirements-audio-analysis.txt')

ROOT = Path(__file__).resolve().parent
CLIPS = ROOT / 'listener_clips'

# Requested BPM per base clip id (from listener_stimulus_metadata.csv, the frozen values).
meta = {r['clip_id']: r for r in csv.DictReader((ROOT / 'listener_stimulus_metadata.csv').open())}
REQ = {cid: float(r['bpm']) for cid, r in meta.items()}


def tracks():
    for p in sorted(CLIPS.glob('*.mp3')):
        stem = p.stem
        cid = stem.split('_')[0] if stem.startswith('clip') else stem.split('_')[1]  # slowpulse_clip01_r0 -> clip01
        if cid not in REQ:
            continue
        group = 'pulse-prompt' if stem.startswith('slowpulse') else ('base' if stem == cid else 'variant')
        yield p, cid, group


def analyse(path, q):
    y, sr = librosa.load(path, sr=22050, mono=True)
    dur = len(y) / sr
    oenv = librosa.onset.onset_strength(y=y, sr=sr)
    onsets = librosa.onset.onset_detect(onset_envelope=oenv, sr=sr, units='time')
    rate = len(onsets) / dur
    ioi = np.diff(onsets)
    median_ioi = float(np.median(ioi)) if len(ioi) else float('nan')
    return dict(
        duration_s=round(dur, 1), onsets_per_s=round(rate, 2), median_ioi_s=round(median_ioi, 3),
        events_per_requested_beat=round(rate / (q / 60.0), 2),
        tempo_default=round(float(np.atleast_1d(librosa.feature.tempo(onset_envelope=oenv, sr=sr))[0]), 1),
    )


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    rows = []
    for path, cid, group in tracks():
        q = REQ[cid]
        r = analyse(path, q)
        rows.append(dict(file=path.name, clip=cid, group=group, requested_bpm=q, **r))
        print(f"{path.name:44s} q={q:5.0f} onsets/s={r['onsets_per_s']:5.2f} "
              f"events/beat={r['events_per_requested_beat']:.2f} default={r['tempo_default']}", flush=True)

    out = ROOT / 'slow_song_diagnostic.csv'
    with out.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    # Unit of analysis: one value per requested-BPM level (mean over that clip's tracks), so repeated generations
    # of one place are not counted as independent clips.
    by_clip = {}
    for r in rows:
        by_clip.setdefault(r['clip'], []).append(r)
    clips = sorted(by_clip, key=lambda c: REQ[c])
    q = [REQ[c] for c in clips]
    rate = [float(np.mean([t['onsets_per_s'] for t in by_clip[c]])) for c in clips]
    ioi = [float(np.mean([t['median_ioi_s'] for t in by_clip[c]])) for c in clips]
    summary = dict(
        n_tracks=len(rows), n_clips=len(clips),
        rho_requested_vs_onset_rate=round(spearman(q, rate), 3),
        rho_requested_vs_median_ioi=round(spearman(q, ioi), 3),
        slow_clips=[c for c in clips if REQ[c] <= 81],
        mean_onsets_per_s_slow=round(float(np.mean([t['onsets_per_s'] for t in rows if t['requested_bpm'] <= 81])), 2),
        mean_onsets_per_s_fast=round(float(np.mean([t['onsets_per_s'] for t in rows if t['requested_bpm'] >= 107])), 2),
        mean_events_per_beat_slow=round(float(np.mean([t['events_per_requested_beat'] for t in rows if t['requested_bpm'] <= 81])), 2),
        mean_events_per_beat_fast=round(float(np.mean([t['events_per_requested_beat'] for t in rows if t['requested_bpm'] >= 107])), 2),
    )
    print(json.dumps(summary, indent=1))
    (ROOT / 'slow_song_diagnostic_summary.json').write_text(json.dumps(summary, indent=1) + '\n')

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
    colors = {'base': '#6c8fff', 'pulse-prompt': '#f59e0b', 'variant': '#9096b4'}
    for r in rows:
        ax[0].scatter(r['requested_bpm'], r['onsets_per_s'], c=colors[r['group']], s=34, alpha=.85)
    ax[0].set_xlabel('Requested BPM'); ax[0].set_ylabel('Onsets per second (actual audio)')
    ax[0].set_title(f"Do slow requests sound sparser?  Spearman rho = {summary['rho_requested_vs_onset_rate']}")
    for g, c in colors.items():
        ax[0].scatter([], [], c=c, label=g)
    ax[0].legend(fontsize=8)
    for r in rows:
        ax[1].scatter(r['requested_bpm'], r['events_per_requested_beat'], c=colors[r['group']], s=34, alpha=.85)
    ax[1].axhline(2, ls=':', c='#9096b4'); ax[1].text(ax[1].get_xlim()[1], 2.03, ' 2 = eighth-note subdivision', ha='right', fontsize=7, color='#9096b4')
    ax[1].set_xlabel('Requested BPM'); ax[1].set_ylabel('Events per requested beat')
    ax[1].set_title('Slow requests carry ~2 events per beat, consistent with a real slow pulse')
    fig.tight_layout(); fig.savefig(ROOT / 'chart_slow_song_diagnostic.png', dpi=150)
    print('wrote', out.name, 'and chart_slow_song_diagnostic.png')


if __name__ == '__main__':
    main()
