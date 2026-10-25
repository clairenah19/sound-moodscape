#!/usr/bin/env python3
"""Compute every number and draw every figure for the full-project paper (research/paper/).

Inputs (all already in the repo; nothing is simulated):
  paper_model_export.json   the live data.js/prompt.js model, exported by paper_export_model.html
  audio_analysis_results.csv, prompt_ablation_results.csv, listener_stimulus_metadata.csv
  paper_audio_reanalysis.json   every generated clip re-measured by paper_audio_reanalysis.py (librosa)
  prompt_ablation_results.csv, audio_analysis_results_v2.csv
  moodscape_landmark_pageviews.csv, ../geojson.js

Outputs: research/paper/figures/*.png and research/paper/stats.json.
Run:  python3 research/paper_analysis.py        (needs numpy, scipy, matplotlib)

Re-export the model after any change to data.js/prompt.js:
  chrome --headless=new --allow-file-access-from-files --dump-dom file://$PWD/research/paper_export_model.html
  (take the text of <pre id="o"> and save it as research/paper_model_export.json)
"""
import csv
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon as MplPolygon
from scipy import stats

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'paper'
FIG = OUT / 'figures'
FIG.mkdir(parents=True, exist_ok=True)
SEED = 20260920
RNG = np.random.default_rng(SEED)

# Palette: one blue/orange pair for the two main categories, gray for context (color-blind safe pair).
BLUE, ORANGE, GREY, INK, MUTED, GRID = '#2a78d6', '#eb6834', '#898781', '#0b0b0b', '#52514e', '#e1e0d9'
GREEN, RED = '#1baf7a', '#e34948'
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 8.5, 'axes.edgecolor': '#c3c2b7', 'axes.labelcolor': INK,
    'axes.titlesize': 9, 'axes.titleweight': 'bold', 'axes.titlelocation': 'left',
    'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.spines.top': False, 'axes.spines.right': False,
    'figure.dpi': 100, 'savefig.dpi': 220, 'savefig.facecolor': 'white'})

W_STATED = np.array([.35, .30, .15, .10, .10])
COMP_NAMES = ['density', 'tourism', 'complaints', 'facilities', 'crowding']
COMP_LABEL = ['Density', 'Tourism intensity', 'Noise complaints', 'Noise facilities', 'Crowding pressure']
ABBR = {'Seoul': 'SEL', 'Busan': 'BSN', 'Daegu': 'DAG', 'Incheon': 'ICN', 'Gwangju': 'GWJ', 'Daejeon': 'DJN',
        'Ulsan': 'USN', 'Sejongsi': 'SEJ', 'Gyeonggi-do': 'GG', 'Gangwon': 'GW', 'Chungcheongbuk-do': 'CB',
        'Chungcheongnam-do': 'CN', 'Jeollabuk-do': 'JB', 'Jeollanam-do': 'JN', 'Gyeongsangbuk-do': 'GB',
        'Gyeongsangnam-do': 'GN', 'Jeju-do': 'JJ'}


def panel(ax, letter):
    ax.text(-0.02, 1.08, f'({letter})', transform=ax.transAxes, fontsize=10, fontweight='bold', va='bottom', ha='right')


def save(fig, name):
    fig.savefig(FIG / name, bbox_inches='tight')
    plt.close(fig)


def clopper_pearson(k, n, a=.05):
    lo = 0.0 if k == 0 else stats.beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(1 - a / 2, k + 1, n - k)
    return float(lo), float(hi)


def perm_p(x, y, n=20000):
    obs = stats.spearmanr(x, y).statistic
    rs = np.array([stats.spearmanr(x, RNG.permutation(y)).statistic for _ in range(n)])
    return float(obs), float((np.sum(np.abs(rs) >= abs(obs) - 1e-12) + 1) / (n + 1))


def desc(v):
    v = np.asarray(v, float)
    return dict(min=float(v.min()), max=float(v.max()), mean=float(v.mean()), median=float(np.median(v)), sd=float(v.std(ddof=1)))


# ---------------------------------------------------------------- load
M = json.loads((ROOT / 'paper_model_export.json').read_text())
regions, places = M['regions'], M['places']
S = {'seed': SEED, 'pleasantness_median': M['median']}
act = np.array([r['activity'] for r in regions])
pleas = np.array([r['pleasantness'] for r in regions])
comps = np.array([[r['comps'][k] for k in COMP_NAMES] for r in regions])
names = [r['region'] for r in regions]

# ---------------------------------------------------------------- RQ1: descriptives + sensitivity
raw_keys = [('density', 'Population density (per km²)'), ('tourism', 'Domestic tourism trips per resident'),
            ('complaints', 'Noise/vibration complaints per 100,000 residents'),
            ('facilities', 'Regulated noise-emitting facilities per 100,000 residents'),
            ('crowdingPressure', 'Crowding pressure (100 − crowding satisfaction)')]
S['table1'] = [dict(label=lab, **desc([r['raw'][k] for r in regions])) for k, lab in raw_keys]
for key, lab in (('overall', 'Overall satisfaction (0–100)'), ('recommend', 'Recommendation intention (0–100)'),
                 ('revisit', 'Revisit intention (0–100)'), ('crowding', 'Crowding satisfaction (0–100)')):
    S['table1'].append(dict(label=lab, **desc([r['input'][key] for r in regions])))
S['table1'].append(dict(label='Activity Proxy (0–100)', **desc(act)))
S['table1'].append(dict(label='Visitor Pleasantness composite (0–100)', **desc(pleas)))
S['n_regions'] = len(regions)

base_rank = stats.rankdata(-act)  # 1 = most active
S['activity_rank'] = {n: int(r) for n, r in zip(names, base_rank)}
S['component_vs_activity_rho'] = {c: float(stats.spearmanr(comps[:, i], act).statistic) for i, c in enumerate(COMP_NAMES)}

# drop-one-component and equal weights
loo = {}
for i, c in enumerate(COMP_NAMES):
    w = W_STATED.copy(); w[i] = 0; w /= w.sum()
    loo[c] = float(stats.spearmanr(comps @ w, act).statistic)
S['drop_one_rho'] = loo
S['equal_weights_rho'] = float(stats.spearmanr(comps @ np.full(5, .2), act).statistic)


def mc(alpha, n=10000):
    ws = RNG.dirichlet(alpha, n)
    acts = ws @ comps.T                     # n x 17
    ranks = np.array([stats.rankdata(-a) for a in acts])
    rhos = np.array([stats.spearmanr(a, act).statistic for a in acts])
    return ws, ranks, rhos


ws_loc, rk_loc, rho_loc = mc(W_STATED * 20)
ws_glob, rk_glob, rho_glob = mc(np.ones(5))
S['mc_local'] = dict(concentration=20, n=10000, rho_median=float(np.median(rho_loc)), rho_p5=float(np.percentile(rho_loc, 5)),
                     rho_min=float(rho_loc.min()), share_rho_ge_90=float((rho_loc >= .9).mean()),
                     weight_sd=[float(x) for x in ws_loc.std(axis=0)])
