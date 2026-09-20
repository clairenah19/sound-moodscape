#!/usr/bin/env python3
"""Analyze real exported sessions. Clip-level Spearman permutation test; no invented observations."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ATTRS = ['pleasant', 'chaotic', 'vibrant', 'uneventful', 'calm', 'annoying', 'eventful', 'monotonous']
ROOT = Path(__file__).resolve().parent

def iso_eventfulness(row):
    r = {}
    for key in ATTRS:
        value = float(row[key + '_1_5'])
        if not math.isfinite(value) or value not in range(1, 6):
            raise ValueError('All eight ratings must be integers from 1 to 5')
        r[key] = value
    return ((r['eventful'] - r['uneventful']) + math.sqrt(.5) *
            (r['chaotic'] - r['calm'] + r['vibrant'] - r['monotonous'])) / (4 + math.sqrt(32))

def validated_sessions(rows, metadata, config):
    clips = {c['id']: c for c in config['clips']}
    targets = {r['clip_id']: r for r in metadata}
    if set(clips) != set(targets) or len(targets) != len(metadata):
        raise ValueError('Stimulus metadata must match the unique published clips')
    sessions, excluded = {}, []
    seen = {}
    for row in rows:
        pid = row['participant_id']
        cid = row['clip_id']
        if not pid or cid not in clips:
            raise ValueError('Unknown clip or missing participant ID')
        key = (pid, cid)
        if key in seen:
            if seen[key] == row:
                continue  # Repeated copies of the exact same download are deduplicated.
            raise ValueError(f'Conflicting duplicate response for {pid}/{cid}')
        seen[key] = row
        if row['stimulus_version'] != config['version'] or row['protocol_version'] != config['protocol_version']:
            raise ValueError('Do not mix protocol or stimulus versions')
        if row['clip_sha256'] != clips[cid]['sha256'] or not clips[cid]['sha256']:
            raise ValueError('Clip hash does not match the frozen stimulus manifest')
        if not row['consent_utc']:
            raise ValueError('Consent timestamp is required')
        heard = float(row['listened_seconds'])
        duration = float(row['clip_duration_seconds'])
        response = float(row['response_seconds'])
        if not all(math.isfinite(x) for x in (heard, duration, response)) or duration != clips[cid]['duration_seconds'] or heard < duration - .25 or response < duration - .25:
            raise ValueError('Incomplete clip playback or invalid timing')
        iso_eventfulness(row)
        sessions.setdefault(pid, {})[cid] = row
    complete = {}
    for pid, ratings in sessions.items():
        if set(ratings) != set(clips):
            excluded.append(pid)
        elif sorted(int(r['presentation_order']) for r in ratings.values()) != list(range(1,len(clips)+1)):
            raise ValueError('Invalid presentation order')
        else:
            complete[pid] = ratings
    return complete, excluded

def _minmax(v):
    import numpy as np
    return (v - v.min()) / (v.max() - v.min())

def pairwise_accuracy(scores, means):
    """Share of clip pairs whose rated order matches the generating-score order.
    Pairs with equal scores are skipped; tied ratings count 0.5. Chance is 0.5."""
    import numpy as np
    i, j = np.triu_indices(len(scores), 1)
    ds = np.sign(scores[i] - scores[j])
    keep = ds != 0
    dm = np.sign(means[i] - means[j])[keep]
    hit = np.where(dm == 0, .5, (dm == ds[keep]).astype(float))
    return float(hit.mean()), int(keep.sum())

def lins_ccc(x, y):
    """Lin's concordance correlation coefficient (population variances)."""
    import numpy as np
    return float(2 * np.mean((x - x.mean()) * (y - y.mean())) / (x.var() + y.var() + (x.mean() - y.mean()) ** 2))

def normalised_error(scores, means):
    """WAPE and MAE after min-max scaling both series to 0-1; scores are the 'actual' series.
    Depends on the scaling, so it is descriptive only."""
    import numpy as np
    a, p = _minmax(scores), _minmax(means)
    return float(np.abs(a - p).sum() / np.abs(a).sum()), float(np.abs(a - p).mean())

