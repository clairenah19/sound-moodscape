#!/usr/bin/env python3
"""Tempo and key accuracy for both generation rounds, from the saved analysis CSVs.

Reads audio_analysis_results_octave_aware.csv (round 1) and audio_analysis_results_v2_octave_aware.csv
(round 2). Writes accuracy_both_rounds.png. Nothing is simulated.
"""
import csv
import os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
TICK = MPath([(-1, .05), (-.35, -.65), (1, .85)], [MPath.MOVETO, MPath.LINETO, MPath.LINETO])
import numpy as np

ROOT = Path(__file__).resolve().parent
BLUE, ORANGE, GREEN, RED, INK, MUTED, GRID = '#2a78d6', '#eb6834', '#1baf7a', '#e34948', '#0b0b0b', '#52514e', '#e1e0d9'

def load(name):
    with (ROOT / name).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

r1, r2 = load('audio_analysis_results_octave_aware.csv'), load('audio_analysis_results_v2_octave_aware.csv')
ids = [r['clip_id'] for r in r1]
assert ids == [r['clip_id'] for r in r2]
req = np.array([float(r['requested_bpm']) for r in r1])
def err(rows): return np.array([float(r['octave_aware_diff_pct']) for r in rows])
def hit(rows): return np.array([r['mode_match'] == 'True' for r in rows])
e1, e2, h1, h2 = err(r1), err(r2), hit(r1), hit(r2)
want1 = [r['requested_mode'] for r in r1]
want2 = [r['requested_mode'] for r in r2]
want = want1
x = np.arange(len(ids)); w = .38

plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.edgecolor': '#c3c2b7', 'axes.labelcolor': INK,
                     'xtick.color': MUTED, 'ytick.color': MUTED})
# SLIDE=1 draws a compact copy for presentation slides: same data, smaller canvas (so text reads larger), no title/footnote.
SLIDE = os.environ.get('SLIDE') == '1'
fig, (a, b) = plt.subplots(1, 2, figsize=(10.5, 5.0) if SLIDE else (14, 5.8), gridspec_kw={'width_ratios': [1.25, 1]})

a.axhline(5, color=MUTED, ls='--', lw=1)
a.text(-.5, 5.6, '5% = "fits a standard multiple"', ha='left', fontsize=8, color=MUTED)
a.bar(x - w/2, e1, w, color=BLUE, label='Round 1')
a.bar(x + w/2, e2, w, color='#9ec5f4', label='Round 2 (revised prompts)')
for i in range(len(ids)):
    # The CSV names the nearest multiple even when it is >5% away; only label a fit when within 5%.
    lab = [rows[i]['metrical_relation'] if v <= 5 else 'no fit' for v, rows in ((e1[i], r1), (e2[i], r2))]
    if lab[0] == lab[1]:  # one shared label over the pair, so neighbouring labels cannot collide
        a.text(x[i], max(e1[i], e2[i]) + .8, lab[0], ha='center', fontsize=7.5, color=RED if lab[0] == 'no fit' else MUTED)
        continue
    for xx, v, l in ((x[i] - w/2, e1[i], lab[0]), (x[i] + w/2, e2[i], lab[1])):
        a.text(xx, v + .8, l, ha='center', fontsize=7.5, color=RED if l == 'no fit' else MUTED)
a.set_xticks(x)
a.set_xticklabels([f"{i[-2:]}\n{int(q)}" for i, q in zip(ids, req)] if SLIDE else [f"{i}\n{int(q)} BPM" for i, q in zip(ids, req)], fontsize=8)
if SLIDE:
    a.set_xlabel('Clip / requested BPM', fontsize=9, color=MUTED)
a.set_ylabel('Octave-aware tempo error (%)'); a.grid(axis='y', color=GRID); a.set_axisbelow(True)
a.set_title(f'Tempo: mean error {e1.mean():.1f}% in both rounds; median {np.median(e1):.1f}% / {np.median(e2):.1f}%',
            loc='left', fontsize=11.5, color=INK)
a.legend(frameon=False, loc='upper left', fontsize=9)

y = np.arange(len(ids))[::-1]
b.set_xlim(-.6, 1.6); b.set_ylim(-.7, len(ids) - .3)
for yy, a1, a2, w1, w2 in zip(y, h1, h2, want1, want2):
    for xx, ok, wm in ((0, a1, w1), (1, a2, w2)):
        b.scatter(xx, yy, s=420, marker='o' if wm == 'major' else '^', color=GREEN if ok else RED, zorder=3)
        # Scatter markers are sized in points, so they stay undistorted (the two axes have different data scales).
        # A triangle's visual centre sits below its box centre, so nudge its mark down slightly.
        cy = yy - (.08 if wm == 'minor' else 0)
        b.scatter(xx, cy, s=130 if ok else 90, marker=TICK if ok else 'x', facecolors='none' if ok else 'white',
                  edgecolors='white', c=None if ok else 'white', linewidths=2.6, zorder=4)
b.set_yticks(y); b.set_yticklabels([c + ('  (asked minor, then major)' if (w1, w2) == ('minor', 'major') else f'  (asked {w1})') for c, w1, w2 in zip(ids, want1, want2)], fontsize=9)
b.set_xticks([0, 1]); b.set_xticklabels([f'Round 1\n{h1.sum()}/10 matched', f'Round 2\n{h2.sum()}/10 matched'], fontsize=10)
b.xaxis.tick_top(); b.grid(axis='y', color=GRID); b.set_axisbelow(True)
m1 = [i for i, w_ in enumerate(want1) if w_ == 'minor']
m2 = [i for i, w_ in enumerate(want2) if w_ == 'minor']
b.set_title(f'Mode: minor requests matched {h1[m1].sum()}/{len(m1)} (round 1), {h2[m2].sum()}/{len(m2)} (round 2)',
            loc='right', fontsize=11, color=INK, y=1.12)
if not SLIDE:
    fig.suptitle('Moodscape: how accurately did Suno follow the requested tempo and key?', x=.06, ha='left', fontsize=14, fontweight='bold', color=INK, y=.99)
    fig.text(.06, .01, 'Real Suno tracks, measured with librosa. Tempo labels describe the beat tracker only; no listener has confirmed the felt beat. '
             'Circle = asked for major, triangle = asked for minor (shape follows each round\'s own request).', fontsize=8, color=MUTED)
fig.tight_layout(rect=(0, 0, 1, 1) if SLIDE else (0, .04, 1, .95))
out = ROOT / ('accuracy_both_rounds_slide.png' if SLIDE else 'accuracy_both_rounds.png')
fig.savefig(out, dpi=150, facecolor='white')
print('Wrote', out, '| mean err', e1.mean().round(2), e2.mean().round(2), '| median', np.median(e1).round(2), np.median(e2).round(2), '| key', h1.sum(), h2.sum())