S['mc_global'] = dict(n=10000, rho_median=float(np.median(rho_glob)), rho_p5=float(np.percentile(rho_glob, 5)),
                      rho_min=float(rho_glob.min()), share_rho_ge_90=float((rho_glob >= .9).mean()))
rank_lo = np.percentile(rk_loc, 2.5, axis=0); rank_hi = np.percentile(rk_loc, 97.5, axis=0)
S['rank_range_local'] = {n: [float(a), float(b)] for n, a, b in zip(names, rank_lo, rank_hi)}
S['median_rank_interval_width_local'] = float(np.median(rank_hi - rank_lo))
S['top3_stable_local'] = {n: float((rk_loc[:, i] <= 3).mean()) for i, n in enumerate(names) if (rk_loc[:, i] <= 3).mean() > .5}

ref = dict(zip(names, act))
S['reference_check'] = dict(seoul_activity=float(ref['Seoul']), daejeon_activity=float(ref['Daejeon']),
                            seoul_rank=int(S['activity_rank']['Seoul']), daejeon_rank=int(S['activity_rank']['Daejeon']),
                            order_agrees=bool(ref['Seoul'] > ref['Daejeon']), published_seoul=78, published_daejeon=45)

# ---------------------------------------------------------------- RQ2: landmark scores, clipping, popularity
sc = np.array([p['score'] for p in places]); reg_of = [p['region'] for p in places]
groups = {}
for p in places:
    groups.setdefault(p['region'], []).append(p['score'])
grand = sc.mean()
ssb = sum(len(v) * (np.mean(v) - grand) ** 2 for v in groups.values())
sst = ((sc - grand) ** 2).sum()
k, n = len(groups), len(sc)
msb, msw = ssb / (k - 1), (sst - ssb) / (n - k)
n0 = (n - sum(len(v) ** 2 for v in groups.values()) / n) / (k - 1)
S['place_variance'] = dict(n_places=n, n_regions=k, eta_sq=float(ssb / sst), icc1=float((msb - msw) / (msb + (n0 - 1) * msw)),
                           score=desc(sc), places_per_region=[min(len(v) for v in groups.values()), max(len(v) for v in groups.values())],
                           n_clipped_at_0=int((sc == 0).sum()), n_clipped_at_1=int((sc == 1).sum()))
off = np.array([p['offset'] for p in places])
S['place_variance']['offset_sd'] = float(off.std(ddof=1))
S['place_variance']['offset_range'] = [float(off.min()), float(off.max())]

pv = {(r['state'], r['place']): r for r in csv.DictReader((ROOT / 'moodscape_landmark_pageviews.csv').open(encoding='utf-8'))}
pop_x, pop_y, pop_lab = [], [], []
for p in places:
    r = pv.get((p['region'], p['name']))
    if r and r['status'] == 'ok' and r['popularity_offset_0_100'] != '':
        pop_x.append(float(r['popularity_offset_0_100'])); pop_y.append(p['score'] * 100); pop_lab.append(p['name'])
S['popularity'] = dict(n_complete=len(pop_x), n_total=len(places))
if len(pop_x) > 5:
    rho, p_ = perm_p(np.array(pop_x), np.array(pop_y))
    S['popularity'].update(rho=rho, p_perm=p_)
statuses = {}
for r in pv.values():
    statuses[r['status']] = statuses.get(r['status'], 0) + 1
S['popularity']['status_counts'] = statuses

# ---------------------------------------------------------------- RQ3: specification
bpm = np.array([p['bpm'] for p in places])
S['spec'] = dict(bpm_min=int(bpm.min()), bpm_max=int(bpm.max()), n_places=len(places))
rule_of = lambda p: 'Solemn override' if p['solemn'] else ('Traditional/nature override' if p['majorOv'] else 'Regional Pleasantness default')
tab = {}
for p in places:
    tab.setdefault(rule_of(p), {'major key': 0, 'minor key': 0})[p['key']] += 1
S['key_rules'] = tab
S['n_minor'] = sum(p['key'] == 'minor key' for p in places)
below = [r['region'] for r in regions if r['pleasantness'] < M['median']]
S['regions_below_median'] = below
S['pleasantness_band'] = [float(pleas.min()), float(pleas.max())]
S['n_regions_within1_of_median'] = int((abs(pleas - M['median']) <= 1.0).sum())
S['pleasantness_values'] = {n_: float(v_) for n_, v_ in zip(names, pleas)}
STRONG = ['upbeat', 'happy', 'cheerful', 'uplifting', 'celebratory', 'lively', 'energetic', 'groovy', 'catchy']
SOFT = ['warm', 'relaxing', 'mellow', 'peaceful', 'serene']
minor_places = [p for p in places if p['key'] == 'minor key']
S['valence_conflict'] = dict(
    minor_total=len(minor_places),
    minor_strong_positive=sum(any(w in p['style'].lower() for w in STRONG) for p in minor_places),
    minor_soft_positive=sum(any(w in p['style'].lower() for w in SOFT) for p in minor_places),
    minor_any_positive=sum(any(w in p['style'].lower() for w in STRONG + SOFT) for p in minor_places),
    strong_words=STRONG, soft_words=SOFT,
    default_minor_examples=[f"{p['name']} ({p['region']})" for p in minor_places if not p['solemn']][:6])

# ---------------------------------------------------------------- RQ4: generated audio
A = list(csv.DictReader((ROOT / 'audio_analysis_results.csv').open(encoding='utf-8')))
req = np.array([float(r['requested_bpm']) for r in A]); det = np.array([float(r['detected_bpm']) for r in A])
ratio = det / req
corr = np.array([min((d / 2, d, d * 2), key=lambda c: abs(c - q)) for d, q in zip(det, req)])
meta = {r['clip_id']: r for r in csv.DictReader((ROOT / 'listener_stimulus_metadata.csv').open(encoding='utf-8'))}
score100 = np.array([float(meta[r['clip_id']]['activity_score_0_100']) for r in A])
want = [r['requested_mode'] for r in A]; hit = np.array([r['mode_match'] == 'True' for r in A])
rho_raw, p_raw = perm_p(req, det)
rho_c, p_c = perm_p(req, corr)
S['audio'] = dict(
    n=len(A), within10_raw=int((abs(det - req) / req <= .1).sum()), within10_corrected=int((abs(corr - req) / req <= .1).sum()),
    ratio_min=float(ratio.min()), ratio_max=float(ratio.max()), detected_min=float(det.min()), detected_max=float(det.max()),
    n_detected_115_161=int(((det >= 114) & (det <= 161)).sum()),
    rho_raw=rho_raw, p_raw=p_raw, rho_corrected=rho_c, p_corrected=p_c,
    median_corrected_err_pct=float(np.median(abs(corr - req) / req * 100)), mean_corrected_err_pct=float(np.mean(abs(corr - req) / req * 100)),
    n_not_explained_by_octave=int(((abs(corr - req) / req) > .1).sum()),
    mode_hits=int(hit.sum()), mode_ci=clopper_pearson(int(hit.sum()), len(A)),
    major_hits=int(sum(h for w, h in zip(want, hit) if w == 'major')), major_n=want.count('major'),
    minor_hits=int(sum(h for w, h in zip(want, hit) if w == 'minor')), minor_n=want.count('minor'),
    mean_conf_match=float(np.mean([float(r['key_detection_confidence']) for r, h in zip(A, hit) if h])),
    mean_conf_mismatch=float(np.mean([float(r['key_detection_confidence']) for r, h in zip(A, hit) if not h])))