def icc_two_way(matrix):
    """ICC(2,1) and ICC(2,k), absolute agreement, participants (rows) as raters, clips (columns) as targets."""
    import numpy as np
    r, t = matrix.shape
    grand = matrix.mean()
    ms_targets = r * ((matrix.mean(axis=0) - grand) ** 2).sum() / (t - 1)
    ms_raters = t * ((matrix.mean(axis=1) - grand) ** 2).sum() / (r - 1)
    resid = matrix - matrix.mean(axis=0) - matrix.mean(axis=1, keepdims=True) + grand
    ms_error = (resid ** 2).sum() / ((t - 1) * (r - 1))
    icc1 = (ms_targets - ms_error) / (ms_targets + (r - 1) * ms_error + r * (ms_raters - ms_error) / t)
    icck = (ms_targets - ms_error) / (ms_targets + (ms_raters - ms_error) / t)
    return float(icc1), float(icck)

def kendalls_w(matrix):
    """Kendall's W across participants ranking the clips, with the tie correction."""
    import numpy as np
    from scipy.stats import rankdata
    m, n = matrix.shape
    ranks = np.array([rankdata(row) for row in matrix])
    s = ((ranks.sum(axis=0) - ranks.sum(axis=0).mean()) ** 2).sum()
    ties = sum(((c ** 3 - c).sum()) for row in matrix for c in [np.unique(row, return_counts=True)[1]])
    return float(12 * s / (m ** 2 * (n ** 3 - n) - m * ties))

def secondary_metrics(scores, means):
    acc, pairs = pairwise_accuracy(scores, means)
    wape, mae = normalised_error(scores, means)
    return dict(pairwise_accuracy=acc, pairs=pairs, ccc=lins_ccc(_minmax(scores), _minmax(means)), wape=wape, mae=mae)

def analyze(rows, metadata, config, permutations=49999, bootstrap=5000, seed=20260913):
    import numpy as np
    from scipy.stats import rankdata, spearmanr
    sessions, excluded = validated_sessions(rows, metadata, config)
    if len(sessions) < 15:
        return None, f'{len(sessions)} complete participants; minimum exploratory cohort is 15. {len(excluded)} incomplete sessions excluded.'
    ids = [c['id'] for c in config['clips']]
    targets = {r['clip_id']: r for r in metadata}
    scores = np.array([float(targets[c]['activity_score_0_100']) for c in ids])
    matrix = np.array([[iso_eventfulness(session[c]) for c in ids] for session in sessions.values()])
    means = matrix.mean(axis=0)
    if len(set(scores)) < 2 or len(set(means)) < 2:
        raise ValueError('Correlation undefined: constant stimulus scores or constant clip-mean ratings')
    rho = float(spearmanr(scores, means).statistic)
    rng = np.random.default_rng(seed)
    x = rankdata(scores); x -= x.mean(); x /= np.linalg.norm(x)
    y = rankdata(means); y -= y.mean(); y /= np.linalg.norm(y)
    extreme = sum(abs(float(np.dot(x, rng.permutation(y)))) >= abs(rho) - 1e-12 for _ in range(permutations))
    p = (extreme + 1) / (permutations + 1)
    boot, boot2, boot_means = [], [], []
    for _ in range(bootstrap):
        sample = matrix[rng.integers(0, len(matrix), len(matrix))].mean(axis=0)
        boot_means.append(sample)
        if len(set(sample)) > 1:
            boot.append(float(spearmanr(scores, sample).statistic))
            boot2.append(secondary_metrics(scores, sample))
    ci = np.quantile(boot, [.025, .975]).tolist() if boot else None
    clip_ci = np.quantile(np.array(boot_means), [.025, .975], axis=0).T.tolist() if boot_means else [None] * len(ids)
    # Secondary metrics use their own seeded stream so the primary numbers above are unchanged.
    sec = secondary_metrics(scores, means)
    for key in list(sec):
        if key != 'pairs':
            sec[key + '_ci'] = np.quantile([b[key] for b in boot2], [.025, .975]).tolist() if boot2 else None
    rng2 = np.random.default_rng(seed + 1)
    i, j = np.triu_indices(len(scores), 1)
    ds = np.sign(scores[i] - scores[j]); keep = ds != 0
    extreme = 0
    for _ in range(permutations):
        perm = rng2.permutation(means)
        dm = np.sign(perm[i] - perm[j])[keep]
        acc = np.where(dm == 0, .5, (dm == ds[keep]).astype(float)).mean()
        extreme += abs(acc - .5) >= abs(sec['pairwise_accuracy'] - .5) - 1e-12
    sec['pairwise_p_two_sided'] = (extreme + 1) / (permutations + 1)
    sec['icc2_1'], sec['icc2_k'] = icc_two_way(matrix)
    sec['kendalls_w'] = kendalls_w(matrix)
    return dict(participants=len(sessions), excluded_incomplete=len(excluded), clips=len(ids),
        rho=rho, p_two_sided=p, ci_participant_bootstrap=ci, valid_bootstraps=len(boot),
        permutations=permutations, seed=seed, secondary=sec,
        clip_means=[{'clip_id':c,'score':float(scores[i]),'mean_eventfulness':float(means[i]),'ci95':clip_ci[i]} for i,c in enumerate(ids)]), ''

