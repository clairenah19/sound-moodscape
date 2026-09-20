#!/usr/bin/env python3
"""Draw the project's measured results: what the model specified vs. what the 10 real Suno tracks delivered.

Reads research/audio_analysis_results.csv (real librosa measurements of the generated MP3s) and
research/listener_stimulus_metadata.csv (generating activity scores). Writes
research/moodscape_results_graph.png. Nothing here is simulated; rerun after any regeneration.

Octave correction used for the "corrected" markers: for each clip, take whichever of
{detected/2, detected, detected*2} is nearest the requested BPM. This picks the factor using the
requested value, so it can only reduce error; it shows that the pulse is *plausibly* the requested
one, not that it is.
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
BLUE, ORANGE, INK, MUTED, GRID = '#2a78d6', '#eb6834', '#0b0b0b', '#52514e', '#e1e0d9'


def ranks(v):
    order = np.argsort(v)
    r = np.empty(len(v))
    r[order] = np.arange(1, len(v) + 1)
    return r  # tempo values here are all distinct, so no tie handling is needed


def spearman(a, b):
    return float(np.corrcoef(ranks(a), ranks(b))[0, 1])


def load():
    with (ROOT / 'audio_analysis_results.csv').open(newline='', encoding='utf-8') as f:
        audio = list(csv.DictReader(f))
    with (ROOT / 'listener_stimulus_metadata.csv').open(newline='', encoding='utf-8') as f:
        score = {r['clip_id']: float(r['activity_score_0_100']) for r in csv.DictReader(f)}
    return audio, score


def main():
    audio, score = load()
    req = np.array([float(r['requested_bpm']) for r in audio])
    det = np.array([float(r['detected_bpm']) for r in audio])
    corr = np.array([min((d / 2, d, d * 2), key=lambda c: abs(c - q)) for d, q in zip(det, req)])
    err = np.abs(corr - req) / req * 100
    rho_raw, rho_corr = spearman(req, det), spearman(req, corr)
    ids = [r['clip_id'] for r in audio]
    want = [r['requested_mode'] for r in audio]
    match = np.array([r['mode_match'] == 'True' for r in audio])
    conf = np.array([float(r['key_detection_confidence']) for r in audio])
    x_score = np.array([score[i] for i in ids])
    n = len(audio)

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.edgecolor': '#c3c2b7', 'axes.labelcolor': INK,
                         'xtick.color': MUTED, 'ytick.color': MUTED})
    fig, (a, b) = plt.subplots(1, 2, figsize=(14, 6.2), gridspec_kw={'width_ratios': [1.15, 1]})

    # Left: tempo
    lim = 170
    xs = np.array([30, 145])
    a.plot(xs, xs, color=INK, lw=1.2, label='Exactly as requested (1×)')
    a.plot(xs, xs * 2, color=MUTED, lw=1, ls='--', label='Double tempo (2×)')
    a.plot(xs, xs / 2, color=MUTED, lw=1, ls=':', label='Half tempo (½×)')
    for q, d, c in zip(req, det, corr):
        if abs(c - d) > 1e-9:
            a.annotate('', xy=(q, c), xytext=(q, d), arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1, alpha=.7))
    a.scatter(req, det, s=70, color=BLUE, zorder=3, label='Measured tempo (raw)')
    a.scatter(req, corr, s=70, facecolor='white', edgecolor=ORANGE, linewidth=2, zorder=4,
              label='After octave correction')
    for q, d, i in zip(req, det, ids):
        a.annotate(i, (q, d), xytext={'clip02': (-40, 4)}.get(i, (6, 6)), textcoords='offset points', fontsize=8, color=MUTED)
    a.set_xlim(30, 145); a.set_ylim(30, lim)
    a.set_xlabel('Tempo the model specified (BPM = 42 + 110 × activity score)')
    a.set_ylabel('Tempo measured in the generated audio (BPM)')
    a.set_title('Tempo: 6 of 10 tracks measure near 2\u00d7, \u00bd\u00d7 or 3\u00d7 the request', loc='left', fontsize=12, color=INK)
    a.grid(color=GRID, lw=.8); a.set_axisbelow(True)
    a.legend(loc='upper left', fontsize=8.5, frameon=False)
    a.text(.98, .04, f'Spearman ρ, raw = {rho_raw:.2f}\nSpearman ρ, corrected = {rho_corr:.2f}\n'
           f'median corrected error = {np.median(err):.1f}%', transform=a.transAxes, ha='right', va='bottom',
           fontsize=9, color=INK, bbox=dict(boxstyle='round,pad=.4', fc='white', ec=GRID))

    # Right: mode
    for wanted, marker in (('major', 'o'), ('minor', '^')):
        for m, colr, fill in ((True, BLUE, True), (False, ORANGE, True)):
            sel = np.array([(w == wanted) and (mm == m) for w, mm in zip(want, match)])
            if sel.any():
                b.scatter(x_score[sel], conf[sel], s=120, marker=marker, color=colr, zorder=3,
                          label=f'Asked for {wanted}: ' + ('matched' if m else 'got the other mode'))
    for xv, cv, i, r in zip(x_score, conf, ids, audio):
        b.annotate(f"{i}\n{r['detected_key']}", (xv, cv), xytext={'clip03': (-30, 9), 'clip04': (8, 4)}.get(i, (7, -3)),
                   textcoords='offset points', fontsize=7.5, color=MUTED)
    b.set_xlim(-6, 100); b.set_ylim(.5, 1.02)
    b.set_xlabel('Generating activity score (0–100, 10 clips spanning the 75-place range)')
    b.set_ylabel('Key-detection confidence')
    n_major, n_minor = want.count('major'), want.count('minor')
    hit_major = int(sum(m for w, m in zip(want, match) if w == 'major'))
    hit_minor = int(sum(m for w, m in zip(want, match) if w == 'minor'))
    b.set_title(f'Mode: {match.sum()} of {n} matched (major {hit_major}/{n_major}, minor {hit_minor}/{n_minor})',
                loc='left', fontsize=12, color=INK)
    b.grid(color=GRID, lw=.8); b.set_axisbelow(True)
    b.legend(loc='lower left', fontsize=8.5, frameon=False)

    fig.suptitle('Moodscape: does the generated music match what the model specified?', x=.06, ha='left',
                 fontsize=15, fontweight='bold', color=INK, y=.985)
    fig.text(.06, .012, 'Data: 10 real Suno tracks, one per clip; tempo and key measured with librosa (Krumhansl–Schmuckler).\n'
             'Octave correction picks the factor nearest the request, so it can only shrink error. Small n; no human listening check yet.',
             fontsize=8.5, color=MUTED, va='bottom')
    fig.tight_layout(rect=(0, .07, 1, .95))
    out = ROOT / 'moodscape_results_graph.png'
    fig.savefig(out, dpi=150, facecolor='white')
    print(f'Wrote {out}')
    print(f'n={n} rho_raw={rho_raw:.3f} rho_corrected={rho_corr:.3f} median_err={np.median(err):.2f}% mean_err={err.mean():.2f}%')


if __name__ == '__main__':
    main()