S['audio']['major_ci'] = clopper_pearson(S['audio']['major_hits'], S['audio']['major_n'])
S['audio']['minor_ci'] = clopper_pearson(S['audio']['minor_hits'], S['audio']['minor_n'])
S['audio']['rows'] = [dict(clip=r['clip_id'], place=r['place'], score=float(s), req_bpm=float(q), det_bpm=float(d), ratio=float(d / q),
                           req_mode=r['requested_mode'], det_key=r['detected_key'], match=r['mode_match'] == 'True',
                           conf=float(r['key_detection_confidence'])) for r, s, q, d in zip(A, score100, req, det)]

ab = list(csv.DictReader((ROOT / 'prompt_ablation_results.csv').open(encoding='utf-8')))
S['ablation'] = [dict(clip=r['clip_id'], condition=r['condition'], track=int(r['track']), task=r['task_id'], req_bpm=float(r['requested_bpm']),
                      det_bpm=float(r['detected_bpm']), key=r['detected_key'], match=r['mode_match'] == 'True', conf=float(r['key_confidence']))
                 for r in ab]

# ---- unified re-measurement of every generated clip (paper_audio_reanalysis.py)
RE = json.loads((ROOT / 'paper_audio_reanalysis.json').read_text())
byfile = {r['file']: r for r in RE}
R1 = [byfile[f'clip{i:02d}.mp3'] for i in range(1, 11)]
R2 = [byfile[f'v2_clip{i:02d}.mp3'] for i in range(1, 11)]
v2csv = {r['clip_id']: r for r in csv.DictReader((ROOT / 'audio_analysis_results_v2.csv').open(encoding='utf-8'))}
req_mode = {r['clip_id']: r['requested_mode'] for r in A}
req_mode2 = {c: v2csv[c]['requested_mode'] for c in v2csv}
assert all(abs(float(v2csv[r['clip']]['detected_bpm']) - r['beat_track_bpm']) < .05 for r in R2), 'v2 CSV and re-measurement disagree'


def round_stats(rows, modes):
    rq = np.array([r['requested_bpm'] for r in rows], float); dt = np.array([r['beat_track_bpm'] for r in rows])
    hit = np.array([r['mode'] == modes[r['clip']] for r in rows])
    major = [h for r, h in zip(rows, hit) if modes[r['clip']] == 'major']; minor = [h for r, h in zip(rows, hit) if modes[r['clip']] == 'minor']
    rho, pv = perm_p(rq, dt)
    return dict(n=len(rows), mode_hits=int(hit.sum()), mode_ci=clopper_pearson(int(hit.sum()), len(rows)),
                major_hits=int(sum(major)), major_n=len(major), minor_hits=int(sum(minor)), minor_n=len(minor),
                within10=int((abs(dt - rq) / rq <= .1).sum()), rho=rho, p=pv, det_min=float(dt.min()), det_max=float(dt.max()),
                conf_match=float(np.mean([r['confidence'] for r, h in zip(rows, hit) if h])),
                conf_mismatch=float(np.mean([r['confidence'] for r, h in zip(rows, hit) if not h])),
                minor_clips=[r['clip'] for r in rows if modes[r['clip']] == 'minor'])


S['round1'] = round_stats(R1, req_mode)
S['round2'] = round_stats(R2, req_mode2)
d1 = np.array([r['beat_track_bpm'] for r in R1]); d2 = np.array([r['beat_track_bpm'] for r in R2])
S['replication'] = dict(rho_detected_tempo=float(stats.spearmanr(d1, d2).statistic), n_identical=int((abs(d1 - d2) < .05).sum()),
                        slow_clips_r1=[float(x) for x in d1[:3]], slow_clips_r2=[float(x) for x in d2[:3]],
                        mode_agreement=int(sum((a['mode'] == b['mode']) for a, b in zip(R1, R2))),
                        identical_values=sorted(set(float(x) for x in d1[abs(d1 - d2) < .05])))
S['round2']['rows'] = [dict(clip=r['clip'], place=meta[r['clip']]['place'], req_bpm=r['requested_bpm'], det_bpm=r['beat_track_bpm'],
                            req_mode=req_mode2[r['clip']], key=r['key'], match=r['mode'] == req_mode2[r['clip']], conf=r['confidence']) for r in R2]

tol = .05


def diag(rows):
    reqs_ = np.array([r['requested_bpm'] for r in rows], float)
    close = lambda c, q: abs(c - q) / q <= tol
    obs = sum(any(close(c, q) for c in r['top3']) for r, q in zip(rows, reqs_))
    null = np.array([sum(any(close(c, q) for c in r['top3']) for r, q in zip(rows, RNG.permutation(reqs_))) for _ in range(20000)])
    slow = [i for i, q in enumerate(reqs_) if q <= 68]; fast = [i for i, q in enumerate(reqs_) if q >= 75]
    top_hit = [any(close(c, reqs_[i]) for c in rows[i]['top3']) for i in range(len(rows))]
    dflt = np.array([r['tempo_default_prior'] for r in rows]); flat = np.array([r['tempo_flat_prior'] for r in rows])
    return dict(top3_hits=int(obs), null_mean=float(null.mean()), null_p95=float(np.percentile(null, 95)),
                p_perm=float((np.sum(null >= obs) + 1) / (len(null) + 1)),
                slow_hits=int(sum(top_hit[i] for i in slow)), slow_n=len(slow), fast_hits=int(sum(top_hit[i] for i in fast)), fast_n=len(fast),
                best_estimate_hits=int(sum(close(r['tempo_default_prior'], q) for r, q in zip(rows, reqs_))),
                default_rho=float(stats.spearmanr(reqs_, dflt).statistic), flat_rho=float(stats.spearmanr(reqs_, flat).statistic),
                default_range=[float(dflt.min()), float(dflt.max())], flat_range=[float(flat.min()), float(flat.max())],
                missed=[rows[i]['clip'] for i, h in enumerate(top_hit) if not h])


S['tempo_diag'] = dict(tol=tol, round1=diag(R1), round2=diag(R2), beat_track_start_bpm=120.0, librosa='1.0.0')
TD = R1  # figure 7 uses both rounds via R1/R2