def render_figure(result):
    """Self-contained SVG (no plotting dependency): generating score vs. mean rated Eventfulness per clip,
    with 95% participant-bootstrap intervals. Rank order is the tested claim, so no fitted line is drawn."""
    from xml.sax.saxutils import escape
    clips, sec = result['clip_means'], result['secondary']
    W, H, L, R, T, B = 720, 480, 78, 24, 56, 92
    lo = min(c['ci95'][0] if c['ci95'] else c['mean_eventfulness'] for c in clips)
    hi = max(c['ci95'][1] if c['ci95'] else c['mean_eventfulness'] for c in clips)
    pad = (hi - lo) * .08 or .05
    lo, hi = lo - pad, hi + pad
    X = lambda v: L + (W - L - R) * v / 100
    Y = lambda v: T + (H - T - B) * (1 - (v - lo) / (hi - lo))
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d" font-family="Helvetica, Arial, sans-serif">',
         '<title id="t">Generating activity score versus listener-rated Eventfulness for each clip</title>',
         f'<desc id="d">{len(clips)} clips. Spearman rho {result["rho"]:.2f}; pairwise ordering accuracy {sec["pairwise_accuracy"]:.2f} over {sec["pairs"]} pairs; {result["participants"]} participants. Error bars are 95% participant-bootstrap intervals.</desc>',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{L}" y="26" font-size="15" font-weight="bold" fill="#0b0b0b">Does the music\'s rated Eventfulness follow the model\'s activity score?</text>',
         f'<text x="{L}" y="44" font-size="12" fill="#52514e">Spearman \u03c1 = {result["rho"]:.2f} ({("p < 0.0001" if result["p_two_sided"] < .0001 else "p = %.4f" % result["p_two_sided"])}) \u00b7 pairwise ordering accuracy = {sec["pairwise_accuracy"]:.2f} (chance 0.50) \u00b7 n = {result["participants"]} participants</text>']
    step = (hi - lo) / 5
    for k in range(6):
        v = lo + k * step
        o.append(f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#e1e0d9"/><text x="{L - 8}" y="{Y(v) + 4:.1f}" font-size="11" text-anchor="end" fill="#52514e">{v:.2f}</text>')
    for v in range(0, 101, 20):
        o.append(f'<text x="{X(v):.1f}" y="{H - B + 18}" font-size="11" text-anchor="middle" fill="#52514e">{v}</text>')
    o.append(f'<line x1="{L}" x2="{W - R}" y1="{H - B}" y2="{H - B}" stroke="#c3c2b7"/>')
    if lo < 0 < hi:
        o.append(f'<line x1="{L}" x2="{W - R}" y1="{Y(0):.1f}" y2="{Y(0):.1f}" stroke="#898781" stroke-dasharray="4 3"/>')
    for c in clips:
        x, y = X(c['score']), Y(c['mean_eventfulness'])
        if c['ci95']:
            o.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{Y(c["ci95"][0]):.1f}" y2="{Y(c["ci95"][1]):.1f}" stroke="#2a78d6" stroke-width="2"/>')
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#2a78d6" stroke="#ffffff" stroke-width="2"><title>{escape(c["clip_id"])}: score {c["score"]:.1f}, mean {c["mean_eventfulness"]:.3f}</title></circle>')
        o.append(f'<text x="{x + 8:.1f}" y="{y - 8:.1f}" font-size="10" fill="#52514e">{escape(c["clip_id"])}</text>')
    o.append(f'<text x="{(L + W - R) / 2:.0f}" y="{H - B + 42}" font-size="12" text-anchor="middle" fill="#0b0b0b">Generating activity score (model, 0\u2013100)</text>')
    o.append(f'<text transform="translate(18 {(T + H - B) / 2:.0f}) rotate(-90)" font-size="12" text-anchor="middle" fill="#0b0b0b">Mean rated Eventfulness (adapted ISO index)</text>')
    o.append(f'<text x="{L}" y="{H - 14}" font-size="11" fill="#52514e">Error bars: 95% participant bootstrap, conditional on these ten clips. Tests the encoding of the modelled score, not real places.</text>')
    o.append('</svg>')
    return '\n'.join(o) + '\n'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('responses', nargs='*', type=Path)
    parser.add_argument('--manifest', type=Path, default=ROOT/'listener_stimuli.json')
    parser.add_argument('--metadata', type=Path, default=ROOT/'listener_stimulus_metadata.csv')
    parser.add_argument('--output', type=Path, default=ROOT/'listener_experiment_results.md')
    parser.add_argument('--figure', type=Path, default=ROOT/'listener_experiment_figure.svg')
    args = parser.parse_args()
    rows = []
    for file in args.responses:
        with file.open(newline='', encoding='utf-8-sig') as src:
            rows.extend(csv.DictReader(src))
    if not rows:
        print('0 rows found — no listener data collected yet. Results remain [PENDING].')
        return
    config = json.loads(args.manifest.read_text())
    if not config.get('ready'):
        parser.error('Stimulus manifest is not ready; do not analyze placeholder clips')
    with args.metadata.open(newline='') as src:
        metadata = list(csv.DictReader(src))
    try:
        result, pending = analyze(rows, metadata, config)
    except (ValueError, KeyError) as exc:
        parser.error(str(exc))
    if result is None:
        print('[PENDING] ' + pending)
        return
    evidence = '\n'.join(f'- `{p.name}`: SHA-256 `{hashlib.sha256(p.read_bytes()).hexdigest()}`' for p in args.responses)
    direction = 'Positive association' if result['rho'] > 0 else 'Non-positive association'
    decision = 'Meets the prespecified positive-direction and p < .05 criterion for these clips.' if result['rho'] > 0 and result['p_two_sided'] < .05 else 'Does not meet the prespecified positive-direction and p < .05 criterion.'
    text = '# Listener experiment results\n\n'
    text += f"{result['participants']} complete participants; {result['clips']} independently permuted clip units. {result['excluded_incomplete']} incomplete sessions excluded.\n\n"
    text += f"Spearman rho = {result['rho']:.4f}; two-sided Monte Carlo permutation p = {result['p_two_sided']:.5f} ({result['permutations']} permutations; seed {result['seed']}). {direction}. {decision}\n\n"
    text += f"Participant-bootstrap 95% interval, conditional on this fixed stimulus set: {result['ci_participant_bootstrap']} ({result['valid_bootstraps']} valid resamples).\n\n"
    text += 'This tests the musical encoding of modelled activity. It does not validate the model against real places, establish causation, or generalize to all music or all regions. Musical ratings use adapted soundscape descriptors, not in-situ ISO measurements.\n\n'
    sec = result['secondary']
    fmt = lambda k: f"{sec[k]:.3f} (95% CI {sec[k + '_ci'][0]:.3f} to {sec[k + '_ci'][1]:.3f})" if sec[k + '_ci'] else f"{sec[k]:.3f}"
    text += '## Secondary and descriptive agreement metrics\n\n'
    text += 'Prespecified secondary (amended 2026-09-20, before any data): pairwise ordering accuracy. Chance is 0.50. Intervals are participant bootstraps; the p value permutes clip labels (same seed scheme, seed+1).\n\n'
    text += f"- Pairwise ordering accuracy: {fmt('pairwise_accuracy')} over {sec['pairs']} clip pairs; two-sided permutation p = {sec['pairwise_p_two_sided']:.5f}.\n\n"
    text += 'Descriptive only, no pass/fail threshold. CCC, WAPE and MAE min-max scale both series to 0-1 first, so they depend on the observed ranges and must not be read as absolute errors.\n\n'
    text += f"- Lin's CCC (normalised): {fmt('ccc')}\n- WAPE (normalised, generating score as actual): {fmt('wape')}\n- MAE (normalised): {fmt('mae')}\n"
    text += f"- Rater consistency, participants as raters: ICC(2,1) = {sec['icc2_1']:.3f}; ICC(2,k) = {sec['icc2_k']:.3f}; Kendall's W = {sec['kendalls_w']:.3f}. These show whether listeners agree with each other, not whether they agree with the model.\n\n"
    text += f'![Generating score versus rated Eventfulness per clip; text summary in the table below]({args.figure.name})\n\n'
    text += '| Clip | Generating score | Mean rated Eventfulness |\n|---|---:|---:|\n'
    text += ''.join(f"| {r['clip_id']} | {r['score']:.2f} | {r['mean_eventfulness']:.4f} |\n" for r in result['clip_means'])
    text += '\n## Input provenance\n\n' + evidence + '\n'
    args.figure.write_text(render_figure(result))
    args.output.write_text(text)
    print(f'Wrote {args.output} and {args.figure}')

if __name__ == '__main__':
    main()
