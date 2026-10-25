#!/usr/bin/env python3
"""Same chart as plot_project_results.py, but for the v2 re-verification batch:
all 10 landmarks regenerated with (a) the current, fixed buildSunoPrompt()
(institutional-category fix, Sejong major-key fix, reworded mode clause) and
(b) customMode:true + style/title, matching the live app's real
buildSunoGenerationRequest() exactly (the original 2026-09-13 test used the
older customMode:false + flat prompt shape).
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
BLUE, ORANGE, INK, MUTED, GRID = '#2a78d6', '#eb6834', '#0b0b0b', '#52514e', '#e1e0d9'


def main():
    with (ROOT / 'audio_analysis_results_v2.csv').open(newline='', encoding='utf-8') as f:
        audio = list(csv.DictReader(f))
    with (ROOT / 'listener_stimulus_metadata.csv').open(newline='', encoding='utf-8') as f:
        score = {r['clip_id']: float(r['activity_score_0_100']) for r in csv.DictReader(f)}

    req = np.array([float(r['requested_bpm']) for r in audio])
    det = np.array([float(r['detected_bpm']) for r in audio])
    corr = np.array([min((d / 2, d, d * 2), key=lambda c: abs(c - q)) for d, q in zip(det, req)])
    err = np.abs(corr - req) / req * 100
    ids = [r['clip_id'] for r in audio]
    want = [r['requested_mode'] for r in audio]
    match = np.array([r['mode_match'] == 'True' for r in audio])
    conf = np.array([float(r['key_detection_confidence']) for r in audio])
    x_score = np.array([score[i] for i in ids])
    n = len(audio)

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.edgecolor': '#c3c2b7', 'axes.labelcolor': INK,
                         'xtick.color': MUTED, 'ytick.color': MUTED})
    fig, (a, b) = plt.subplots(1, 2, figsize=(14, 6.2), gridspec_kw={'width_ratios': [1.15, 1]})

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
              label='Same audio, re-read at ½×/2× (no audio was changed)')
    for q, d, i in zip(req, det, ids):
        a.annotate(i, (q, d), xytext=(6, 6), textcoords='offset points', fontsize=8, color=MUTED)
    a.set_xlim(30, 145); a.set_ylim(30, lim)
    a.set_xlabel('Tempo the model specified (BPM) (Suno Prompt)')
    a.set_ylabel('Tempo measured in the generated audio (BPM) (Actual Suno Product)')
    a.set_title('v2 re-verification: tempo, fixed prompts + customMode:true', loc='left', fontsize=12, color=INK)
    a.grid(color=GRID, lw=.8); a.set_axisbelow(True)
    a.legend(loc='upper left', fontsize=8.5, frameon=False)
    a.text(.98, .04, f'median corrected error = {np.median(err):.1f}%\nmean corrected error = {err.mean():.1f}%',
           transform=a.transAxes, ha='right', va='bottom', fontsize=9, color=INK,
           bbox=dict(boxstyle='round,pad=.4', fc='white', ec=GRID))

    for wanted, marker in (('major', 'o'), ('minor', '^')):
        for m, colr in ((True, BLUE), (False, ORANGE)):
            sel = np.array([(w == wanted) and (mm == m) for w, mm in zip(want, match)])
            if sel.any():
                b.scatter(x_score[sel], conf[sel], s=120, marker=marker, color=colr, zorder=3,
                          label=f'Asked for {wanted}: ' + ('matched' if m else 'got the other mode'))
    for xv, cv, i, r in zip(x_score, conf, ids, audio):
        b.annotate(f"{i}\n{r['detected_key']}", (xv, cv), xytext=(7, -3),
                   textcoords='offset points', fontsize=7.5, color=MUTED)
    b.set_xlim(-6, 100); b.set_ylim(.5, 1.02)
    b.set_xlabel('Generating activity score (0–100) (Suno Prompt)')
    b.set_ylabel('Key-detection confidence (Actual Suno Product)')
    n_major, n_minor = want.count('major'), want.count('minor')
    hit_major = int(sum(m for w, m in zip(want, match) if w == 'major'))
    hit_minor = int(sum(m for w, m in zip(want, match) if w == 'minor'))
    b.set_title(f'v2: {match.sum()} of {n} matched (major {hit_major}/{n_major}, minor {hit_minor}/{n_minor})',
                loc='left', fontsize=12, color=INK)
    b.grid(color=GRID, lw=.8); b.set_axisbelow(True)
    b.legend(loc='lower left', fontsize=8.5, frameon=False)

    fig.suptitle('Moodscape v2 re-verification: fixed prompts + customMode:true (vs. original 50% mode match)',
                 x=.06, ha='left', fontsize=14, fontweight='bold', color=INK, y=.985)
    fig.text(.06, .012, 'Data: 10 real Suno tracks regenerated 2026-10, using current buildSunoPrompt() and\n'
             'customMode:true+style/title (the live app\'s real request shape; the original 2026-09-13 test used customMode:false+prompt).\n'
             'Octave re-read does not change the audio — it only tests whether the tempo DETECTOR mislabeled the pulse. Small n; no human listening check yet.',
             fontsize=8.5, color=MUTED, va='bottom')
    fig.tight_layout(rect=(0, .08, 1, .94))
    out = ROOT / 'moodscape_results_graph_v2.png'
    fig.savefig(out, dpi=150, facecolor='white')
    print(f'Wrote {out}')
    print(f'n={n} median_err={np.median(err):.2f}% mean_err={err.mean():.2f}% mode_match={match.sum()}/{n}')


if __name__ == '__main__':
    main()