# ---- Gangnam / Asan / Sejong: every generation in one place
pil = {(r['condition'], int(r['track'])): r for r in ab}
g = lambda f: byfile[f]
gang = [
    ('Round 1 wording, non-custom', 'original genre words', [g('clip09.mp3')]),
    ('Reworded, non-custom', 'original genre words', [g('clip09_retest_minor_fix.mp3')]),
    ('Explicit "A minor", custom', 'original genre words',
     [dict(key=r['detected_key'], mode=r['detected_mode'], confidence=float(r['key_confidence'])) for r in ab if r['condition'] == 'C_custom' and r['clip_id'] == 'clip09']),
    ('Round 2 prompt, custom', 'original genre words', [g('v2_clip09.mp3')]),
    ('Mode + tempo only (no genre words)', 'no genre words',
     [dict(key=r['detected_key'], mode=r['detected_mode'], confidence=float(r['key_confidence'])) for r in ab if r['condition'] == 'B_plain' and r['clip_id'] == 'clip09']),
    ('Genre swapped to dark synth-pop', 'swapped genre words',
     [g('clip09_genre_swap_test.mp3'), g('clip09_genre_swap_test_run2.mp3'), g('clip09_genre_swap_test_run3.mp3')]),
]
asan = [
    ('Round 1 wording, non-custom', 'original genre words', [g('clip10.mp3')]),
    ('Reworded, custom', 'original genre words', [g('clip10_asan_retest_custommode.mp3')]),
    ('Round 2 prompt, custom', 'original genre words', [g('v2_clip10.mp3')]),
    ('Genre swapped to dark techno', 'swapped genre words',
     [g('clip10_genre_swap_test_run1.mp3'), g('clip10_genre_swap_test_run2.mp3'), g('clip10_genre_swap_test_run3.mp3')]),
]
pack = lambda rows: [dict(condition=c, group=grp, tracks=[dict(key=t['key'], conf=float(t['confidence']), minor=t['mode'] == 'minor') for t in ts]) for c, grp, ts in rows]
S['gangnam'] = pack(gang); S['asan'] = pack(asan)
for k_, rows_ in (('gangnam', S['gangnam']), ('asan', S['asan'])):
    tally = {}
    for r in rows_:
        t = tally.setdefault(r['group'], [0, 0]); t[0] += sum(x['minor'] for x in r['tracks']); t[1] += len(r['tracks'])
    S[k_ + '_by_group'] = tally
S['sejong_pilot'] = [dict(key=r['detected_key'], conf=float(r['key_confidence']), bpm=float(r['detected_bpm'])) for r in ab if r['clip_id'] == 'clip07']
S['sejong'] = [dict(label=byfile[f]['description'], key=byfile[f]['key'], conf=byfile[f]['confidence'], bpm=byfile[f]['beat_track_bpm'])
               for f in ('clip07.mp3', 'v2_clip07.mp3', 'clip07_sejong_retest_custommode.mp3', 'clip07_sejong_institutional_fix.mp3', 'clip07_sejong_major_fix.mp3')]
S['genre_swap_pooled'] = dict(
    gangnam_minor=sum(x['minor'] for r in S['gangnam'] if r['group'] == 'swapped genre words' for x in r['tracks']),
    asan_minor=sum(x['minor'] for r in S['asan'] if r['group'] == 'swapped genre words' for x in r['tracks']))
root_hits = [(byfile[f]['key'].split()[0]) for f in ('clip09_genre_swap_test.mp3', 'clip09_genre_swap_test_run2.mp3', 'clip09_genre_swap_test_run3.mp3')]
S['root_note_gangnam_swap_detected'] = root_hits


# ---- Prompt-feature analysis: every minor-key request we have audio for, tagged by what the prompt contained
# shape: provider request shape; genre: whether the genre/style nouns were the original ones, none, or changed;
# wording: how the mode was phrased (bare theory term vs an early descriptive sentence with affect words).
MT = []
def mt(shape, genre, wording, ok, clip, src):
    MT.append(dict(shape=shape, genre=genre, wording=wording, ok=bool(ok), clip=clip, src=src))
for r in R1:
    if req_mode[r['clip']] == 'minor': mt('non-custom', 'original', 'bare', r['mode'] == 'minor', r['clip'], 'round 1')
for r in R2:
    if req_mode2[r['clip']] == 'minor': mt('custom', 'original', 'descriptive', r['mode'] == 'minor', r['clip'], 'round 2')
mt('non-custom', 'original', 'descriptive', byfile['clip09_retest_minor_fix.mp3']['mode'] == 'minor', 'clip09', 'reworded retest')
mt('custom', 'original', 'descriptive', byfile['clip10_asan_retest_custommode.mp3']['mode'] == 'minor', 'clip10', 'reworded retest')
mt('custom', 'original', 'descriptive', byfile['clip07_sejong_retest_custommode.mp3']['mode'] == 'minor', 'clip07', 'reworded retest')
mt('custom', 'changed', 'descriptive', byfile['clip07_sejong_institutional_fix.mp3']['mode'] == 'minor', 'clip07', 'category fix')
for f in ('clip09_genre_swap_test.mp3', 'clip09_genre_swap_test_run2.mp3', 'clip09_genre_swap_test_run3.mp3'):
    mt('custom', 'changed', 'descriptive', byfile[f]['mode'] == 'minor', 'clip09', 'genre swap')
for f in ('clip10_genre_swap_test_run1.mp3', 'clip10_genre_swap_test_run2.mp3', 'clip10_genre_swap_test_run3.mp3'):
    mt('custom', 'changed', 'descriptive', byfile[f]['mode'] == 'minor', 'clip10', 'genre swap')
for r in ab:
    if r['condition'] == 'B_plain': mt('non-custom', 'none', 'bare', r['detected_mode'] == 'minor', r['clip_id'], 'pilot')
    if r['condition'] == 'C_custom': mt('custom', 'original', 'bare', r['detected_mode'] == 'minor', r['clip_id'], 'pilot')


def tally(key, val):
    sub = [m for m in MT if m[key] == val]
    k_, n_ = sum(m['ok'] for m in sub), len(sub)
    return dict(k=k_, n=n_, ci=clopper_pearson(k_, n_))


def fisher(key, a, b):
    ta, tb = tally(key, a), tally(key, b)
    return float(stats.fisher_exact([[ta['k'], ta['n'] - ta['k']], [tb['k'], tb['n'] - tb['k']]])[1])


gang_sw = [m for m in MT if m['clip'] == 'clip09' and m['src'] == 'genre swap']
gang_rest = [m for m in MT if m['clip'] == 'clip09' and m['src'] != 'genre swap']
S['prompt_features'] = dict(
    n=len(MT), k=sum(m['ok'] for m in MT),
    shape={v: tally('shape', v) for v in ('non-custom', 'custom')}, genre={v: tally('genre', v) for v in ('original', 'none', 'changed')},
    wording={v: tally('wording', v) for v in ('bare', 'descriptive')},
    p_shape=fisher('shape', 'custom', 'non-custom'), p_wording=fisher('wording', 'descriptive', 'bare'), p_genre=fisher('genre', 'changed', 'original'),
    gangnam_swap=[sum(m['ok'] for m in gang_sw), len(gang_sw)], gangnam_rest=[sum(m['ok'] for m in gang_rest), len(gang_rest)],
    p_gangnam=float(stats.fisher_exact([[sum(m['ok'] for m in gang_sw), len(gang_sw) - sum(m['ok'] for m in gang_sw)],
                                        [sum(m['ok'] for m in gang_rest), len(gang_rest) - sum(m['ok'] for m in gang_rest)]])[1]))
# generate-and-check illustration: probability of at least one requested-mode track among m tracks, if tracks were independent
import math as _m
pf = S['prompt_features']
base_p = pf['genre']['original']['k'] / pf['genre']['original']['n']
S['gen_check'] = dict(p_original=base_p, p_pooled=pf['k'] / pf['n'],
                      at_least_one_of_2=1 - (1 - base_p) ** 2,
                      tracks_for_90=int(_m.ceil(_m.log(.1) / _m.log(1 - base_p))),
                      tracks_for_90_pooled=int(_m.ceil(_m.log(.1) / _m.log(1 - pf['k'] / pf['n']))),
                      credits_per_call=18)

# ================================================================ FIGURES
# ---- Fig 1: the chain
fig, ax = plt.subplots(figsize=(7.4, 3.3)); ax.axis('off'); ax.set_xlim(0, 100); ax.set_ylim(0, 46)
boxes = [
    ('Official\nregional\nstatistics', '17 regions,\n9 inputs', 'RQ1', GREEN),
    ('Activity Proxy\n+ Visitor\nPleasantness', 'weights are\nhypotheses', 'RQ1', GREEN),
    ('Landmark\nscore', '75 places,\nauthored offsets', 'RQ2', GREEN),
    ('Musical\nspecification', 'BPM, pitch,\nmode, style', 'RQ3', GREEN),
    ('Generated\naudio (Suno)', '10 clips\nmeasured', 'RQ4', ORANGE),
    ('Listener\nperception', 'no data yet', 'RQ6', GREY),
    ('Real-place\nperception', 'no data yet', 'RQ7', GREY),
]
bw, gap = 12.6, 1.6
xs = [bw / 2 + 1 + i * (bw + gap) for i in range(len(boxes))]
for i, (t, sub, rq, col) in enumerate(boxes):
    ax.add_patch(plt.Rectangle((xs[i] - bw / 2, 17), bw, 17, fc='white', ec=col, lw=1.8))
    ax.text(xs[i], 28.3, t, ha='center', va='center', fontsize=6.0, color=INK, fontweight='bold', linespacing=1.15)
    ax.text(xs[i], 20.6, sub, ha='center', va='center', fontsize=5.0, color=MUTED, linespacing=1.1)
    ax.text(xs[i], 36.5, rq, ha='center', fontsize=7, color=col, fontweight='bold')
    if i < len(boxes) - 1:
        ax.annotate('', xy=(xs[i + 1] - bw / 2 + .1, 25.5), xytext=(xs[i] + bw / 2 - .1, 25.5), arrowprops=dict(arrowstyle='-|>', color=INK, lw=.9, shrinkA=0, shrinkB=0, mutation_scale=7))
ax.add_patch(plt.Rectangle((xs[3] - bw / 2 - 6, 2), bw + 12, 9.5, fc='white', ec=ORANGE, lw=1.6, ls='--'))
ax.text(xs[3], 6.8, 'RQ5  Gemini style prediction\n(hand-simulated, not live)', ha='center', va='center', fontsize=4.9, color=INK)
ax.annotate('', xy=(xs[3], 17), xytext=(xs[3], 11.5), arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=.9, ls='--', mutation_scale=7))
ax.add_patch(plt.Rectangle((xs[1] - bw / 2 - 6, 2), bw + 12, 9.5, fc='white', ec=GREY, lw=1.6))
ax.text(xs[1], 6.8, 'RQ8  Map interface, keyboard\nand audio cues (no user test)', ha='center', va='center', fontsize=4.9, color=INK)
ax.annotate('', xy=(xs[1], 17), xytext=(xs[1], 11.5), arrowprops=dict(arrowstyle='<|-', color=GREY, lw=.9, mutation_scale=7))
for lab, col, x in (('computed from project data', GREEN, 2), ('measured audio or hand-simulated estimate', ORANGE, 33), ('no data collected yet', GREY, 72)):
    ax.add_patch(plt.Rectangle((x, 41.2), 2.2, 3, fc='white', ec=col, lw=1.6))
    ax.text(x + 3.2, 42.7, lab, fontsize=5.8, va='center', color=INK)
save(fig, 'fig1_chain.png')

# ---- Fig 2: maps
gtxt = (ROOT.parent / 'geojson.js').read_text(encoding='utf-8')
gj = json.loads(gtxt[gtxt.index('{'):gtxt.rindex('}') + 1])
alias = {'Gangwon-do': 'Gangwon', 'Gangwon': 'Gangwon'}


def rings(geom):
    if geom['type'] == 'Polygon':
        return [geom['coordinates'][0]]
    return [poly[0] for poly in geom['coordinates']]


fig, axes = plt.subplots(1, 2, figsize=(7.4, 4.3))
by_name = {n: (a, p) for n, a, p in zip(names, act, pleas)}
for ax, which, cmap, label, vmin, vmax in ((axes[0], 0, 'Blues', 'Activity Proxy (0–100)', act.min(), act.max()),
                                           (axes[1], 1, 'Oranges', 'Visitor Pleasantness (0–100)', pleas.min(), pleas.max())):
    cm = plt.get_cmap(cmap); patches, cols, cents = [], [], []
    for f in gj['features']:
        nm = alias.get(f['properties']['name_eng'], f['properties']['name_eng'])
        if nm not in by_name:
            continue
        v = by_name[nm][which]
        for ring in rings(f['geometry']):
            patches.append(MplPolygon(np.array(ring), closed=True)); cols.append(cm(.12 + .88 * (v - vmin) / (vmax - vmin)))
        biggest = max(rings(f['geometry']), key=len)
        cents.append((nm, np.mean(np.array(biggest), axis=0)))
    ax.add_collection(PatchCollection(patches, facecolors=cols, edgecolors='white', linewidths=.6))
    shift = {'GG': (.55, .12), 'ICN': (-.42, -.1), 'BSN': (.12, -.28), 'SEL': (0, 0), 'DJN': (.08, -.08), 'SEJ': (-.12, .05)}
    for nm, c in cents:
        dx, dy = shift.get(ABBR[nm], (0, 0))
        dark = (by_name[nm][which] - vmin) / (vmax - vmin) > .62 and (dx, dy) == (0, 0)
        ax.text(c[0] + dx, c[1] + dy, ABBR[nm], fontsize=5.2, ha='center', va='center', color='white' if dark else INK)
    ax.set_xlim(125.0, 130.0); ax.set_ylim(33.0, 38.7); ax.set_aspect(1.22); ax.axis('off')
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin, vmax)); sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, orientation='horizontal', fraction=.04, pad=.02, shrink=.8); cb.set_label(label, fontsize=7); cb.ax.tick_params(labelsize=6.5)
axes[0].set_title('Activity Proxy', fontsize=9); axes[1].set_title('Visitor Pleasantness composite', fontsize=9)
panel(axes[0], 'a'); panel(axes[1], 'b')
save(fig, 'fig2_maps.png')

# ---- Fig 3: sensitivity
order = np.argsort(base_rank)
fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.9), gridspec_kw={'width_ratios': [1.25, 1]})
ax = axes[0]
for yi, i in enumerate(order):
    ax.plot([rank_lo[i], rank_hi[i]], [yi, yi], color=BLUE, lw=3, alpha=.45, solid_capstyle='round')
    ax.plot(base_rank[i], yi, 'o', color=BLUE, ms=4.5, mec='white', mew=1)
ax.set_yticks(range(len(order))); ax.set_yticklabels([names[i] for i in order], fontsize=6.8); ax.invert_yaxis()
ax.set_xlabel('Rank by Activity Proxy (1 = most active)'); ax.set_xlim(.3, 17.7); ax.set_xticks(range(1, 18, 2)); ax.grid(axis='x', color=GRID)
ax.set_title('Rank of each region under perturbed weights'); panel(ax, 'a')
ax = axes[1]
ax.hist(rho_glob, bins=40, color=ORANGE, alpha=.55, label='Any weights')
ax.hist(rho_loc, bins=40, color=BLUE, alpha=.7, label='Near the stated weights')
ax.axvline(.9, color=INK, lw=.8, ls='--')
ax.set_xlabel('Spearman ρ with the stated-weight ranking'); ax.set_ylabel('Weight draws (of 10,000)')
ax.legend(frameon=False, fontsize=6.3, loc='upper left'); ax.text(.905, ax.get_ylim()[1] * .55, '\u03c1 = 0.9', fontsize=6, rotation=90, va='center'); ax.set_title('Agreement with the stated-weight ranking'); panel(ax, 'b')
fig.tight_layout(); save(fig, 'fig3_sensitivity.png')

# ---- Fig 4: model circumplex analogue (region-level pleasantness vs place-level activity), with marginals
fig = plt.figure(figsize=(7.0, 5.0))
gs = fig.add_gridspec(2, 2, width_ratios=[4, 1], height_ratios=[1, 4], hspace=.05, wspace=.05)
ax = fig.add_subplot(gs[1, 0]); axt = fig.add_subplot(gs[0, 0], sharex=ax); axr = fig.add_subplot(gs[1, 1], sharey=ax)
px = np.array([p['pleas'] if 'pleas' in p else next(r['pleasantness'] for r in regions if r['region'] == p['region']) for p in places])
py = sc * 100
for keyname, col, mk in (('major key', BLUE, 'o'), ('minor key', ORANGE, '^')):
    sel = np.array([p['key'] == keyname for p in places])
    ax.scatter(px[sel], py[sel], s=26, color=col, marker=mk, alpha=.85, edgecolor='white', linewidth=.5,
               label=f"{keyname.split()[0].capitalize()} requested (n={sel.sum()})", zorder=3)
    axt.hist(px[sel], bins=np.linspace(pleas.min() - .1, pleas.max() + .1, 18), color=col, alpha=.45)
    axr.hist(py[sel], bins=np.linspace(0, 90, 19), orientation='horizontal', color=col, alpha=.45)
ax.scatter(pleas, act, s=60, facecolor='none', edgecolor=INK, linewidth=1.1, label='Region value (17)', zorder=4)
ax.axvline(M['median'], color=GREY, ls='--', lw=1); ax.text(M['median'] + .03, 91, 'median of 17 regions', fontsize=6.2, color=MUTED)
ax.set_xlabel('Visitor Pleasantness composite of the place’s region (0–100)'); ax.set_ylabel('Landmark Activity score (0–100)')
ax.set_ylim(-3, 95); ax.legend(frameon=False, fontsize=6.6, loc='upper right'); ax.grid(color=GRID, lw=.6)
for a in (axt, axr):
    a.axis('off')
fig.suptitle('', y=.92)
save(fig, 'fig5_model_space.png')

# ---- Fig 5: key rule decomposition per region (stacked 100% bars)
cats = [('Solemn override (minor)', '#26215C'), ('Traditional/nature override (major)', BLUE), ('Regional default: major', '#97C459'), ('Regional default: minor', ORANGE)]
cls = lambda p: 0 if p['solemn'] else (1 if p['majorOv'] else (2 if p['key'] == 'major key' else 3))
reg_order = [n for n in np.array(names)[np.argsort(-pleas)]]
fig, ax = plt.subplots(figsize=(7.2, 4.6))
shares = np.zeros((len(reg_order), 4))
for p in places:
    shares[reg_order.index(p['region']), cls(p)] += 1
tot = shares.sum(1, keepdims=True); shares_p = shares / tot * 100
left = np.zeros(len(reg_order))
for j, (lab, col) in enumerate(cats):
    ax.barh(range(len(reg_order)), shares_p[:, j], left=left, color=col, label=lab, edgecolor='white', linewidth=1.2, height=.72)
    left += shares_p[:, j]
for i in range(len(reg_order)):
    ax.text(101, i, f'n={int(tot[i, 0])}', fontsize=6.2, va='center', color=MUTED)
ax.set_yticks(range(len(reg_order))); ax.set_yticklabels([f"{n} ({pleas[names.index(n)]:.1f})" for n in reg_order], fontsize=6.8); ax.invert_yaxis()
ax.set_xlim(0, 108); ax.set_xticks(range(0, 101, 20)); ax.set_xticklabels([f'{v}%' for v in range(0, 101, 20)])
ax.set_xlabel('Share of the region’s landmarks by the rule that decides major/minor'); ax.spines['left'].set_visible(False)
ax.legend(frameon=False, fontsize=6.4, ncol=2, loc='upper center', bbox_to_anchor=(.45, -.1))
save(fig, 'fig6_key_rules.png')

# ---- Fig 6: audio fidelity, both rounds
fig = plt.figure(figsize=(7.4, 3.9))
gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.25], wspace=.28)
ax = fig.add_subplot(gs[0, 0])
xs_ = np.array([35, 145])
ax.plot(xs_, xs_, color=INK, lw=1, label='Requested (1\u00d7)'); ax.plot(xs_, xs_ * 2, color=GREY, lw=.9, ls='--', label='2\u00d7'); ax.plot(xs_, xs_ / 2, color=GREY, lw=.9, ls=':', label='\u00bd\u00d7')
r1 = np.array([r['beat_track_bpm'] for r in R1]); r2 = np.array([r['beat_track_bpm'] for r in R2]); rq_ = np.array([r['requested_bpm'] for r in R1], float)
def _shift(d, q): return min((d / 2, d, d * 2), key=lambda c: abs(c - q))
for dd, col in ((r1, BLUE), (r2, ORANGE)):
    for q_, d_ in zip(rq_, dd):
        c_ = _shift(d_, q_)
        if abs(c_ - d_) > 1e-9:
            ax.annotate('', xy=(q_, c_), xytext=(q_, d_), arrowprops=dict(arrowstyle='-|>', color=col, lw=.7, alpha=.45, mutation_scale=6), zorder=2)
            ax.scatter(q_, c_, s=14, marker='D', facecolor='white', edgecolor=col, linewidth=.9, zorder=3)
ax.scatter([], [], s=14, marker='D', facecolor='white', edgecolor=GREY, linewidth=.9, label='Half/double-tempo equivalent')
ax.scatter(rq_, r1, s=34, color=BLUE, zorder=3, label='Round 1')
ax.scatter(rq_, r2, s=34, facecolor='white', edgecolor=ORANGE, linewidth=1.6, zorder=4, label='Round 2')
ax.set_xlim(35, 145); ax.set_ylim(35, 170); ax.grid(color=GRID, lw=.6)
ax.set_xlabel('Tempo requested in the prompt (BPM)'); ax.set_ylabel('Tempo measured in the audio (BPM)')
ax.legend(frameon=False, fontsize=5.8, loc='upper center', bbox_to_anchor=(.5, -.2), ncol=3, columnspacing=.8, handletextpad=.3); ax.set_title('Tempo'); panel(ax, 'a')
ax = fig.add_subplot(gs[0, 1])
for row, (rows_, modes_, lab) in enumerate(((R1, req_mode, 'Round 1'), (R2, req_mode2, 'Round 2'))):
    for col, r in enumerate(rows_):
        ok = r['mode'] == modes_[r['clip']]
        ax.add_patch(plt.Rectangle((col - .45, 1 - row - .45), .9, .9, fc=BLUE if ok else ORANGE, ec='white', alpha=.9 if ok else .95))
        ax.text(col, 1 - row + .12, r['key'].replace(' major', '\nmaj').replace(' minor', '\nmin'), ha='center', va='center', fontsize=5.4, color='white', linespacing=1.0)
        ax.text(col, 1 - row - .3, f"{r['confidence']:.2f}", ha='center', va='center', fontsize=4.8, color='white')
for col, r in enumerate(R1):
    ax.text(col, 1.62, f"{col + 1:02d}", ha='center', fontsize=6, color=MUTED)
    ax.text(col, 1.95, 'M' if req_mode[r['clip']] == 'major' else 'm', ha='center', fontsize=6.5, color=INK, fontweight='bold')
    ax.text(col, 2.0 - .02, '', fontsize=1)
ax.text(-.7, 1.95, 'asked', ha='right', fontsize=5.8, color=MUTED); ax.text(-.7, 1.62, 'clip', ha='right', fontsize=5.8, color=MUTED)
ax.set_xlim(-.6, 9.6); ax.set_ylim(-.6, 2.25); ax.set_yticks([1, 0]); ax.set_yticklabels(['Round 1', 'Round 2'], fontsize=6.8)
ax.set_xticks([]); [ax.spines[k].set_visible(False) for k in ('left', 'bottom')]; ax.tick_params(length=0)
ax.set_title('Major/minor mode', pad=12); panel(ax, 'b')
ax.text(4.5, -.95, 'M = major requested, m = minor requested. Blue: requested mode detected; orange: other mode. Number = key-fit score.',
        ha='center', fontsize=5.2, color=MUTED, wrap=True)
save(fig, 'fig7_audio_fidelity.png')

# ---- Fig 7: tempo-detector diagnostic, both rounds
fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.9), sharey=True)
for ax, rows_, ttl, lt in ((axes[0], R1, 'Round 1', 'a'), (axes[1], R2, 'Round 2', 'b')):
    for yi, t in enumerate(rows_):
        ax.plot([t['requested_bpm']] * 2, [yi - .38, yi + .38], color=INK, lw=2.2, zorder=3)
        for rank, c in enumerate(t['top3']):
            ax.scatter(c, yi, s=[46, 26, 16][rank], color=BLUE, alpha=[1, .75, .5][rank], zorder=4, edgecolor='white', linewidth=.4)
        ax.scatter(t['tempo_default_prior'], yi, s=60, marker='x', color=ORANGE, zorder=5, linewidth=1.3)
    ax.set_xscale('log'); ax.set_xlim(35, 330); ax.set_xticks([40, 60, 80, 100, 150, 200, 300]); ax.set_xticklabels(['40', '60', '80', '100', '150', '200', '300'], fontsize=6.5)
    ax.set_xlabel('Tempo (BPM, log scale)'); ax.grid(axis='x', color=GRID, lw=.6); ax.set_title(ttl); panel(ax, lt)
axes[0].set_yticks(range(10)); axes[0].set_yticklabels([f"{t['clip'][-2:]}  {meta[t['clip']]['place']}" for t in R1], fontsize=6.3); axes[0].invert_yaxis()
fig.legend(handles=[Line2D([0], [0], color=INK, lw=2.2, label='Tempo requested'),
                    Line2D([0], [0], marker='o', color='w', markerfacecolor=BLUE, markersize=7, label='Three strongest autocorrelation peaks (larger = stronger)'),
                    Line2D([0], [0], marker='x', color=ORANGE, lw=0, markersize=7, label='librosa single-value estimate (default prior)')],
           frameon=False, fontsize=6.3, loc='lower center', ncol=1, bbox_to_anchor=(.55, -.09))
fig.tight_layout(); save(fig, 'fig8_tempo_diagnostic.png')

# ---- Fig 8: popularity vs place score
if len(pop_x) > 5:
    fig, ax = plt.subplots(figsize=(5.6, 3.9))
    ax.scatter(pop_x, pop_y, s=24, color=BLUE, alpha=.8, edgecolor='white', linewidth=.5, zorder=3)
    ax.set_xlabel('Wikipedia readership index (0–100, log-scaled, English, 12 months)'); ax.set_ylabel('Landmark Activity score (0–100)')
    ax.grid(color=GRID, lw=.6)
    ax.text(.02, .96, f"Spearman ρ = {S['popularity']['rho']:.2f}, permutation p = {S['popularity']['p_perm']:.3f}, n = {len(pop_x)}",
            transform=ax.transAxes, fontsize=7, va='top', color=INK)
    save(fig, 'fig4_popularity.png')


# ---- Fig 9: every generation for the two failing minor-key clips
fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.5), gridspec_kw={'width_ratios': [1, 1], 'wspace': .85})
grp_col = {'original genre words': GREY, 'no genre words': '#BA7517', 'swapped genre words': GREEN}
for ax, rows_, ttl, lt in ((axes[0], S['gangnam'], 'Gangnam', 'a'), (axes[1], S['asan'], 'Asan plant', 'b')):
    ylab = []
    for yi, r in enumerate(rows_):
        for j, t in enumerate(r['tracks']):
            ax.scatter(t['conf'], yi + (j - (len(r['tracks']) - 1) / 2) * .16, s=46, marker='^' if t['minor'] else 'o',
                       color=BLUE if t['minor'] else ORANGE, edgecolor=grp_col[r['group']], linewidth=1.6, zorder=3)
        ylab.append(r['condition'])
    ax.set_yticks(range(len(rows_))); ax.set_yticklabels(ylab, fontsize=5.9); ax.invert_yaxis(); ax.set_xlim(.5, 1.0); ax.grid(axis='x', color=GRID, lw=.6)
    ax.set_xlabel('Key-fit score'); ax.set_title(ttl); panel(ax, lt)
axes[1].yaxis.tick_right()
fig.legend(handles=[Line2D([0], [0], marker='^', color='w', markerfacecolor=BLUE, markeredgecolor=INK, markersize=7, label='Minor detected (requested)'),
                    Line2D([0], [0], marker='o', color='w', markerfacecolor=ORANGE, markeredgecolor=INK, markersize=7, label='Major detected'),
                    Line2D([0], [0], marker='s', color='w', markerfacecolor='white', markeredgecolor=GREY, markeredgewidth=1.6, markersize=7, label='Outline: original genre words'),
                    Line2D([0], [0], marker='s', color='w', markerfacecolor='white', markeredgecolor='#BA7517', markeredgewidth=1.6, markersize=7, label='no genre words'),
                    Line2D([0], [0], marker='s', color='w', markerfacecolor='white', markeredgecolor=GREEN, markeredgewidth=1.6, markersize=7, label='swapped genre words')],
           frameon=False, fontsize=6, loc='lower center', ncol=3, bbox_to_anchor=(.5, -.1))
fig.tight_layout(); save(fig, 'fig9_genre_words.png')

# ---- Fig: prompt features (success rate of minor requests by what the prompt contained)
fig, ax = plt.subplots(figsize=(7.0, 3.6))
rows_ = [('Request shape', 'non-custom', pf['shape']['non-custom']), ('', 'custom', pf['shape']['custom']),
         ('Mode wording', 'bare term ("minor key", "in A minor")', pf['wording']['bare']), ('', 'early descriptive sentence', pf['wording']['descriptive']),
         ('Genre words', 'original', pf['genre']['original']), ('', 'none', pf['genre']['none']), ('', 'changed', pf['genre']['changed'])]
for yi, (grp, lab, t) in enumerate(rows_):
    ax.plot([100 * t['ci'][0], 100 * t['ci'][1]], [yi, yi], color=GREY, lw=2, alpha=.7, solid_capstyle='round')
    ax.scatter(100 * t['k'] / t['n'], yi, s=60, color=BLUE, zorder=3, edgecolor='white')
    ax.text(103, yi, f"{t['k']}/{t['n']}", va='center', fontsize=7, color=MUTED)
ax.set_yticks(range(len(rows_))); ax.set_yticklabels([f"{g_ + ': ' if g_ else ''}{l_}" for g_, l_, _ in rows_], fontsize=6.8); ax.invert_yaxis()
ax.set_xlim(-2, 112); ax.set_xticks(range(0, 101, 20)); ax.set_xlabel('Minor mode obtained (% of minor-key requests, with 95% interval)'); ax.grid(axis='x', color=GRID)
for y_ in (1.5, 3.5): ax.axhline(y_, color='#c3c2b7', lw=.6)
save(fig, 'fig_prompt_features.png')

# ---- Fig: real Spearman rank-vs-rank plots (diagonal = perfect agreement; d = vertical distance to the diagonal)
def rankplot(ax, xs, ys, title, xl, yl, letter, labels=None):
    rx, ry = stats.rankdata(xs), stats.rankdata(ys)
    n_ = len(xs); rho_ = float(stats.spearmanr(xs, ys).statistic); sd = float(((rx - ry) ** 2).sum())
    ax.plot([.5, n_ + .5], [.5, n_ + .5], color=INK, lw=1, ls='--')
    m_ = (n_ + 1) / 2; xx = np.array([.5, n_ + .5])
    ax.plot(xx, m_ + rho_ * (xx - m_), color=ORANGE, lw=1.6, label='Average trend (slope = \u03c1)')
    for a_, b_ in zip(rx, ry): ax.plot([a_, a_], [a_, b_], color=GREY, lw=.5, alpha=.5)
    ax.scatter(rx, ry, s=26 if n_ > 20 else 40, color=BLUE, edgecolor='white', linewidth=.5, zorder=3)
    if labels:
        for a_, b_, l_ in zip(rx, ry, labels): ax.annotate(l_, (a_, b_), xytext=(4, 3), textcoords='offset points', fontsize=6, color=MUTED)
    ax.set_xlim(.5, n_ + .5); ax.set_ylim(.5, n_ + .5); ax.set_aspect('equal'); ax.grid(color=GRID, lw=.5)
    ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_title(title); panel(ax, letter)
    ax.text(.04, .96, f"\u03c1 = {rho_:.2f}\n\u03a3d\u00b2 = {sd:.0f}", transform=ax.transAxes, va='top', fontsize=7, color=INK)
    return rho_, sd

fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.9))
ids_ = [r['clip'][-2:] for r in R1]
S['rankplots'] = {}
S['rankplots']['tempo_r1'] = rankplot(axes[0], rq_, r1, 'Round 1 tempo', 'Rank of requested tempo', 'Rank of measured tempo', 'a', ids_)
S['rankplots']['tempo_r2'] = rankplot(axes[1], rq_, r2, 'Round 2 tempo', 'Rank of requested tempo', 'Rank of measured tempo', 'b', ids_)
S['rankplots']['popularity'] = rankplot(axes[2], np.array(pop_x), np.array(pop_y), 'Landmarks', 'Rank of readership index', 'Rank of Activity score', 'c')
fig.legend(handles=[Line2D([0], [0], color=INK, lw=1, ls='--', label='Perfect agreement (\u03c1 = 1)'),
                    Line2D([0], [0], color=ORANGE, lw=1.6, label='Average trend of the points (slope = \u03c1)')],
           frameon=False, fontsize=6.5, loc='lower center', ncol=2, bbox_to_anchor=(.5, -.06))
fig.tight_layout(); save(fig, 'fig_rank_agreement.png')

(OUT / 'stats.json').write_text(json.dumps(S, indent=1, default=float))
print('Wrote', OUT / 'stats.json', 'and', len(list(FIG.glob('*.png'))), 'figures')
print(json.dumps({k: S[k] for k in ('place_variance', 'popularity', 'key_rules', 'valence_conflict', 'tempo_diag', 'mc_local', 'mc_global', 'reference_check')}, indent=1, default=float))
